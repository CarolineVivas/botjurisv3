# app/service/sanitize.py
def sanitize_dict(data: dict) -> dict:
    """Sanitiza recursivamente um dicionário"""
    if not isinstance(data, dict):
        return data

    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_text(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)  # ✅ Recursivo
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_text(item) if isinstance(item, str) else item for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized
