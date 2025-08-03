def highlight_text_with_markers(text, matches):
    highlighted = text
    corrected = text
    offset = 0

    for match in matches:
        offset_start = match['offset'] + offset
        error_length = match['length']

        start_marker = "[!! "
        end_marker = " !!]"

        highlighted = (
            highlighted[:offset_start] +
            start_marker +
            highlighted[offset_start:offset_start + error_length] +
            end_marker +
            highlighted[offset_start + error_length:]
        )
        offset += len(start_marker) + len(end_marker)

    # Apply basic correction
    for match in reversed(matches):  # reverse to avoid offset conflict
        start = match['offset']
        end = start + match['length']
        corrected = corrected[:start] + match['better'] + corrected[end:]

    return highlighted, corrected
