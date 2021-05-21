# This project is archived due to [CIA-webpage redisign in 2021](https://www.latimes.com/entertainment-arts/story/2021-01-08/the-cia-redesigns-its-logo-and-other-reasons-why-the-governments-graphic-design-needs-work)
For the first time in many years CIA webpage was updated and this scraper was made obsolete. You can access PDF-files at [CIA new page](https://www.cia.gov/the-world-factbook/references/one-page-country-summaries/) and since PDF a still the same the scraper can be updated to work with them.
But for now this project is archived.

# CIA factbook one page summaries scraping tool

Script to scrape PDF with one-page summaries of different countries from CIA website.

The same data is available on CIA webpage in more convenient form, but I wanted to exercise in working with PDF scraping and working with loosely formatted text.
Script downloads PDF to local folder, scrapes text from it and pass it as a formatted data into sqlite DB.
Example of the DB is in the ```data``` folder.

CIA-webpage used as a source for PDF available here:
https://www.cia.gov/library/publications/resources/the-world-factbook/docs/one_page_summaries.html


## How to use the script

The script is written in **Python 3.8.2**

Install required libraries by running ```pip install -r requirements.txt```

Then run ```python runner.py```

Script will download PDF to folder named `pdf` and will create sqlite DB `summaries.db` in the folder `data`.


