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


def download_pdf(country, link, path_to_folder):
    """Take dict of links and download them in folder 'PDF'.

    Args:
        country (str): name of country.
        link (str): link to PDF corresponding to country.
        path_to_folder (str): path to folder for saving PDF.
    """

    file_name = country + ".pdf"
    file_path = os.path.join(path_to_folder, file_name)

    # downloading files using HTMLsession
    with open(file_path, "wb") as pdf_file:
        pdf_as_page = HTMLSession().get(link)
        pdf_file.write(pdf_as_page.content)
