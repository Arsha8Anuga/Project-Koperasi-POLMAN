import re


def search_regex(term: str) -> dict:
    """Pencarian case-insensitive & cocok sebagian (dokumen 04 §1). Input di-escape
    supaya karakter seperti `(` atau `.*` dari user tidak dianggap regex."""
    return {"$regex": re.escape(term.strip()), "$options": "i"}
