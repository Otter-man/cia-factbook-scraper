"""Module for scraping CIA page for links and downloading PDF files."""
import os
from requests_html import HTMLSession, AsyncHTMLSession


def scrape_pdf_links(cia_page):
    """Scrape CIA page for PDF links and return them as dict.

    Args:
        cia_page (str): link to the page, containing PDF files.

    Returns:
        List of lists. Each nested list contains 4 elements, each element
        is a list made of two str - country name and link to PDF file.
    """

    link_blocks = []
    links_temp = []

    session = HTMLSession()
    source = session.get(cia_page).html  # downloading page as html

    country_data = source.find("div.country-name")

    count = 0
    for country in country_data:
        links_temp.append([country.text, list(country.absolute_links)[0]])
        count += 1
        if count % 4 == 0:
            link_blocks.append(links_temp)
            links_temp = []
        elif count % 4 != 0 and count == len(list(country_data)):
            link_blocks.append(links_temp)

    return link_blocks


def download_pdf_single(country, link, path_to_folder):
    """Take country and link and download single PDF.

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


def download_pdf_multi(block, path_to_folder):
    """Take list of links and download them five files at a time.

    Args:
        block (list): contains 5 elements, each element is a list made of
            two str - country name and link to corresponding PDF file.
        path_to_folder (str): path to folder for saving PDF.
    """
    async_ses = AsyncHTMLSession()

    link1 = block[0][1]
    link2 = block[1][1]
    link3 = block[2][1]
    link4 = block[3][1]

    async def downloader1():
        pdf_as_page = await async_ses.get(link1)
        return pdf_as_page

    async def downloader2():
        pdf_as_page = await async_ses.get(link2)
        return pdf_as_page

    async def downloader3():
        pdf_as_page = await async_ses.get(link3)
        return pdf_as_page

    async def downloader4():
        pdf_as_page = await async_ses.get(link4)
        return pdf_as_page

    pages_return = async_ses.run(
        downloader1, downloader2, downloader3, downloader4, )

    counter = 0
    for page in pages_return:

        file_name = [i[0] for i in block if page.url == i[1]]
        file_name = file_name[0] + ".pdf"

        file_path = os.path.join(path_to_folder, file_name)

        with open(file_path, "wb") as pdf_file:
            pdf_file.write(page.content)
        counter += 1
