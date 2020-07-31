"""Main script to run all other modules in project."""
import os
import scripts.sqlite as sq
from scripts.pdf_downloader import scrape_pdf_links, download_pdf
from scripts.pdf_scraper import scrape_pdf

CIA_PAGE = """https://www.cia.gov/library/publications/resources/the-world-factbook/docs/one_page_summaries.html"""

links = scrape_pdf_links(CIA_PAGE)  # make dictionary of links for PDF
print("Downloading PDFs...")

PDF_FOLDER_PATH = "pdf"

if not os.path.exists(PDF_FOLDER_PATH):
    os.mkdir(PDF_FOLDER_PATH)


for country, link in links.items():  # download PDFs to folder "pdf"
    download_pdf(country, link, PDF_FOLDER_PATH)
print("Finished downloading all PDFs")

print("Starting scraping PDFs for text...")

data_containers = scrape_pdf('pdf')  # create list with data containers
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
