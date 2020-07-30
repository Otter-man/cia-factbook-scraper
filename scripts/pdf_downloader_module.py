"""Module for scraping CIA page for links and downloading PDF files."""
import os
from requests_html import HTMLSession


def scrape_pdf_links(cia_page):
    """Scrape CIA page for PDF links and return them as dict.

    Args:
        cia_page (str): link to the page, containing PDF files.

    Returns:
        dict: country names are used as keys, link to corresponding PDF
        file as values.
    """

    links = {}

    session = HTMLSession()
    source = session.get(cia_page).html  # downloading page as html

    country_data = source.find("div.country-name")

    for country in country_data:
        links[country.text] = list(country.absolute_links)[0]

    return links


def download_pdf(links):
    """Take dict of links and download them in folder 'PDF'.

    Args:
        links (dict): each key in a dict is a country name, each value is
            a corresponding link to PDF.
    """

    if not os.path.exists("pdf"):
        os.mkdir("pdf")

    for country, link in links.items():

        file_name = country + ".pdf"
        file_path = os.path.join("pdf", file_name)

        # downloading files using HTMLsession
        with open(file_path, "wb") as pdf_file:
            pdf_as_page = HTMLSession().get(link)
            pdf_file.write(pdf_as_page.content)

    print("Finished downloading all PDFs")
