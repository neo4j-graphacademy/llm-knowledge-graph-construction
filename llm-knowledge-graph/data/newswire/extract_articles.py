import os, csv

from datasets import load_dataset
from fpdf import FPDF

# dict_keys(
# ['article', 'byline', 'dates', 'newspaper_metadata', 'antitrust', 'civil_rights', 
# 'crime', 'govt_regulation', 'labor_movement', 'politics', 'protests', 'ca_topic', 
# 'ner_words', 'ner_labels', 'wire_city', 'wire_state', 'wire_country', 'wire_coordinates', 
# 'wire_location_notes', 'people_mentioned', 'cluster_size', 'year'])

ARTICLES_REQUIRED = 100
DATA_PATH = 'llm-knowledge-graph/data/newswire'
ARTICLE_FILENAME = os.path.join(DATA_PATH, 'articles.csv')
PDF_PATH = os.path.join(DATA_PATH, 'pdfs')
FONT_PATH = os.path.join(DATA_PATH, 'CourierPrime-Regular.ttf')
DATAFILE = '1976_data_clean.json'

def create_pdf(text, path):
    pdf = FPDF()

    pdf.add_page()
    pdf.add_font("CourierPrime", style="", fname=FONT_PATH, uni=True)
    pdf.set_font('CourierPrime', size=12)

    pdf.write(5, text)
    pdf.output(path)

ds = load_dataset("dell-research-harvard/newswire", data_files=DATAFILE, split="train")

articles_csv_file = open(ARTICLE_FILENAME, "w", encoding="utf8", newline='')
fieldnames = [
    'id',
    'date',
    'text',
    'newspapers',
    ]
articles_csv = csv.DictWriter(articles_csv_file, fieldnames=fieldnames)
articles_csv.writeheader()

for i in range(ARTICLES_REQUIRED):
    id = f"1976-{i}"

    print(id)
    print(ds[i]["people_mentioned"])

    text = ds[i]["article"]
    date = ds[i]["dates"][-1]
    newspaper_titles = []
    for newspaper in ds[i]["newspaper_metadata"]:
        newspaper_titles.append(
            newspaper["newspaper_title"][1:-1].replace("'","").split(",")[0]
        )

    articles_csv.writerow({
        'id': id,
        'date': date,
        'text': text,
        'newspapers': newspaper_titles
    })

    create_pdf(text, os.path.join(PDF_PATH, f"{id}.pdf"))

articles_csv_file.close()