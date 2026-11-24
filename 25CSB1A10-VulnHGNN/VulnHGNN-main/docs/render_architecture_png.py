from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "vulnhgnn_updated_architecture.png"
WIDTH, HEIGHT = 2000, 1500

WHITE = "#FFFFFF"
BLACK = "#292929"
GRAY = "#888888"
LIGHT_GRAY = "#D9D9D9"
GREEN = "#E2F2E2"
PINK = "#F7CAD8"
BLUE = "#E7EFF8"
YELLOW = "#FFF2C8"
ORANGE = "#F8E3D8"

FONT_REGULAR = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_ITALIC = r"C:\Windows\Fonts\ariali.ttf"

image = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
draw = ImageDraw.Draw(image)


def font(size, style="regular"):
    path = {
        "regular": FONT_REGULAR,
        "bold": FONT_BOLD,
        "italic": FONT_ITALIC,
    }[style]
    return ImageFont.truetype(path, size)


def wrap(text, selected_font, max_width):
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=selected_font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def centered_text(text, box, selected_font, fill=BLACK, spacing=8):
    x1, y1, x2, y2 = box
    lines = text.split("\n")
    heights = [
        draw.textbbox((0, 0), line, font=selected_font)[3]
        - draw.textbbox((0, 0), line, font=selected_font)[1]
        for line in lines
    ]
    y = (y1 + y2 - sum(heights) - spacing * (len(lines) - 1)) / 2
    for line, height in zip(lines, heights):
        bounds = draw.textbbox((0, 0), line, font=selected_font)
        width = bounds[2] - bounds[0]
        draw.text(((x1 + x2 - width) / 2, y), line, font=selected_font, fill=fill)
        y += height + spacing


def box(rect, title, body, fill=WHITE, title_size=30, body_size=25):
    x1, y1, x2, y2 = rect
    draw.rectangle((x1 + 8, y1 + 8, x2 + 8, y2 + 8), fill="#EEEEEE")
    draw.rectangle(rect, fill=fill, outline=BLACK, width=4)
    title_font = font(title_size, "bold")
    title_lines = wrap(title, title_font, x2 - x1 - 36)
    body_font = font(body_size)
    body_lines = []
    for item in body.split("\n"):
        body_lines.extend(wrap(item, body_font, x2 - x1 - 42))
    line_height = 8
    title_height = sum(
        draw.textbbox((0, 0), line, font=title_font)[3] for line in title_lines
    )
    body_height = sum(
        draw.textbbox((0, 0), line, font=body_font)[3] for line in body_lines
    )
    total_height = title_height + body_height + line_height * (len(title_lines) + len(body_lines))
    y = (y1 + y2 - total_height) / 2
    for line in title_lines:
        bounds = draw.textbbox((0, 0), line, font=title_font)
        draw.text(((x1 + x2 - bounds[2] + bounds[0]) / 2, y), line, font=title_font, fill=BLACK)
        y += bounds[3] + line_height
    y += 3
    for line in body_lines:
        bounds = draw.textbbox((0, 0), line, font=body_font)
        draw.text(((x1 + x2 - bounds[2] + bounds[0]) / 2, y), line, font=body_font, fill=BLACK)
        y += bounds[3] + line_height


def phase(title, y):
    draw.text((100, y), title, font=font(31, "bold"), fill=GRAY)
    draw.line((100, y + 51, 1900, y + 51), fill=LIGHT_GRAY, width=3)
    for x in range(100, 1900, 18):
        draw.line((x, y + 51, min(x + 9, 1900), y + 51), fill=LIGHT_GRAY, width=3)


def arrow(start, end, label=None, label_position=None, color=BLACK, width=5, head=18):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 >= x1 else -1
        points = [
            (x2, y2),
            (x2 - direction * head, y2 - head),
            (x2 - direction * head, y2 + head),
        ]
    else:
        direction = 1 if y2 >= y1 else -1
        points = [
            (x2, y2),
            (x2 - head, y2 - direction * head),
            (x2 + head, y2 - direction * head),
        ]
    draw.polygon(points, fill=color)
    if label and label_position:
        draw.text(label_position, label, font=font(23, "italic"), fill=GRAY)


