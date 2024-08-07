import os, csv

from datasets import load_dataset

# dict_keys(
# ['article', 'byline', 'dates', 'newspaper_metadata', 'antitrust', 'civil_rights', 
# 'crime', 'govt_regulation', 'labor_movement', 'politics', 'protests', 'ca_topic', 
# 'ner_words', 'ner_labels', 'wire_city', 'wire_state', 'wire_country', 'wire_coordinates', 
# 'wire_location_notes', 'people_mentioned', 'cluster_size', 'year'])

ARTICLES_REQUIRED = 100
OUTPUT_PATH = 'llm-knowledge-graph/data'
ARTICLE_FILENAME = os.path.join(OUTPUT_PATH, 'articles.csv')
DATAFILE = '1976_data_clean.json'

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

articles_csv_file.close()