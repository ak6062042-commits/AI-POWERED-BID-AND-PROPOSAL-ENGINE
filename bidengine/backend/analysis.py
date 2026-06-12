import re
import json
import os
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

ISO_PATTERN = re.compile(r"ISO\s?\d{4,5}", re.IGNORECASE)
KNOWN_CERTS = [
    "ISO 9001", "ISO 27001", "ISO 14001", "CMMI Level 3", "PMP",
    "PEC Registered", "OHSAS 18001", "Microsoft Gold Partner",
    "AWS Advanced Tier Partner", "CISSP",
]


def _extract_required_certs(mandatory_requirements: List[Dict[str, Any]]) -> List[str]:
    found = set()
    for req in mandatory_requirements:
        text = req.get("text", "")
        for iso in ISO_PATTERN.findall(text):
            found.add(iso.upper().replace("ISO", "ISO ").replace("  ", " ").strip())
        for cert in KNOWN_CERTS:
            if cert.lower() in text.lower():
                found.add(cert)
    return sorted(found)


def _library_cert_pool() -> set:
    with open(os.path.join(DATA_DIR, "capability_library.json"), encoding="utf-8") as f:
        library = json.load(f)
    pool = set()
    for entry in library:
        for c in entry.get("certifications", []):
            pool.add(c.upper().replace("ISO", "ISO ").replace("  ", " ").strip())
    return pool


def _parse_budget_amount(budget_entries: List[Dict[str, str]]) -> float:
    best = 0.0
    pattern = re.compile(r"(PKR|Rs\.?)\s?([\d,]+(?:\.\d+)?)", re.IGNORECASE)
    for entry in budget_entries:
        amount_str = entry.get("amount", "")
        m = pattern.search(amount_str)
        if m:
            value = float(m.group(2).replace(",", ""))
            best = max(best, value)
    return best


def compute_scoring_inputs(
    extraction: Dict[str, Any],
    checklist_summary: Dict[str, Any],
    estimated_competitor_count: int = 5,
    past_relationship: bool = False,
) -> Dict[str, Any]:
    required_certs = _extract_required_certs(extraction.get("mandatory_requirements", []))
    library_certs = _library_cert_pool()
    if required_certs:
        matched = sum(1 for c in required_certs if c.upper() in library_certs)
        certifications_match_pct = round(matched / len(required_certs) * 100, 1)
    else:
        certifications_match_pct = 70.0 

    requirements_matched_pct = checklist_summary.get("requirements_matched_pct", 50.0)
    rfp_budget = _parse_budget_amount(extraction.get("budget", []))
    if rfp_budget > 0:
        with open(os.path.join(DATA_DIR, "capability_library.json"), encoding="utf-8") as f:
            library = json.load(f)
        values = [e["contract_value_pkr"] for e in library]
        median_value = sorted(values)[len(values) // 2]
        ratio = min(rfp_budget, median_value * 5) / max(rfp_budget, median_value * 5)
        budget_alignment_score = round(0.4 + 0.6 * ratio, 2)
    else:
        budget_alignment_score = 0.65  

    technical_score_pct = round(min(95, max(40, requirements_matched_pct + 10)), 1)

    return {
        "certifications_match_pct": certifications_match_pct,
        "requirements_matched_pct": requirements_matched_pct,
        "past_relationship": 1 if past_relationship else 0,
        "budget_alignment_score": budget_alignment_score,
        "technical_score_pct": technical_score_pct,
        "estimated_competitor_count": estimated_competitor_count,
        "required_certifications_detected": required_certs,
        "rfp_budget_pkr": rfp_budget,
    }
