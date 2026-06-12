
import os
import json
import re
from typing import List, Dict, Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

PASS_THRESHOLD = 0.18  
PARTIAL_THRESHOLD = 0.08  


def load_capability_library() -> List[Dict[str, Any]]:
    with open(os.path.join(DATA_DIR, "capability_library.json"), encoding="utf-8") as f:
        return json.load(f)


def _capability_corpus(library: List[Dict[str, Any]]) -> List[str]:
    docs = []
    for entry in library:
        cert_text = " ".join(entry.get("certifications", []))
        tag_text = " ".join(entry.get("tags", []))
        docs.append(
            f"{entry['title']} {entry['description']} {cert_text} {tag_text} "
            f"{entry['sector']} {entry['client_type']}"
        )
    return docs


class CapabilityMatcher:
    """Builds a TF-IDF index over the capability library once and reuses it."""

    def __init__(self, library: List[Dict[str, Any]] = None):
        self.library = library or load_capability_library()
        self.corpus = _capability_corpus(self.library)
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(self.corpus)

    def match(self, requirement_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_vec = self.vectorizer.transform([requirement_text])
        sims = cosine_similarity(query_vec, self.matrix)[0]
        ranked_idx = sims.argsort()[::-1][:top_k]
        matches = []
        for idx in ranked_idx:
            score = float(sims[idx])
            if score <= 0:
                continue
            entry = self.library[idx]
            matches.append({
                "capability_id": entry["id"],
                "title": entry["title"],
                "similarity": round(score, 3),
                "sector": entry["sector"],
                "year_completed": entry["year_completed"],
                "contract_value_pkr": entry["contract_value_pkr"],
                "client_type": entry["client_type"],
                "certifications": entry.get("certifications", []),
                "description": entry["description"],
            })
        return matches


def build_compliance_checklist(
    requirements: List[Dict[str, Any]],
    matcher: CapabilityMatcher,
) -> List[Dict[str, Any]]:
    checklist = []
    for req in requirements:
        req_text = req.get("text", "")
        matches = matcher.match(req_text, top_k=3)
        best = matches[0] if matches else None
        best_score = best["similarity"] if best else 0.0

        if best_score >= PASS_THRESHOLD:
            status = "pass"
        elif best_score >= PARTIAL_THRESHOLD:
            status = "partial"
        else:
            status = "gap"

        checklist.append({
            "id": req.get("id"),
            "requirement": req_text,
            "short_label": req.get("short_label", _shorten(req_text)),
            "status": status,
            "best_match": best,
            "alternative_matches": matches[1:] if len(matches) > 1 else [],
        })
    return checklist


def _shorten(text: str, max_words: int = 8) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def checklist_summary(checklist: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(checklist)
    counts = {"pass": 0, "partial": 0, "gap": 0}
    for item in checklist:
        counts[item["status"]] += 1
    matched_pct = round(((counts["pass"] + 0.5 * counts["partial"]) / total) * 100, 1) if total else 0.0
    return {
        "total_requirements": total,
        "pass": counts["pass"],
        "partial": counts["partial"],
        "gap": counts["gap"],
        "requirements_matched_pct": matched_pct,
    }


if __name__ == "__main__":
    import extraction
    result = extraction.extract(
        "/home/claude/bidengine/sample_rfps/PITB_ICMS_RFP_2026.docx", use_llm=False
    )
    matcher = CapabilityMatcher()
    checklist = build_compliance_checklist(result.mandatory_requirements, matcher)
    print(json.dumps(checklist, indent=2)[:3000])
    print("\nSUMMARY:", json.dumps(checklist_summary(checklist), indent=2))
