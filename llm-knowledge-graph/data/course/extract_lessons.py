# Used to create the /data/courses/pdf docs directory
# Extracts the lesson.adoc files and creates a pdf for each lesson
# neo4j-graphacademy/courses repo
import os
import glob
import csv

from fpdf import FPDF

COURSES_REPO_PATH = "../../courses"
DATA_PATH = "llm-knowledge-graph/data/course"
PDF_PATH = os.path.join(DATA_PATH, "pdfs")
FONT_PATH = os.path.join(DATA_PATH, "CourierPrime-Regular.ttf")
DOCS_CSV_PATH = os.path.join(DATA_PATH,"docs.csv")

docs_csv = csv.DictWriter(
    open(DOCS_CSV_PATH, "w", encoding="utf8", newline=""), 
    fieldnames=["filename", "course","module","lesson","url"]
)
docs_csv.writeheader()

# Extract just the genai-fundamentals courses
SEARCH = "/**/genai-fundamentals/**/lesson.adoc"
# Extract all courses
# SEARCH = "/**/lesson.adoc"

def create_pdf(text, path):
    pdf = FPDF()

    pdf.add_page()
    pdf.add_font("CourierPrime", style="", fname=FONT_PATH, uni=True)
    pdf.set_font("CourierPrime", size=12)

    pdf.write(5, text)
    pdf.output(path)

# Find the lesson files
for file in glob.glob(COURSES_REPO_PATH + SEARCH, recursive=True):
    print(file)

    path = file.split(os.path.sep)
    course = path[-6]
    module = path[-4]
    lesson = path[-2]
    pdf_file_name = f"{course}_{module}_{lesson}.pdf"

    print(pdf_file_name)
    
    docs_csv.writerow({
        "filename": pdf_file_name,
        "course": course,
        "module": module,
        "lesson": lesson,
        "url": f"https://graphacademy.neo4j.com/courses/{course}/{module}/{lesson}"
    })

    # create the pdf
    with open(file, "r") as f:
        text = f.read()
        create_pdf(text, os.path.join(PDF_PATH, pdf_file_name))
