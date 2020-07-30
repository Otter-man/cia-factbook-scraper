"""Main script to run all other modules in project."""
import os
import scripts.sqlite_module as sm
from scripts.pdf_download import pdf_link_scraper, download_pdf
from scripts.pdf_to_text_script import pdf_scraper


links = pdf_link_scraper()  # make dictionary of links for PDF
print("Downloading PDFs...")

download_pdf(links)  # download PDF to folder "pdf"
print("Starting scraping PDFs for text...")

data_containers = pdf_scraper('pdf')
print("Finished preparing objects")

tables = [
    "Country overview",
    "Natural resources",
    "Export partners",
    "Import partners",
    "Ethnicity",
    "Language",
    "Religion",
]

if not os.path.exists("data"):
    os.mkdir("data")

DB_FILE = "data/summaries_new.db"

sm.create_db(DB_FILE)
print("Finished creating db")

with sm.connect_to_db(DB_FILE) as conn:
    cur = conn.cursor()
    print(type(cur))
    for i in zip(tables, data_containers):
        sm.write_to_db(cur, i[0], i[1])

print("Finished filling up db")
