import re


def _extract_report_lines(report_text):
    return [line.strip() for line in report_text.splitlines() if line.strip()]


def _find_matching_lines(report_text, keywords):
    matches = []
    for line in _extract_report_lines(report_text):
        lowered = line.lower()
        if any(keyword in lowered for keyword in keywords):
            matches.append(line)
    return matches


def generate_local_analysis(data):
    report_text = ""
    patient_name = "Patient"
    age = "Unknown"
    gender = "Unknown"

    if isinstance(data, dict):
        report_text = data.get("report", "")
        patient_name = data.get("patient_name", patient_name)
        age = data.get("age", age)
        gender = data.get("gender", gender)
    else:
        report_text = str(data)

    metric_keywords = [
        "hemoglobin",
        "glucose",
        "cholesterol",
        "hdl",
        "ldl",
        "triglycerides",
        "wbc",
        "rbc",
        "platelets",
        "creatinine",
        "tsh",
        "bilirubin",
        "alt",
        "ast",
    ]
    metric_lines = _find_matching_lines(report_text, metric_keywords)

    note_lines = _find_matching_lines(report_text, ["note", "normal", "abnormal", "reference"])
    summary_line = None
    for line in _extract_report_lines(report_text):
        if "all values are within normal" in line.lower():
            summary_line = "The report explicitly states that values are within normal reference ranges."
            break
        if "no significant abnormalities" in line.lower():
            summary_line = "The report notes that no significant abnormalities were detected."
            break

    if not summary_line:
        summary_line = (
            "This local demo analysis summarizes the visible report values, but it does not replace clinician review."
        )

    highlighted_metrics = metric_lines[:6] if metric_lines else ["No structured metric lines were detected in the report text."]
    supporting_notes = note_lines[:4] if note_lines else ["No additional notes were found in the uploaded report."]

    content = "\n".join(
        [
            f"## Local Demo Analysis for {patient_name}",
            f"Patient profile: {age} years old, {gender}.",
            "",
            "### Summary",
            summary_line,
            "",
            "### Key Values Seen In The Report",
            *[f"- {line}" for line in highlighted_metrics],
            "",
            "### Notes And Interpretation",
            *[f"- {line}" for line in supporting_notes],
            "",
            "### Suggested Next Steps",
            "- Review the highlighted values against the reference ranges printed in the report.",
            "- Discuss symptoms, medications, and history with a licensed clinician before making decisions.",
            "- Configure Groq and Supabase secrets to enable the full AI and saved-account experience.",
        ]
    )

    return {
        "success": True,
        "content": content,
        "model_used": "local/demo-analysis",
    }


def generate_local_chat_response(query, context_text, chat_history=None):
    del chat_history
    query_lower = query.lower()
    context_text = context_text or ""
    query_terms = [term for term in re.findall(r"[a-zA-Z]{3,}", query_lower) if term not in {"what", "does", "this", "that", "with", "from", "about", "report", "mean"}]

    matching_lines = _find_matching_lines(context_text, query_terms)[:3]

    if "normal" in query_lower and "all values are within normal" in context_text.lower():
        return (
            "The report text says that all values are within normal reference ranges and no significant abnormalities were detected. "
            "This is a local demo response based only on the report text."
        )

    if matching_lines:
        joined = " ".join(matching_lines)
        return (
            f"Based on the report text, the most relevant lines are: {joined} "
            "This answer is coming from local demo mode, so it is a simple text-based summary."
        )

    return (
        "I could not find a precise matching line for that question in the current report text. "
        "In local demo mode I only answer from the visible report contents, so adding Groq secrets will enable fuller follow-up responses."
    )
