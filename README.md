# AI-Powered Bid & Proposal Response Engine

A working prototype for **CUST Hackathon 2026** — Procurement, Sourcing &
Contract Management track.

Ingests an RFP/RFQ/Tender (PDF/DOCX), extracts mandatory requirements,
deadlines, budget and evaluation criteria, matches them against a
Company Capability Library via RAG, drafts a structured proposal
response, flags compliance gaps, and scores the opportunity's
win-probability with a GO / NO-GO recommendation.

---

## Quick start

```bash
cd backend
pip install -r requirements.txt --break-system-packages   # if needed
uvicorn app:app --reload --port 8000
```

Open **http://localhost:8000** in a browser. A demo workspace
("PITB ICMS - District Case Management") is already loaded with the
included sample RFP so you can explore the full pipeline immediately --
or click **New RFP workspace** and upload your own PDF/DOCX.

### Optional: enable LLM enrichment

Set `ANTHROPIC_API_KEY` before starting the server to turn on:
- LLM-based cleanup / labeling of extracted requirements
- LLM-polished proposal draft prose

```bash
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn app:app --reload --port 8000
```

Without a key, everything still works end-to-end using the
deterministic rule-based extraction, TF-IDF RAG matching, and
template-based drafting -- **the demo never breaks due to missing
connectivity**.

---

## Architecture

```
sample RFP (PDF/DOCX)
        |
        v
 extraction.py   --  regex/NER-lite: deadlines, budget, mandatory
        |             requirements, evaluation criteria, Q&A sections
        |             (+ optional Claude enrichment)
        v
   rag.py        --  TF-IDF retrieval over capability_library.json
        |             -> compliance checklist (pass / partial / gap)
        v
 analysis.py     --  derives win-probability model features
        |             (cert match %, requirement coverage,
        |              budget alignment, competitor count, ...)
        v
 scoring.py      --  logistic regression trained on historical_bids.csv
        |             (120 past bids) -> win probability + GO/NO-GO
        v
 proposal.py     --  drafts each Q&A section using matched evidence
        |             (+ optional Claude polishing)
        v
   export.py     --  assembles everything into a downloadable .docx
        |
        v
   app.py (FastAPI) + frontend/ (vanilla HTML/CSS/JS SPA)
```

### Data (backend/data/)
| File | Description |
|---|---|
| `capability_library.json` | 50 past-project records (sector, certs, contract value, client type) |
| `historical_bids.csv` | 120 rows x 18 cols of win/loss outcomes used to train the scoring model |
| `eval_criteria_taxonomy.json` | 15 common RFP evaluation criteria by sector |
| `generate_data.py` / `generate_sample_rfp.py` | regenerate the sample datasets / sample RFP |

### Sample RFP
`sample_rfps/PITB_ICMS_RFP_2026.docx` -- a realistic IT-services tender
(17 mandatory requirements, 8 weighted evaluation criteria, 5 Q&A
sections, deadlines and budget figures) used to demo the full pipeline.

---

## Mapping to deliverables

- **Working prototype accepting a sample RFP -> structured draft response** -- `proposal.py` + Draft tab
- **Separate workspace per RFP/RFQ/Tender** -- `storage.py` (one JSON record per workspace)
- **Auto-generated compliance checklist with pass/fail mapping** -- `rag.py` -> Checklist tab
- **Win-probability dashboard** -- `scoring.py` -> Dashboard tab, with explainable per-feature contributions
- **GO / NO-GO decision** -- `scoring.go_no_go_decision()`
- **Review/edit/approve UI before export** -- editable draft textareas + "Mark approved" + .docx export

## Mapping to rubric

- **Technical implementation** -- full pipeline runs end-to-end offline (no external dependency required for the core demo); LLM enrichment is additive, not load-bearing.
- **Validation & reliability** -- the scoring model reports its own training accuracy (87.5%) and base win rate (63.3%) directly in the UI; the compliance checklist shows similarity scores for every match.
- **Innovation** -- combines rule-based NER, TF-IDF RAG, and an explainable logistic-regression scoring model with optional LLM enrichment -- degrades gracefully at every layer.
- **Feasibility** -- entirely Python/FastAPI + vanilla JS, runs on a laptop with no GPU and no mandatory API key.
