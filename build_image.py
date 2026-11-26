import json
from datetime import date
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SANS = "DejaVuSans.ttf"
BOLD = "DejaVuSans-Bold.ttf"
SERIF = "DejaVuSerif-Bold.ttf"
SIZE = 1024
MARGIN = 16
GAP = 16
HEADER_HEIGHT = 168
GRID_TOP = 192
CARD_WIDTH = (SIZE - 2 * MARGIN - GAP) // 2
CARD_HEIGHT = 204
TEXT_INSET = 16
TEXT_WIDTH = CARD_WIDTH - 2 * TEXT_INSET
TITLE = "26 November 2026"
COLORS = {
    "navy": "#0E2A47",
    "gold": "#E8B84B",
    "ink": "#111827",
    "muted": "#475569",
    "paper": "#F1F5F9",
    "border": "#CBD5E1",
    "white": "#FFFFFF",
    "mist": "#BACDE0",
}
MEASUREMENTS = []


@lru_cache(maxsize=None)
def font_face(filename, size):
    return ImageFont.truetype(str(FONT_DIR / filename), size)


def line_fits(canvas, text, font, width):
    bounds = canvas.textbbox((0, 0), text, font=font, anchor="lt")
    return (
        canvas.textlength(text, font=font) <= width
        and bounds[0] >= 0
        and bounds[2] <= width
    )


def wrap_words(canvas, text, font, width):
    lines = []
    current_line = ""
    for word in text.split():
        candidate = f"{current_line} {word}" if current_line else word
        if current_line and not line_fits(canvas, candidate, font, width):
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)
    return lines


def fit_text(canvas, text, filename, largest, smallest, width, limit):
    for size in range(largest, smallest - 1, -1):
        font = font_face(filename, size)
        lines = wrap_words(canvas, text, font, width)
        if len(lines) <= limit and all(
            line_fits(canvas, line, font, width) for line in lines
        ):
            assert " ".join(lines) == text, ("Text was changed", text, lines)
            return font, lines
    raise ValueError(f"Cannot fit complete text in {limit} lines: {text}")


def checked_text(canvas, position, text, font, fill, bounds, label, anchor="lt"):
    rectangle = canvas.textbbox(position, text, font=font, anchor=anchor)
    advance = canvas.textlength(text, font=font)
    assert bounds[0] <= rectangle[0] <= rectangle[2] <= bounds[2], (
        label, text, rectangle, bounds
    )
    assert bounds[1] <= rectangle[1] <= rectangle[3] <= bounds[3], (
        label, text, rectangle, bounds
    )
    assert advance <= bounds[2] - bounds[0], (label, text, advance, bounds)
    MEASUREMENTS.append({
        "label": label,
        "text": text,
        "position": position,
        "anchor": anchor,
        "font_path": font.path,
        "font_size": font.size,
        "bbox": rectangle,
        "bounds": bounds,
        "advance": advance,
    })
    canvas.text(position, text, font=font, fill=fill, anchor=anchor)


def draw_header(canvas, news):
    canvas.rectangle((0, 0, SIZE - 1, HEADER_HEIGHT - 1), fill=COLORS["navy"])
    canvas.rectangle(
        (0, HEADER_HEIGHT, SIZE - 1, HEADER_HEIGHT + 3), fill=COLORS["gold"]
    )
    header_bounds = (24, 16, 812, 156)
    checked_text(
        canvas, (36, 30), f"WORLD NEWS • {news['day'].upper()}",
        font_face(BOLD, 21), COLORS["gold"], header_bounds, "kicker"
    )
    checked_text(
        canvas, (36, 66), TITLE, font_face(SERIF, 58), COLORS["white"],
        header_bounds, "title"
    )
    checked_text(
        canvas, (36, 130), "The day's biggest stories, in one image",
        font_face(SANS, 23), COLORS["mist"], header_bounds, "subtitle"
    )
    badge_bounds = (828, 34, 988, 132)
    canvas.rounded_rectangle(
        badge_bounds, radius=12, outline=COLORS["gold"], width=2
    )
    checked_text(
        canvas, (908, 48), "NOV", font_face(BOLD, 21), COLORS["gold"],
        badge_bounds, "badge month", anchor="mt"
    )
    checked_text(
        canvas, (908, 74), "26", font_face(SERIF, 40), COLORS["white"],
        badge_bounds, "badge day", anchor="mt"
    )


