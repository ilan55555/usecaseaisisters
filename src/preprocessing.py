from bs4 import BeautifulSoup
import pandas as pd
import re

def clean_text(txt: str) -> str:
    txt = txt.replace("\xa0", " ")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()

def read_any(path: str) -> str:
    if path.endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return clean_text(f.read())
    if path.endswith(".csv"):
        df = pd.read_csv(path)
        return clean_text(df.to_csv(index=False))
    if path.endswith(".html"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            return clean_text(soup.get_text(separator="\n"))
    raise ValueError("Format non supporté (.txt, .csv, .html uniquement)")

def chunk(text: str, size=800, overlap=100):
    tokens = text.split()
    i = 0
    while i < len(tokens):
        yield " ".join(tokens[i:i+size])
        i += max(size - overlap, 1)