# Shared layout constants for the A1 academic poster template.
# All distances are in millimetres (mm). Each renderer converts to its own units.

# --- Canvas (A1 portrait) ---
W_MM = 594
H_MM = 841
M_MM = 20          # horizontal margin
G_MM = 10          # gap between columns
COL_W_MM = (W_MM - 2 * M_MM - 2 * G_MM) / 3.0

# --- Vertical zones (y measured from top, mm) ---
TOP_BANNER_H = 20
HEADER_H = 110
TOP_SEC_Y = TOP_BANNER_H + HEADER_H
TOP_SEC_H = 250
CASE_TITLE_H = 35
CASE_SEC_Y = TOP_SEC_Y + TOP_SEC_H + 10
CASE_SEC_H = 330
BOT_SEC_Y = CASE_SEC_Y + CASE_SEC_H + 10
BOT_SEC_H = 60
FOOTER_H = H_MM - BOT_SEC_Y - BOT_SEC_H

# --- Font sizes (pt) ---
TITLE_PT = 40
SUBTITLE_PT = 17
SECTION_PT = 22
BODY_PT = 15
SMALL_PT = 12
FOOT_PT = 11
DRAFT_PT = 13

# --- Colours (hex) ---
COLORS = {
    "DARK_BLUE": "#0E3F8C",
    "MAIN_BLUE": "#1E4FA8",
    "MID_BLUE":  "#3D7BD9",
    "LIGHT_BG":  "#F7F9FC",
    "LIGHT_BLUE": "#E8EFF8",
    "TEXT_DARK": "#1A2230",
    "TEXT_GRAY": "#4A5568",
    "AUX_GRAY":  "#8B97A8",
    "LINE":      "#D6DCE5",
    "WHITE":     "#FFFFFF",
    "RED":       "#D9534F",
}

# Image search dir (relative to the project working directory)
IMG_DIR = "resources/images"
