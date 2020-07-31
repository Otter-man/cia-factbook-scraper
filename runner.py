"""Main script to run all other modules in project."""
import os
import scripts.sqlite as sq
import scripts.pdf_downloader as pd
from scripts.pdf_scraper import scrape_pdf

CIA_PAGE = """https://www.cia.gov/library/publications/resources/the-world-factbook/docs/one_page_summaries.html"""

links = pd.scrape_pdf_links(CIA_PAGE)  # make list with links for PDF
print("Downloading PDFs...")

PDF_FOLDER_PATH = "pdf"

if not os.path.exists(PDF_FOLDER_PATH):
    os.mkdir(PDF_FOLDER_PATH)

for block in links:
    if len(block) == 5:
        # download PDF 5 at a time
        pd.download_pdf_multi(block, PDF_FOLDER_PATH)

    for item in block:
        # download PDF from last block one by one
        pd.download_pdf_single(item[0], item[1], PDF_FOLDER_PATH)

print("Finished downloading all PDFs")


print("Starting scraping PDFs for text...")
data_containers = scrape_pdf(PDF_FOLDER_PATH)  # scrape data to lists
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

DB_FILE = "data/summaries.db"  # path to DB file

sq.create_db(DB_FILE)  # check DB file, create file if it doesn't exist
print("Finished creating db")

with sq.connect_to_db(DB_FILE) as conn:  # open connection, write to DB
    cur = conn.cursor()
    for i in zip(tables, data_containers):
        sq.write_to_db(cur, i[0], i[1])

print("Finished filling up db")
