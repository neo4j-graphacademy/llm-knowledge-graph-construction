import os
import subprocess

# OCR yapılmamış PDF'lerin bulunduğu klasör
INPUT_DIR = r"C:\NewMindAI\llm-knowledge-graph-construction\llm-knowledge-graph-construction\llm-knowledge-graph\data\marine\pdfs_raw"
OUTPUT_DIR = r"C:\NewMindAI\llm-knowledge-graph-construction\llm-knowledge-graph-construction\llm-knowledge-graph\data\marine\pdfs_ocr"
# OCR'li PDF'leri buraya kaydedecek


os.makedirs(OUTPUT_DIR, exist_ok=True)

for i in range(1, 83):  # 1.pdf - 81.pdf arası
    input_file = os.path.join(INPUT_DIR, f"{i}.pdf")
    output_file = os.path.join(OUTPUT_DIR, f"{i}_ocr.pdf")

    if os.path.exists(input_file):
        print(f"OCR yapılıyor: {input_file}")
        subprocess.run(["ocrmypdf", input_file, output_file])
    else:
        print(f"Dosya bulunamadı: {input_file}")
