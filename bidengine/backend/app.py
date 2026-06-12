"""
Run with:
    uvicorn app:app --reload --port 8000
http://localhost:8000/ 

Endpoints
---------
GET    /api/health
POST   /api/workspaces                       create a new RFP workspace
GET    /api/workspaces                        list all workspaces
GET    /api/workspaces/{id}                   full workspace detail
DELETE /api/workspaces/{id}                   delete a workspace
POST   /api/workspaces/{id}/upload            upload RFP file (PDF/DOCX/TXT), runs extraction
POST   /api/workspaces/{id}/analyze           run RAG match + checklist + scoring + draft
PUT    /api/workspaces/{id}/draft/{section_id} edit a drafted proposal section
GET    /api/workspaces/{id}/export            download proposal as .docx
GET    /api/capability-library                view the capability library
GET    /api/eval-criteria-taxonomy            view the evaluation criteria taxonomy
"""

import os
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import extraction
import rag
import scoring
import proposal
import analysis
import storage
import export as export_module
import json

BASE_DIR = os.path.dirname(__file__)
UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")
EXPORTS_DIR = os.path.join(BASE_DIR, "data", "exports")
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)

app = FastAPI(title="AI Bid & Proposal Response Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_capability_matcher = rag.CapabilityMatcher()
_win_model = scoring.WinProbabilityModel()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm_enrichment_available": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "model_train_accuracy_pct": _win_model.train_accuracy * 100,
        "model_base_win_rate_pct": _win_model.base_win_rate * 100,
    }


@app.get("/api/capability-library")
def capability_library():
    return _capability_matcher.library


@app.get("/api/eval-criteria-taxonomy")
def eval_criteria_taxonomy():
    with open(os.path.join(BASE_DIR, "data", "eval_criteria_taxonomy.json"), encoding="utf-8") as f:
        return json.load(f)

@app.post("/api/workspaces")
def create_workspace(payload: dict = Body(...)):
    name = payload.get("name", "").strip() or "Untitled RFP"
    record = storage.create_workspace(name)
    return record


@app.get("/api/workspaces")
def list_workspaces():
    return storage.list_workspaces()


@app.get("/api/workspaces/{workspace_id}")
def get_workspace(workspace_id: str):
    record = storage.get_workspace(workspace_id)
    if not record:
        raise HTTPException(404, "Workspace not found")
    return record


@app.delete("/api/workspaces/{workspace_id}")
def delete_workspace(workspace_id: str):
    if not storage.delete_workspace(workspace_id):
        raise HTTPException(404, "Workspace not found")
    return {"deleted": True}

@app.post("/api/workspaces/{workspace_id}/upload")
async def upload_rfp(workspace_id: str, file: UploadFile = File(...)):
    record = storage.get_workspace(workspace_id)
    if not record:
        raise HTTPException(404, "Workspace not found")

    if not file.filename.lower().endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(400, "Only PDF, DOCX, or TXT files are supported")

    dest_path = os.path.join(UPLOADS_DIR, f"{workspace_id}_{file.filename}")
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    try:
        result = extraction.extract(dest_path, use_llm=True)
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {e}")

    record["source_file"] = file.filename
    record["extraction"] = result.to_dict()
    record["extraction"]["full_text_preview"] = result.full_text[:2000]
    record["status"] = "extracted"

    record["checklist"] = None
    record["checklist_summary"] = None
    record["draft"] = None
    record["scoring_inputs"] = None
    record["scoring_result"] = None
    record["go_no_go"] = None
    storage.save_workspace(record)

    return record


@app.post("/api/workspaces/{workspace_id}/analyze")
def analyze_workspace(workspace_id: str, payload: dict = Body(default={})):
    record = storage.get_workspace(workspace_id)
    if not record:
        raise HTTPException(404, "Workspace not found")
    if not record.get("extraction"):
        raise HTTPException(400, "Upload and extract an RFP before analyzing")

    extraction_data = record["extraction"]
    competitor_count = int(payload.get("estimated_competitor_count", 5))
    past_relationship = bool(payload.get("past_relationship", False))
    use_llm = bool(payload.get("use_llm", True))

    checklist = rag.build_compliance_checklist(
        extraction_data.get("mandatory_requirements", []), _capability_matcher
    )
    summary = rag.checklist_summary(checklist)

    scoring_inputs = analysis.compute_scoring_inputs(
        extraction_data, summary, competitor_count, past_relationship
    )
    scoring_result = _win_model.predict(scoring_inputs)
    go_no_go = scoring.go_no_go_decision(
        win_probability_pct=scoring_result["win_probability_pct"],
        gap_count=summary["gap"],
        total_requirements=summary["total_requirements"],
        budget_alignment_score=scoring_inputs["budget_alignment_score"],
    )

    draft = proposal.generate_proposal_draft(
        extraction_data.get("qa_sections", []), _capability_matcher, use_llm=use_llm
    )

    record["checklist"] = checklist
    record["checklist_summary"] = summary
    record["scoring_inputs"] = scoring_inputs
    record["scoring_result"] = scoring_result
    record["go_no_go"] = go_no_go
    record["draft"] = draft
    record["status"] = "analyzed"
    storage.save_workspace(record)

    return record

@app.put("/api/workspaces/{workspace_id}/draft/{section_id}")
def update_draft_section(workspace_id: str, section_id: str, payload: dict = Body(...)):
    record = storage.get_workspace(workspace_id)
    if not record or not record.get("draft"):
        raise HTTPException(404, "Workspace or draft not found")

    new_text = payload.get("draft_response")
    new_status = payload.get("status", "approved")
    found = False
    for section in record["draft"]:
        if section["id"] == section_id:
            if new_text is not None:
                section["draft_response"] = new_text
            section["status"] = new_status
            found = True
            break

    if not found:
        raise HTTPException(404, "Section not found")

    storage.save_workspace(record)
    return record

@app.get("/api/workspaces/{workspace_id}/export")
def export_workspace(workspace_id: str):
    record = storage.get_workspace(workspace_id)
    if not record:
        raise HTTPException(404, "Workspace not found")
    if record["status"] != "analyzed":
        raise HTTPException(400, "Run analysis before exporting")

    safe_name = "".join(c for c in record["name"] if c.isalnum() or c in " _-").strip() or "proposal"
    out_path = os.path.join(EXPORTS_DIR, f"{workspace_id}_{safe_name}.docx")
    export_module.build_proposal_docx(record, out_path)
    return FileResponse(
        out_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{safe_name} - Proposal Draft.docx",
    )


FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
