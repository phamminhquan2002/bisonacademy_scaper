import os
from urllib.parse import unquote, urljoin, urlparse

import requests
import yt_dlp
from bs4 import BeautifulSoup

if __name__ == "__main__":
    base_url = "https://bisonacademy.net/ECE111/Index.htm"

    base_url = input("Enter URL: ")

    headers = {"User-Agent": "HTTPie/3.2.3"}

    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    base_dir = "ece111_files/Homework"
    base_dir = input("Save to: ")

    os.makedirs(base_dir, exist_ok=True)

    # Extract the base directory path to compute relative paths
    parsed_base = urlparse(base_url)
    base_path_prefix = os.path.dirname(parsed_base.path)  # e.g., '/ECE111'

    youtube_links = []
    file_extensions = (
        ".pdf",
        ".docx",
        ".pptx",
        ".zip",
        ".xlsx",
        ".pptm",
        ".doc",
        ".ppt",
        ".htm",
    )

    for link in soup.find_all("a"):
        href = link.get("href")
        if not href:
            continue

        if href.startswith("mailto:") or "@" in href:
            continue

        full_url = urljoin(base_url, href)

        if "youtube.com" in full_url or "youtu.be" in full_url:
            if "playlist" not in full_url:
                youtube_links.append(full_url)
            continue

        parsed_full = urlparse(full_url)
        parsed_path = parsed_full.path

        if parsed_path.lower().endswith(file_extensions):
            # Determine path relative to the base page directory
            if parsed_path.startswith(base_path_prefix):
                rel_path = parsed_path[len(base_path_prefix) :].lstrip("/")
            else:
                rel_path = os.path.basename(parsed_path)

            # Decode URL encoding across the entire relative path
            decoded_rel_path = unquote(rel_path)
            file_path = os.path.join(base_dir, decoded_rel_path)

            # Skip downloading if the file already exists locally
            if os.path.exists(file_path):
                print(f"Skipping {decoded_rel_path}: file already exists.")
                continue

            # Create local subdirectories if they do not exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            try:
                print(f"Downloading {decoded_rel_path}...")
                file_response = requests.get(full_url, headers=headers)
                if file_response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(file_response.content)
            except Exception as error:  # noqa: BLE001
                print(f"Failed to download {decoded_rel_path}: {error}")

    print("\nExported YouTube Links:")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-angle",
    }

    ydl_opts = {
        "outtmpl": "ece111_files/ece111_videos/%(title)s.%(ext)s",
        "nocheckcertificate": True,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "cookiefile": "cookies.txt",
    }

    for index, link in enumerate(youtube_links, start=1):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\nProcessing video {index}: {link}")
            # Download the specific video
            ydl.download([link])
