from grammar_checker import check_grammar, correct_text
from scorer import get_grammar_score
from highlighter import highlight_text_with_markers as highlight_text

def process_text(answer_text: str):
    # Process the entire text at once for better context
    errors = check_grammar(answer_text)
    total_errors = len(errors)
    
    # Get corrected text using the improved correct_text function
    corrected_text = correct_text(answer_text)
    
    # Create error log from the corrections
    error_log = []
    highlighted_errors = []
    
    if errors:
        # Process errors for highlighting and logging
        highlighted_line, _ = highlight_text(answer_text, errors)
        
        for i, error in enumerate(errors):
            error_log.append({
                "highlighted": error.get('message', f'Grammar issue {i+1}'),
                "corrected": error.get('better', 'Correction applied')
            })
            
        highlighted_errors.append({
            "highlighted": highlighted_line,
            "corrected_line": corrected_text
        })
    else:
        highlighted_errors.append({
            "highlighted": answer_text,
            "corrected_line": corrected_text
        })
    
    # If no API errors were found but text was still corrected, 
    # estimate errors based on text differences
    if total_errors == 0 and corrected_text != answer_text:
        # Use dynamic comparison to identify improvements
        import difflib
        
        # Count significant differences
        differences = []
        words_original = answer_text.split()
        words_corrected = corrected_text.split()
        
        # Simple word-level comparison
        if len(words_original) != len(words_corrected):
            differences.append("Text length changed")
        
        # Check for major changes
        for i, (orig, corr) in enumerate(zip(words_original, words_corrected)):
            if orig.lower() != corr.lower():
                differences.append(f"Changed '{orig}' to '{corr}'")
        
        # Estimate errors based on differences (but cap it)
        estimated_errors = min(len(differences), 10)
        
        if estimated_errors > 0:
            total_errors = estimated_errors
            
            # Add difference-based error log
            for diff in differences[:5]:  # Show only first 5
                error_log.append({
                    "highlighted": diff,
                    "corrected": "Applied correction"
                })

    score, remark = get_grammar_score(answer_text, corrected_text, total_errors)

    return {
        "original": answer_text,
        "corrected": corrected_text,
        "highlighted_errors": highlighted_errors,
        "errors": error_log,
        "score": score,
        "remark": remark,
        "total_errors": total_errors
    }

