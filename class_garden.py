import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# -----------------------------
# Load PNGs (must be in same folder as this script)
# -----------------------------
PLANT_IMAGES = {
    "A": Image.open("A.png").convert("RGBA"),
    "B": Image.open("B.png").convert("RGBA"),
    "C": Image.open("C.png").convert("RGBA"),
    "D": Image.open("D.png").convert("RGBA"),
    "F": Image.open("F.png").convert("RGBA"),
}

GRADE_LABELS = {
    "A": "Thriving 🌿",
    "B": "Healthy 🌱",
    "C": "Drooping 🍃",
    "D": "Wilted 🍂",
    "F": "Withered 🥀",
}

# -----------------------------
# Helper functions
# -----------------------------
def grade_to_letter(score):
    if score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 60: return "D"
    else: return "F"

def create_student_image(student_id, grade):
    base_img = PLANT_IMAGES[grade].copy().resize((100,100))
    draw = ImageDraw.Draw(base_img)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()

    # Center the student ID text
    bbox = draw.textbbox((0,0), student_id, font=font)
    text_w, text_h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((base_img.width - text_w)//2, base_img.height - text_h - 5),
              student_id, fill="black", font=font)
    return base_img

def create_legend(img_width):
    padding = 10
    legend_h = 160
    legend_img = Image.new("RGBA", (img_width, legend_h), (245,245,245,255))
    draw = ImageDraw.Draw(legend_img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 16)
        font_label = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = font_label = ImageFont.load_default()

    # Border
    draw.rectangle([0,0,img_width-1,legend_h-1], outline="black", width=2)

    # Title
    title_text = "🌸 Legend: Plant Health"
    bbox = draw.textbbox((0,0), title_text, font=font_title)
    title_w, title_h = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text(((img_width - title_w)//2, padding), title_text, fill="black", font=font_title)

    # Entries
    y = padding + 30
    icon_size = 30
    for grade in ["A","B","C","D","F"]:
        icon = PLANT_IMAGES[grade].copy().resize((icon_size,icon_size))
        legend_img.paste(icon, (padding, y), icon)
        draw.text((padding + icon_size + 10, y + 5), GRADE_LABELS[grade], fill="black", font=font_label)
        y += icon_size + 5

    return legend_img

def create_class_garden(df, cols=4):
    student_images = []
    for _, row in df.iterrows():
        grade = grade_to_letter(row["Score"])
        img = create_student_image(str(row["StudentID"]), grade)
        student_images.append(img)

    if not student_images:
        return None

    img_w, img_h = student_images[0].size
    rows = -(-len(student_images)//cols)  # ceiling division
    garden_w = cols * img_w
    garden_h = rows * img_h
    garden = Image.new("RGBA", (garden_w, garden_h), (245,245,245,255))

    for idx, img in enumerate(student_images):
        x = (idx % cols) * img_w
        y = (idx // cols) * img_h
        garden.paste(img, (x, y), img)

    legend_img = create_legend(garden_w)
    combined_h = garden_h + legend_img.height
    combined = Image.new("RGBA", (garden_w, combined_h), (245,245,245,255))
    combined.paste(garden, (0,0), garden)
    combined.paste(legend_img, (0,garden_h), legend_img)

    return combined

# -----------------------------
# Streamlit app
# -----------------------------
st.title("🌱 Class Garden AI (PNG Plants)")

uploaded_file = st.file_uploader("Upload CSV with StudentID,Score", type="csv")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### Uploaded Data", df)

    garden_img = create_class_garden(df)
    st.image(garden_img, caption="Class Garden", use_column_width=True)

    buf = BytesIO()
    garden_img.save(buf, format="PNG")
    st.download_button("💾 Download Garden Image", data=buf.getvalue(),
                       file_name="class_garden.png", mime="image/png")
