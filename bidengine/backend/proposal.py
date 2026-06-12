
import os
import json
import re
from typing import List, Dict, Any

from rag import CapabilityMatcher


def _format_currency(value: int) -> str:
    return f"PKR {value:,}"


def _template_draft(question: str, matches: List[Dict[str, Any]]) -> str:
    if not matches:
        return (
            "Our organization does not currently have directly comparable "
            "project evidence on file for this section. We recommend "
            "either sourcing a relevant case study before submission or "
            "partnering with a subcontractor to strengthen this response."
        )

    paras = []
    intro_evidence = matches[0]
    client_label = intro_evidence['client_type']
    client_label = client_label if client_label.isupper() or "SME" in client_label else client_label.lower()
    paras.append(
        f"Our organization is well positioned to address this requirement, "
        f"drawing on relevant experience including \"{intro_evidence['title']}\" "
        f"({intro_evidence['year_completed']}), a {_format_currency(intro_evidence['contract_value_pkr'])} "
        f"engagement delivered for a {client_label} client in the "
        f"{intro_evidence['sector']} sector."
    )

    if len(matches) > 1:
        other_titles = ", ".join(f"\"{m['title']}\"" for m in matches[1:])
        paras.append(
            f"This is further supported by additional relevant engagements, "
            f"including {other_titles}, demonstrating a consistent track "
            f"record of delivery in this domain."
        )

    certs = set()
    for m in matches:
        certs.update(m.get("certifications", []))
    if certs:
        paras.append(
            f"Our team's relevant certifications -- {', '.join(sorted(certs))} -- "
            f"underpin the quality and compliance assurance applied to this "
            f"engagement."
        )

    paras.append(
        "[Bid manager: please review and add project-specific details, "
        "named personnel, and quantified outcomes before final submission.]"
    )

    return " ".join(paras)


def _llm_polish(question: str, template_draft: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return template_draft

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""You are a professional bid writer. Rewrite the draft
response below into a polished, confident, 2-3 paragraph proposal answer
to the RFP question. Keep all factual details (project names, values,
years, certifications) exactly as given -- do not invent new facts. Keep
the final bracketed reviewer note at the end verbatim. Return only the
rewritten text, no preamble.

QUESTION:
{question}

DRAFT:
{template_draft}
"""
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        text_out = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()
        return text_out or template_draft
    except Exception:
        return template_draft


def generate_proposal_draft(
    qa_sections: List[Dict[str, str]],
    matcher: CapabilityMatcher,
    use_llm: bool = True,
) -> List[Dict[str, Any]]:
    draft_sections = []
    for qa in qa_sections:
        question = qa.get("question", "")
        matches = matcher.match(question, top_k=2)
        template_draft = _template_draft(question, matches)
        final_draft = _llm_polish(question, template_draft) if use_llm else template_draft

        draft_sections.append({
            "id": qa.get("id"),
            "question": question,
            "draft_response": final_draft,
            "evidence_used": [
                {"capability_id": m["capability_id"], "title": m["title"]}
                for m in matches
            ],
            "status": "needs_review",
        })
    return draft_sections


if __name__ == "__main__":
    import extraction
    result = extraction.extract(
        "/home/claude/bidengine/sample_rfps/PITB_ICMS_RFP_2026.docx", use_llm=False
    )
    matcher = CapabilityMatcher()
    drafts = generate_proposal_draft(result.qa_sections, matcher, use_llm=False)
    print(json.dumps(drafts, indent=2))
