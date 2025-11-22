def log_payload(data: dict):
    import json

    with open("last_payload.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
