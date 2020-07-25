# CIA factbook one page summaries scraping tool

Script to scrape PDF with one-page summaries of different countries from CIA website.

The same data is availible on CIA webpage in more convinient form, but I wanted to exercise in working with PDF scraping and working with losely formated text.
Script downloads PDF to local folder, scrapes text from it and pass it as a formated data into sqlite DB.
Example of the DB is in the /db folder.

CIA-webpage used as a source for PDF availible here:
https://www.cia.gov/library/publications/resources/the-world-factbook/docs/one_page_summaries.html


## How to use the script

The script is written in **Python 3.8.2**

Install required libraries by runing ```pip install -r requirements.txt```

Then run ```python3 script.py```

Script will donwload PDF to folder named `pdf` and will create sqlite DB `summaries.db` in the folder `db`.
