from flask import Flask, render_template, request, jsonify, send_file
import io
import pyarabic.araby as araby
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype("font.ttf", 35)
app = Flask(__name__)

def reshape_text(text):
    """تشبيك الحروف العربية مع الحفاظ على التشكيل والحركات"""
    if not text:
        return ""
    
    configuration = {
        'delete_harakat': False,  # عدم حذف التشكيل
        'support_ligatures': True
    }
    
    reshaper = arabic_reshaper.ArabicReshaper(configuration)
    reshaped_text = reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json() or {}
    text = data.get('text', '')
    author = data.get('author', '')
    
    clean_text = araby.strip_harakat(text.strip())
    rhyme = clean_text[-1] if clean_text else "-"
    
    return jsonify({
        'success': True,
        'text': text,
        'author': author,
        'rhyme': rhyme
    })

@app.route('/download-card', methods=['POST'])
def download_card():
    data = request.get_json() or {}
    text = data.get('text', '')
    author = data.get('author', '')
    theme = data.get('theme', 'brown')
    
    width, height = 1000, 650
    
    # 1. لوحة الألوان الفخمة
    if theme == 'brown':
        bg_color = (42, 28, 20)
        text_color = (235, 215, 190)
        author_color = (180, 140, 95)
        border_type = 'classic'
        accent_color = (120, 85, 55)
        
    elif theme == 'gray':
        bg_color = (28, 33, 40)
        text_color = (220, 228, 235)
        author_color = (130, 145, 160)
        border_type = 'classic'
        accent_color = (70, 80, 95)
        
    elif theme == 'blue':
        bg_color = (12, 20, 36)
        text_color = (245, 240, 225)
        author_color = (212, 175, 55)
        border_type = 'gold_elegant'
        accent_color = (212, 175, 55)
        
    elif theme == 'olive':
        bg_color = (25, 34, 22)
        text_color = (238, 235, 220)
        author_color = (150, 165, 130)
        border_type = 'leaf_light'
        accent_color = (100, 115, 85)

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # 2. رسم الإطارات
    if border_type == 'classic':
        draw.rectangle([30, 30, width - 30, height - 30], outline=accent_color, width=2)
    elif border_type == 'gold_elegant':
        draw.rectangle([25, 25, width - 25, height - 25], outline=accent_color, width=2)
        draw.rectangle([33, 33, width - 33, height - 33], outline=accent_color, width=1)
    elif border_type == 'leaf_light':
        draw.rectangle([30, 30, width - 30, height - 30], outline=accent_color, width=1)
        offset = 15
        draw.line([(30, 30 + offset), (30 + offset, 30)], fill=accent_color, width=2)
        draw.line([(width - 30, 30 + offset), (width - 30 - offset, 30)], fill=accent_color, width=2)

    # 3. إعداد الخطوط داخل الدالة
    try:
        font_poem = ImageFont.truetype("Amiri-Regular.ttf", 32)
        font_author = ImageFont.truetype("Amiri-Regular.ttf", 24)
    except:
        try:
            font_poem = ImageFont.truetype("arial.ttf", 30)
            font_author = ImageFont.truetype("arial.ttf", 24)
        except:
            font_poem = ImageFont.load_default()
            font_author = ImageFont.load_default()

    # 4. معالجة النص ديناميكياً
    raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
    reshaped_lines = [reshape_text(line) for line in raw_lines]
    final_author = reshape_text(f"- {author}" if author else "")

    line_height = 50
    total_poem_height = len(reshaped_lines) * line_height
    start_y = (height - total_poem_height - (60 if author else 0)) / 2

    current_y = start_y
    for line in reshaped_lines:
        line_bbox = draw.textbbox((0, 0), line, font=font_poem)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) / 2
        
        draw.text((line_x, current_y), line, font=font_poem, fill=text_color)
        current_y += line_height

    if final_author:
        author_y = current_y + 35
        author_bbox = draw.textbbox((0, 0), final_author, font=font_author)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (width - author_width) / 2
        draw.text((author_x, author_y), final_author, font=font_author, fill=author_color)

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name=f'poetry_card_{theme}.png')

if __name__ == '__main__':
    app.run(debug=True)
