import re


def normalize_str(text: str) -> str:
    text = text.strip().lower()\
        .replace("-", "_")\
        .replace(" ", "_")\
        .replace("d", "o")\
        .replace("i", "l")
    return re.sub(r'\W+', '', text)
