"""
Render carousel HTML pages to mobile-friendly JPGs and a flat PDF.
Optionally also produces a vector PDF for desktop sharing.

Usage:
  python3 render_carousel.py <output_prefix> <page1.html> [page2.html ...] [--vector-pdf]

Output files (next to the HTML files):
  <prefix>-page1.jpg ... <prefix>-pageN.jpg     (1080x1080, ~130KB each)
  <prefix>-mobile.pdf                           (flat PDF, fast on mobile)
  <prefix>-desktop.pdf                          (vector PDF, optional)

Dependencies: playwright, Pillow, reportlab.
  pip3 install --break-system-packages playwright Pillow reportlab
  python3 -m playwright install chromium
"""
import argparse
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from reportlab.pdfgen import canvas


async def render(html_files, prefix, vector_pdf=False):
    html_files = [Path(p).resolve() for p in html_files]
    out_dir = html_files[0].parent
    jpgs = []
    vector_tmp = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 1080, "height": 1080},
            device_scale_factor=1,  # 1x for mobile-friendly file size
        )
        page = await ctx.new_page()

        for i, src in enumerate(html_files, 1):
            await page.goto(src.as_uri(), wait_until="networkidle")
            await page.wait_for_timeout(400)

            # Capture as JPG via Playwright's screenshot
            jpg_path = out_dir / f"{prefix}-page{i}.jpg"
            await page.locator(".slide").screenshot(
                path=str(jpg_path), type="jpeg", quality=88
            )
            jpgs.append(jpg_path)
            print(f"OK {jpg_path.name}: {jpg_path.stat().st_size} bytes")

            if vector_pdf:
                tmp = out_dir / f"_vec_page{i}.pdf"
                await page.emulate_media(media="print")
                await page.pdf(
                    path=str(tmp),
                    width="1080px", height="1080px",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                    prefer_css_page_size=True,
                )
                vector_tmp.append(tmp)
                # Reset media emulation for next page screenshot
                await page.emulate_media(media="screen")

        await browser.close()

    # Build flat-image PDF (mobile-friendly, fast)
    pt_size = 1080 * 72 / 96  # 810pt = 1080px
    flat_pdf = out_dir / f"{prefix}-mobile.pdf"
    c = canvas.Canvas(str(flat_pdf), pagesize=(pt_size, pt_size))
    for jpg in jpgs:
        c.drawImage(str(jpg), 0, 0, width=pt_size, height=pt_size)
        c.showPage()
    c.save()
    print(f"OK {flat_pdf.name}: {flat_pdf.stat().st_size} bytes")

    # Build vector PDF (optional)
    if vector_pdf and vector_tmp:
        from pypdf import PdfReader, PdfWriter
        writer = PdfWriter()
        for vec in vector_tmp:
            for pg in PdfReader(str(vec)).pages:
                writer.add_page(pg)
        desktop_pdf = out_dir / f"{prefix}-desktop.pdf"
        with open(desktop_pdf, "wb") as f:
            writer.write(f)
        print(f"OK {desktop_pdf.name}: {desktop_pdf.stat().st_size} bytes")
        # Cleanup vector temps (best effort)
        for vec in vector_tmp:
            try: vec.unlink()
            except Exception: pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix", help="Output filename prefix, e.g. 'delightree-carousel'")
    parser.add_argument("html_files", nargs="+", help="HTML page files in order")
    parser.add_argument("--vector-pdf", action="store_true",
                        help="Also produce a vector PDF (desktop-quality, slower on mobile)")
    args = parser.parse_args()

    asyncio.run(render(args.html_files, args.prefix, args.vector_pdf))


if __name__ == "__main__":
    main()
