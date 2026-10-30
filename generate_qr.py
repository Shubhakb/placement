import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

ARTIFACT_DIR = r"C:\Users\DELL\.gemini\antigravity-ide\brain\eb33d7c7-9a7d-4cf0-9c90-871c0f43671b"
STATIC_DIR = r"c:\Users\DELL\Desktop\college_placement_management_system1\static"

os.makedirs(ARTIFACT_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

public_url = "https://mulberry-nimble-carpentry.ngrok-free.dev"

# 1. Generate clean high-res QR Code
qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=12,
    border=4,
)
qr.add_data(public_url)
qr.make(fit=True)

qr_img = qr.make_image(fill_color="#1e293b", back_color="#ffffff").convert("RGBA")

# Save direct QR codes
qr_img.save(os.path.join(STATIC_DIR, "qr_code.png"))
qr_img.save(os.path.join(ARTIFACT_DIR, "qr_code.png"))

# 2. Create a premium poster card for students
card_width = 700
card_height = 920

card = Image.new("RGBA", (card_width, card_height), "#0f172a")
draw = ImageDraw.Draw(card)

# Header banner gradient-like accent
draw.rectangle([0, 0, card_width, 140], fill="#1e3a8a")

# Title text
try:
    font_large = ImageFont.truetype("arial.ttf", 34)
    font_sub = ImageFont.truetype("arial.ttf", 20)
    font_bold = ImageFont.truetype("arialbd.ttf", 24)
    font_small = ImageFont.truetype("arial.ttf", 16)
except Exception:
    font_large = font_sub = font_bold = font_small = ImageFont.load_default()

# Header text
draw.text((card_width // 2, 45), "CAMPUS PLACEMENT PORTAL", fill="#ffffff", font=font_large, anchor="mm")
draw.text((card_width // 2, 90), "Official Student & Placement Recruitment Portal", fill="#93c5fd", font=font_sub, anchor="mm")

# White QR Container Card
container_pad_x = 75
container_top = 180
container_bottom = 740
draw.rounded_rectangle([container_pad_x, container_top, card_width - container_pad_x, container_bottom], radius=24, fill="#ffffff")

# Paste QR in center of container
qr_resized = qr_img.resize((440, 440))
qr_paste_x = (card_width - 440) // 2
qr_paste_y = 210
card.paste(qr_resized, (qr_paste_x, qr_paste_y), qr_resized)

# Instruction below QR inside white container
draw_white = ImageDraw.Draw(card)
draw_white.text((card_width // 2, 675), "Scan with your Phone Camera", fill="#0f172a", font=font_bold, anchor="mm")
draw_white.text((card_width // 2, 705), "Open camera and tap the link to join directly", fill="#64748b", font=font_small, anchor="mm")

# Footer URL pill
pill_top = 770
pill_bottom = 830
draw.rounded_rectangle([60, pill_top, card_width - 60, pill_bottom], radius=16, fill="#1e293b", outline="#3b82f6", width=2)
draw.text((card_width // 2, (pill_top + pill_bottom) // 2), public_url, fill="#60a5fa", font=font_bold, anchor="mm")

# Bottom note
draw.text((card_width // 2, 875), "Available 24/7 for Placement Drives, Jobs & Interviews", fill="#94a3b8", font=font_small, anchor="mm")

card.save(os.path.join(STATIC_DIR, "placement_scanner_poster.png"))
card.save(os.path.join(ARTIFACT_DIR, "placement_scanner_poster.png"))

print("QR Code generated successfully at:")
print(os.path.join(STATIC_DIR, "qr_code.png"))
print(os.path.join(STATIC_DIR, "placement_scanner_poster.png"))
