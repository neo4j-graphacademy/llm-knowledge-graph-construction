# Used to create the /data/courses/pdf docs directory
# Extracts the lesson.adoc files and creates a pdf for each lesson
# neo4j-graphacademy/courses repo
import os
import glob

from fpdf import FPDF

COURSES_REPO_PATH = "../../courses"
DATA_PATH = "llm-knowledge-graph/data/course"
PDF_PATH = os.path.join(DATA_PATH, 'pdfs')
FONT_PATH = os.path.join(DATA_PATH, 'CourierPrime-Regular.ttf')

# Extract just the genai-fundamentals courses
SEARCH = "/**/genai-fundamentals/**/lesson.adoc"
# Extract all courses
# SEARCH = "/**/lesson.adoc"

def create_pdf(text, path):
    pdf = FPDF()

    pdf.add_page()
    pdf.add_font("CourierPrime", style="", fname=FONT_PATH, uni=True)
    pdf.set_font('CourierPrime', size=12)

    pdf.write(5, text)
    pdf.output(path)

# Find the lesson files
for file in glob.glob(COURSES_REPO_PATH + SEARCH, recursive=True):
    print(file)

    path = file.split(os.path.sep)
    pdf_file_name = f"{path[-6]}_{path[-4]}_{path[-2]}.pdf"

    print(pdf_file_name)

    # create the pdf
    with open(file, "r") as f:
        text = f.read()
        create_pdf(text, os.path.join(PDF_PATH, pdf_file_name))
