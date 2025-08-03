import requests

def check_grammar(text):
    api_url = "https://api.languagetool.org/v2/check"
    data = {
        "text": text,
        "language": "en-US"
    }

    response = requests.post(api_url, data=data)
    result = response.json()

    errors = []
    for match in result.get("matches", []):
        better = match.get("replacements", [])
        suggestion = better[0]['value'] if better else match['context']['text'][match['context']['offset']:match['context']['offset'] + match['length']]

        errors.append({
            "offset": match["offset"],
            "length": match["length"],
            "message": match["message"],
            "better": suggestion
        })

    return errors

def correct_text(text):
    errors = check_grammar(text)
    corrected = list(text)

    # Apply corrections in reverse order to avoid offset issues
    for error in sorted(errors, key=lambda x: -x["offset"]):
        start = error["offset"]
        end = start + error["length"]
        suggestion = error["better"]

        corrected[start:end] = suggestion

    return ''.join(corrected)
