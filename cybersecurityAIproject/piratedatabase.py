#build database.py

from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

# Read the saved Reddit webpage
html_file = Path("r_Piracy Wiki_ Books, Audiobooks & More.html")

if not html_file.exists():
    raise FileNotFoundError(
        "r_Piracy Wiki_ Books, Audiobooks & More.html was not found. "
        "Put it in the same folder as this script."
    )

with html_file.open("r", encoding="utf-8", errors="replace") as file:
    soup = BeautifulSoup(file, "html.parser")

rows = []

# Find hyperlinks in the saved webpage
for link in soup.find_all("a", href=True):
    url = link["href"].strip()
    link_text = link.get_text(" ", strip=True)

    # Keep actual web links with meaningful displayed text
    if url.startswith(("http://", "https://")) and link_text:
        rows.append({
            "link_text": link_text,
            "url": url
        })

# Create the database and remove exact duplicates
df = pd.DataFrame(rows, columns=["link_text", "url"])
df = df.drop_duplicates(subset=["link_text", "url"])

df.to_csv("reddit_links.csv", index=False, encoding="utf-8-sig")

print(f"Extracted {len(df)} hyperlinks.")
print("Saved database to reddit_links.csv")
print(df.head(10).to_string(index=False))
