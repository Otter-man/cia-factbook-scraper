"""Main script to run all other modules in project."""
import os
import scripts.sqlite_module as sm
from scripts.pdf_downloader_module import scrape_pdf_links, download_pdf
from scripts.pdf_scraper_module import scrape_pdf

CIA_PAGE = """https://www.cia.gov/library/publications/resources/the-world-factbook/docs/one_page_summaries.html"""

links = scrape_pdf_links(CIA_PAGE)  # make dictionary of links for PDF
print("Downloading PDFs...")

download_pdf(links)  # download PDF to folder "pdf"
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

DB_FILE = "data/summaries_new.db"  # path to DB file

sm.create_db(DB_FILE)  # check DB file, create file if it doesn't exist
print("Finished creating db")

with sm.connect_to_db(DB_FILE) as conn:  # open connection, write to DB
    cur = conn.cursor()
    for i in zip(tables, data_containers):
        sm.write_to_db(cur, i[0], i[1])

print("Finished filling up db")
