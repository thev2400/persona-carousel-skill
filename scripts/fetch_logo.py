"""
Find and download a company's logo from their website.

Usage: python3 fetch_logo.py <website_url> <output_dir>
Outputs: writes the best logo file found to <output_dir>/logo.<ext>
         and prints the local file path to stdout.

Order of preference:
  1. apple-touch-icon (often clean, often SVG)
  2. <link rel="icon" type="image/svg+xml">
  3. og:image meta tag
  4. shortcut icon
  5. footer <img> with alt containing "logo"

Falls back to writing nothing and exiting non-zero if none found.
"""
import sys
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
import urllib.request


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_link_tags(html):
    """Yield (attrs_dict) for every <link ...> in the HTML."""
    for m in re.finditer(r'<link\b([^>]*)/?>', html, re.I):
        attrs = {}
        for a in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+)["\']', m.group(1)):
            attrs[a.group(1).lower()] = a.group(2)
        yield attrs


def parse_meta_tags(html):
    for m in re.finditer(r'<meta\b([^>]*)/?>', html, re.I):
        attrs = {}
        for a in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+)["\']', m.group(1)):
            attrs[a.group(1).lower()] = a.group(2)
        yield attrs


def parse_img_tags(html):
    for m in re.finditer(r'<img\b([^>]*)/?>', html, re.I):
        attrs = {}
        for a in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+)["\']', m.group(1)):
            attrs[a.group(1).lower()] = a.group(2)
        yield attrs


def find_logo_urls(html, base_url):
    """Return a ranked list of candidate logo URLs.
    SVG sources are preferred — they give clean, exact palette extraction.
    """
    candidates = []

    for attrs in parse_link_tags(html):
        rel = (attrs.get("rel", "") or "").lower()
        href = attrs.get("href")
        type_ = (attrs.get("type", "") or "").lower()
        if not href:
            continue
        url = urljoin(base_url, href)
        is_svg = url.lower().endswith(".svg") or "svg" in type_

        # 1. SVG favicon
        if "icon" in rel and is_svg:
            candidates.append((1, url))
        # 2. apple-touch-icon SVG
        elif "apple-touch-icon" in rel and is_svg:
            candidates.append((2, url))
        # 3. apple-touch-icon (any)
        elif "apple-touch-icon" in rel:
            candidates.append((3, url))
        # 5. shortcut icon / generic icon
        elif "icon" in rel:
            candidates.append((5, url))

    # 4. og:image
    for attrs in parse_meta_tags(html):
        if attrs.get("property") == "og:image" and attrs.get("content"):
            candidates.append((4, urljoin(base_url, attrs["content"])))

    # 6. img with alt/class containing "logo" or "brand"
    for attrs in parse_img_tags(html):
        src = attrs.get("src")
        if not src:
            continue
        alt = (attrs.get("alt", "") or "").lower()
        cls = (attrs.get("class", "") or "").lower()
        if any(k in alt for k in ("logo", "brand")) or "logo" in cls or "brand" in cls:
            candidates.append((6, urljoin(base_url, src)))

    # Within each tier, prefer .svg URLs over .png/.jpg
    def tier_subrank(item):
        tier, url = item
        is_svg = ".svg" in url.lower()
        return (tier, 0 if is_svg else 1)

    candidates.sort(key=tier_subrank)
    seen = set()
    out = []
    for _, url in candidates:
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


def detect_ext(url, content_type=None):
    if content_type:
        ct = content_type.lower()
        if "svg" in ct: return ".svg"
        if "png" in ct: return ".png"
        if "jpeg" in ct or "jpg" in ct: return ".jpg"
        if "webp" in ct: return ".webp"
    parsed = urlparse(url).path.lower()
    for ext in (".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico"):
        if parsed.endswith(ext):
            return ext
    return ".png"


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 fetch_logo.py <website_url> <output_dir>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        html = fetch(url).decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Failed to fetch {url}: {e}", file=sys.stderr)
        sys.exit(2)

    candidates = find_logo_urls(html, url)
    if not candidates:
        print("No logo candidates found in HTML", file=sys.stderr)
        sys.exit(3)

    # Try downloading in preference order
    for cand in candidates:
        try:
            req = urllib.request.Request(cand, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                ct = r.headers.get("Content-Type", "")
                ext = detect_ext(cand, ct)
                data = r.read()
            if len(data) < 100:  # skip suspiciously tiny responses
                continue
            target = out_dir / f"logo{ext}"
            target.write_bytes(data)
            print(str(target))
            return
        except Exception:
            continue

    print("All candidate downloads failed", file=sys.stderr)
    sys.exit(4)


if __name__ == "__main__":
    main()
