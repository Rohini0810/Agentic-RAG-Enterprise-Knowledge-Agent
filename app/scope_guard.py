
import re

# Topics supported by the current enterprise document collection.
ENTERPRISE_KEYWORDS = {
    "leave", "holiday", "vacation", "absence",
    "remote", "work from home", "wfh",
    "security", "password", "device", "network",
    "expense", "reimbursement", "claim", "approval",
    "benefit", "insurance", "employee", "policy",
    "company", "workplace"
}

def is_in_scope(question: str) -> bool:
    if not question or not question.strip():
        return False

    normalized = question.lower().strip()

    # Match known enterprise terminology.
    return any(
        re.search(r"\b" + re.escape(keyword) + r"\b", normalized)
        for keyword in ENTERPRISE_KEYWORDS
    )
