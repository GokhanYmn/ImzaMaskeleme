import cv2
import sys
import os
import numpy as np
from flask import Flask, request, render_template_string, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # PyInstaller temp dizini
else:
    base_path = os.getcwd()

POPPLER_PATH = os.path.join(base_path, "poppler-25.07.0", "Library", "bin")
UPLOAD_FOLDER = os.path.join(base_path, "uploads")
OUTPUT_FOLDER = os.path.join(base_path, "outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Flask Uygulaması ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="utf-8">
    <title>İmza Maskeleme</title>
  </head>
  <body style="font-family: Arial; margin: 50px;">
    <h2>İmza Maskeleme Uygulaması</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
      <input type="file" name="file" required>
      <button type="submit">Yükle ve Maskele</button>
    </form>
    {% if output_file %}
      <h3>Sonuç:</h3>
      <iframe src="{{ output_file }}" width="600" height="800"></iframe>
      <br><a href="{{ output_file }}" download>📥 PDF İndir</a>
    {% endif %}
  </body>
</html>
"""

# --- Fonksiyonlar ---

def mask_signature(image_path, output_path):
    """Resim dosyası için lacivert imza maskeleme"""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Görüntü okunamadı: {image_path}")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.medianBlur(mask, 5)

    img[mask > 0] = (255, 255, 255)
    cv2.imwrite(output_path, img)

def mask_pdf(pdf_path, output_path):
    """PDF dosyası için lacivert imza maskeleme"""
    pages = convert_from_path(pdf_path, 300, poppler_path=POPPLER_PATH)
    processed_images = []

    for page in pages:
        img = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=2)
        mask = cv2.medianBlur(mask, 5)

        img[mask > 0] = (255, 255, 255)
        processed_images.append(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))

    processed_images[0].save(output_path, save_all=True, append_images=processed_images[1:])

# --- Route'lar ---

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "Dosya yüklenmedi", 400

    file = request.files["file"]
    if file.filename == "":
        return "Dosya seçilmedi", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, "masked_" + filename)

    file.save(input_path)

    ext = filename.split('.')[-1].lower()
    try:
        if ext == "pdf":
            mask_pdf(input_path, output_path)
        elif ext in ["jpg", "jpeg", "png"]:
            mask_signature(input_path, output_path)
        else:
            return "Desteklenmeyen dosya tipi", 400
    except Exception as e:
        return f"Hata oluştu: {str(e)}", 500

    return render_template_string(HTML_TEMPLATE, 
                                  output_file="/outputs/" + "masked_" + filename)

@app.route("/outputs/<filename>")
def output_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename))

# --- Main ---
if __name__ == "__main__":
    app.run(debug=True)
