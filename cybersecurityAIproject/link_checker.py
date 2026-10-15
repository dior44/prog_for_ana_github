
from pathlib import Path
from urllib.parse import urlsplit
import pandas as pd

DATABASE = Path(__file__).with_name("reddit_links.csv")


def normalize_url(url):
    url = url.strip()

    if not url:
        return None

    if "://" not in url:
        url = "https://" + url

    parts = urlsplit(url)

    if not parts.hostname:
        raise ValueError("Invalid URL")

    # Treat HTTP and HTTPS, and www/non-www,
    # as equivalent for this lookup.
    hostname = parts.hostname.lower().removeprefix("www.")

    # Preserve non-default ports
    port = parts.port
    if port and not (
        (parts.scheme.lower() == "https" and port == 443)
        or (parts.scheme.lower() == "http" and port == 80)
    ):
        hostname = f"{hostname}:{port}"

    path = parts.path.rstrip("/") or "/"

    return hostname, path, parts.query


def main():
    if not DATABASE.exists():
        print("The link database is missing.")
        return

    df = pd.read_csv(DATABASE).fillna("")

    # Prepare URLs once when the program starts
    df["url_key"] = df["url"].apply(normalize_url)

    print("Reddit Megathread Link Checker")
    print("Enter a URL, or type 'exit' to quit.")

    while True:
        entered = input("\nURL: ").strip()

        if entered.lower() == "exit":
            print("Goodbye!")
            break

        try:
            key = normalize_url(entered)
        except ValueError:
            print("Please enter a valid URL.")
            continue

        if key is None:
            print("Please enter a URL.")
            continue

        matches = df[df["url_key"] == key]

        if matches.empty:
            print("NOT FOUND: This URL is not in the database.")
        else:
            print("FOUND: This URL appears in the database.")

            for _, row in matches.iterrows():
                print("Displayed text:", row["link_text"])
                print("Stored URL:", row["url"])


if __name__ == "__main__":
    main()
