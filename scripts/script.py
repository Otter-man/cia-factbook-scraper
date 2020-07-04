import os
from pdf_to_text_script import pdf_scraper
from pdf_download import pdf_link_scraper, download_pdf

links = pdf_link_scraper()
download_pdf(links)
pdf_scraper("pdf")