def draw_card(canvas, story, index):
    column_index = index % 2
    row_index = index // 2
    left = MARGIN + column_index * (CARD_WIDTH + GAP)
    top = GRID_TOP + row_index * (CARD_HEIGHT + GAP)
    card_bounds = (left, top, left + CARD_WIDTH, top + CARD_HEIGHT)
    canvas.rounded_rectangle(
        card_bounds, radius=14, fill=COLORS["white"],
        outline=COLORS["border"], width=1
    )
    canvas.rounded_rectangle(
        (left, top, left + 8, top + CARD_HEIGHT), radius=4, fill=story["color"]
    )
    tag_font = font_face(BOLD, 17)
    tag_width = int(canvas.textlength(story["tag"], font=tag_font) + 21)
    tag_bounds = (
        left + TEXT_INSET, top + 16, left + TEXT_INSET + tag_width, top + 44
    )
    assert tag_bounds[2] <= left + CARD_WIDTH - TEXT_INSET
    canvas.rounded_rectangle(tag_bounds, radius=7, fill=story["color"])
    checked_text(
        canvas, (left + TEXT_INSET + 10, top + 23), story["tag"], tag_font,
        COLORS["white"], tag_bounds, f"story {index + 1} tag"
    )
    headline_font, headline_lines = fit_text(
        canvas, story["headline"], BOLD, 25, 18, TEXT_WIDTH, 2
    )
    summary_font, summary_lines = fit_text(
        canvas, story["summary"], SANS, 19, 14, TEXT_WIDTH, 3
    )
    for section, font, lines, offset, leading, bottom in (
        ("headline", headline_font, headline_lines, 60, 30, 116),
        ("summary", summary_font, summary_lines, 125, 25, 194),
    ):
        section_bounds = (
            left + TEXT_INSET, top + offset,
            left + CARD_WIDTH - TEXT_INSET, top + bottom
        )
        assert card_bounds[0] <= section_bounds[0] < section_bounds[2] <= card_bounds[2]
        assert card_bounds[1] <= section_bounds[1] < section_bounds[3] <= card_bounds[3]
        previous_bottom = section_bounds[1]
        for line_index, line in enumerate(lines):
            position = (left + TEXT_INSET, top + offset + line_index * leading)
            rectangle = canvas.textbbox(position, line, font=font, anchor="lt")
            assert previous_bottom <= rectangle[1], (story["tag"], section, line)
            previous_bottom = rectangle[3]
            checked_text(
                canvas, position, line, font,
                COLORS["ink"] if section == "headline" else COLORS["muted"],
                section_bounds, f"story {index + 1} {section}"
            )


def draw_also_today(canvas, news):
    top = GRID_TOP + 3 * CARD_HEIGHT + 2 * GAP + 16
    canvas.rounded_rectangle(
        (MARGIN, top, SIZE - MARGIN, top + 100), radius=14, fill=COLORS["paper"]
    )
    text_bounds = (
        MARGIN + TEXT_INSET, top + 8, SIZE - MARGIN - TEXT_INSET, top + 96
    )
    checked_text(
        canvas, (MARGIN + TEXT_INSET, top + 13), "ALSO TODAY", font_face(BOLD, 19),
        COLORS["navy"], text_bounds, "also heading"
    )
    bullet_lines = [f"•  {story}" for story in news["also_today"]]
    for size in range(19, 13, -1):
        font = font_face(SANS, size)
        if all(line_fits(canvas, line, font, text_bounds[2] - text_bounds[0])
               for line in bullet_lines):
            break
    else:
        raise ValueError("The also-today stories do not fit the strip")
    for line_index, line in enumerate(bullet_lines):
        checked_text(
            canvas, (MARGIN + TEXT_INSET, top + 36 + line_index * 20), line, font,
            COLORS["ink"], text_bounds, "also story"
        )


def build():
    news = json.loads((ROOT / "news.json").read_text(encoding="utf-8"))
    assert news["date"] == "2026-11-26" and news["day"] == "Thursday"
    assert date.fromisoformat(news["date"]).weekday() == 3
    assert len(news["stories"]) == 6 and len(news["also_today"]) == 3
    MEASUREMENTS.clear()
    image = Image.new("RGB", (SIZE, SIZE), COLORS["white"])
    canvas = ImageDraw.Draw(image)
    draw_header(canvas, news)
    for index, story in enumerate(news["stories"]):
        draw_card(canvas, story, index)
    draw_also_today(canvas, news)
    checked_text(
        canvas, (SIZE // 2, 978),
        f"Sources: {' · '.join(news['sources'])}  —  {TITLE}",
        font_face(SANS, 15), COLORS["muted"], (24, 970, SIZE - 24, SIZE - 16),
        "footer", anchor="mt"
    )
    destination = ROOT / "entry.png"
    image.save(destination, format="PNG", optimize=True, compress_level=9)
    byte_size = destination.stat().st_size
    assert image.size == (1024, 1024)
    assert byte_size <= 1048576, byte_size
    print(
        f"entry.png: {SIZE}x{SIZE}, {byte_size:,} bytes; "
        f"{len(MEASUREMENTS)} text lines measured and inside bounds"
    )
    return destination


if __name__ == "__main__":
    build()
