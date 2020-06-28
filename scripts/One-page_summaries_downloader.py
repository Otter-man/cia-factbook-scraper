from requests_html import HTML, HTMLSession
import wget
import os


def pdf_link_scraper():
    """this function scrapes CIA web-page with
    one-page summaries of the countries
    """

    links = {}  # creating empty dictionary
    cia_page = "https://www.cia.gov/library/publications/resources/the-world-factbook/docs/one_page_summaries.html"

    session = HTMLSession()
    source = session.get(cia_page).html  # downloading link as html

    country_data = source.find(
        "div.country-name"
    )  # finding all blocks containing country name and link to onepage summary

    for country in country_data:
        links[country.text] = list(country.absolute_links)[
            0
        ]  # add coyntry name as a key and link to pdf summary as a value to dictionary

    return links  # returning resulting dictionary


def download_pdf(links):
    """this function takes list of links, generated by pdf_link_scraper()
    creates folder "pdf" and downloads one-page summaries for each country
    """

    if not os.path.exists("pdf"):  # check if folder "pdf" exists
        os.mkdir("pdf")  # creating the folder if not

    for (
        country,
        link,
    ) in links.items():  # we take dictionary resulting from the previous function
        file_name = (
            country + ".pdf"
        )  # create filename for a pdf using keys from dictionary
        file_path = os.path.join("pdf", file_name)  # create path for downloading pdf
        wget.download(
            link, file_path
        )  # download pdf using links from values in dictionary


links = pdf_link_scraper()
download_pdf(links)

print("Finished downloading all PDFs")
