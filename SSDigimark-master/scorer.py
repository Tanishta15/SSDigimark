def get_grammar_score(original, corrected, total_errors):
    """
    Score is based on the number of grammar errors found.
    Fewer errors = higher score.
    """
    if total_errors == 0:
        return 100, "Excellent"
    elif total_errors == 1:
        return 95, "Excellent"
    elif total_errors == 2:
        return 90, "Good"
    elif total_errors <= 4:
        return 80, "Good"
    elif total_errors <= 6:
        return 70, "Fair"
    elif total_errors <= 8:
        return 60, "Needs Improvement"
    else:
        return 50, "Poor"