# Title
title = "VulnHGNN - Updated End-to-End Architecture"
title_font = font(49, "bold")
title_width = draw.textbbox((0, 0), title, font=title_font)[2]
draw.text(((WIDTH - title_width) / 2, 34), title, font=title_font, fill=BLACK)
subtitle = "Gemini + Clang web detection; existing GNN CLI and repair pipeline retained"
subtitle_font = font(26)
subtitle_width = draw.textbbox((0, 0), subtitle, font=subtitle_font)[2]
draw.text(((WIDTH - subtitle_width) / 2, 100), subtitle, font=subtitle_font, fill=GRAY)

# Phase 1: the source-to-IR pipeline and the separate live editor check.
phase("PHASE 1: SOURCE INTAKE & REAL-TIME CHECKS", 165)
box((120, 245, 565, 415), "C / C++ Source", "Web editor or CLI input", GREEN)
box((770, 245, 1215, 415), "Clang Compiler", "Validate and emit LLVM IR", BLUE)
box((1420, 245, 1875, 415), "IR Parser", "Functions, blocks, instructions")
arrow((565, 330), (770, 330), "Compile", (635, 292))
arrow((1215, 330), (1420, 330), "Parse", (1283, 292))

box(
    (205, 455, 1065, 585),
    "Web Detection (Updated)",
    "Live: local Clang checks. Analyze: Gemini agent + Clang.",
    YELLOW,
    title_size=27,
    body_size=22,
)
arrow((342, 415), (342, 455), "While typing", (355, 420), color=GRAY, width=4, head=13)

# Phase 2: graph representation and model inference.
phase("PHASE 2: LEGACY GNN INFERENCE (CLI / REPAIR)", 620)
box((120, 700, 535, 890), "CWE Predictions", "Legacy supported classes and confidence", BLUE)
box((790, 700, 1210, 890), "Legacy VulnHGNN Model", "GATv2Conv layers\nCLI and repair workflows")
box((1460, 700, 1875, 890), "Graph Construction", "Instruction nodes\nControl-flow / data-flow edges", PINK)
arrow((1460, 795), (1210, 795), "PyG graph", (1285, 755))
arrow((790, 795), (535, 795), "Scores", (625, 755))
arrow((1640, 415), (1640, 700), "Extract features", (1655, 570), color=GRAY, width=4, head=14)

# Phase 3: bounded repair and human review.
phase("PHASE 3: LEGACY GNN LOCALIZATION, REPAIR & VERIFY", 935)
box((120, 1015, 500, 1170), "Localization", "Rank suspicious instructions", BLUE)
box((575, 1015, 955, 1170), "Rule-Based IR Repair", "Apply supported repair rules", ORANGE)
box((1030, 1015, 1450, 1170), "Legacy Clang + GNN Re-check", "Compile patched IR; re-run detection", YELLOW, title_size=25)
box((1525, 1015, 1875, 1170), "Bounded Decision", "Stop, or continue if issues remain (limit)", GREEN, title_size=27, body_size=22)
arrow((327, 890), (327, 1015), color=GRAY, width=4, head=14)
arrow((500, 1092), (575, 1092))
arrow((955, 1092), (1030, 1092))
arrow((1450, 1092), (1525, 1092))

# The established feedback loop remains bounded and rechecks patched IR.
draw.line((1700, 1015, 1700, 980), fill=BLACK, width=4)
draw.line((1700, 980, 765, 980), fill=BLACK, width=4)
arrow((765, 980), (765, 1015), width=4, head=14)

box(
    (245, 1205, 1755, 1315),
    "Legacy Source Repair Proposal",
    "Clang-check the proposal; review its diff before Apply or Discard",
    ORANGE,
    title_size=27,
    body_size=22,
)
arrow((1240, 1170), (1240, 1205), color=GRAY, width=4, head=14)
box(
    (260, 1350, 1740, 1440),
    "Web Results / Legacy CLI Reports",
    "Gemini + Clang findings; GNN pipeline and repair results",
    GREEN,
    title_size=26,
    body_size=21,
)
arrow((1000, 1315), (1000, 1350), color=GRAY, width=4, head=14)

footer = (
    "Full web analysis sends code to Gemini; live checks stay local. CLI and repair workflows still use the GNN."
)
footer_font = font(20)
footer_width = draw.textbbox((0, 0), footer, font=footer_font)[2]
draw.text(((WIDTH - footer_width) / 2, 1460), footer, font=footer_font, fill=GRAY)

image.save(OUTPUT, format="PNG", optimize=True, dpi=(180, 180))
print(f"Wrote {OUTPUT} ({WIDTH}x{HEIGHT})")
