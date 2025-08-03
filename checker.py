from grammar_checker import check_grammar
from scorer import get_grammar_score
from highlighter import highlight_text_with_markers as highlight_text

def process_text(answer_text: str):
    lines = answer_text.strip().split("\n")
    corrected_lines = []
    total_errors = 0
    highlighted_errors = []
    error_log = []

    for line in lines:
        errors = check_grammar(line)
        if errors:
            total_errors += len(errors)
            highlighted_line, corrected_line = highlight_text(line, errors)
            highlighted_errors.append({
                "highlighted": highlighted_line,
                "corrected_line": corrected_line
            })
            error_log.append({
                "highlighted": highlighted_line,
                "corrected": corrected_line
            })
            corrected_lines.append(corrected_line)
        else:
            highlighted_errors.append({
                "highlighted": line,
                "corrected_line": line
            })
            # Optional: include non-error lines in error_log too
            corrected_lines.append(line)

    corrected_text = "\n".join(corrected_lines)
    score, remark = get_grammar_score(answer_text, corrected_text, total_errors)

    return {
        "original": answer_text,
        "corrected": corrected_text,
        "highlighted_errors": highlighted_errors,
        "errors": error_log,  # ✅ Now correctly populated
        "score": score,
        "remark": remark,
        "total_errors": total_errors
    }

