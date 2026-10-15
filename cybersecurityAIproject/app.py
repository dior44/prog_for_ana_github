
import csv
from pathlib import Path
from urllib.parse import urlsplit

from flask import Flask, render_template, request

app = Flask(__name__)
DATABASE = Path(__file__).with_name("reddit_links.csv")


def normalize_url(url):
    url = url.strip()

    if not url:
        return None

    if "://" not in url:
        url = "https://" + url

    parts = urlsplit(url)

    if parts.scheme.lower() not in ("http", "https"):
        raise ValueError("Enter an HTTP or HTTPS URL.")

    if not parts.hostname:
        raise ValueError("Please enter a valid URL.")

    hostname = parts.hostname.lower().removeprefix("www.")

    try:
        port = parts.port
    except ValueError:
        raise ValueError("Invalid port in URL.")

    if port and not (
        (parts.scheme.lower() == "https" and port == 443)
        or (parts.scheme.lower() == "http" and port == 80)
    ):
        hostname = f"{hostname}:{port}"

    path = parts.path.rstrip("/") or "/"

    return hostname, path, parts.query


def load_links():
    if not DATABASE.exists():
        raise FileNotFoundError("reddit_links.csv is missing.")

    with DATABASE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        return list(csv.DictReader(file))


@app.route("/")
def home():
    return render_template(
        "index.html",
        message=None,
        status="",
        matches=[],
        entered_url=""
    )


@app.route("/check", methods=["POST"])
def check():
    entered_url = request.form.get("url", "").strip()

    try:
        search_key = normalize_url(entered_url)
        links = load_links()

        matches = [
            row for row in links
            if row.get("url")
            and normalize_url(row["url"]) == search_key
        ]

        if matches:
            message = f"FOUND: {len(matches)} matching link(s)."
            status = "success"
        else:
            message = "NOT FOUND: This URL is not in the database."
            status = "error"

    except ValueError as error:
        message = str(error)
        status = "error"
        matches = []

    except (OSError, csv.Error) as error:
        app.logger.error("Database error: %s", error)
        message = "Unable to read the link database."
        status = "error"
        matches = []

    return render_template(
        "index.html",
        message=message,
        status=status,
        matches=matches,
        entered_url=entered_url
    )


if __name__ == "__main__":
    app.run(debug=True)
