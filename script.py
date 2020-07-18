import sqlite3
import ast
import os

from scripts.pdf_download import pdf_link_scraper, download_pdf
from scripts.pdf_to_text_script import pdf_scraper
from scripts.prepare_data import preparing_db_objects


def create_db(db_file):
    """ create SQLite database and adds 7 prepared tables there"""

    with sqlite3.connect(db_file) as conn:

        c = conn.cursor()

        c.execute(
            """CREATE TABLE IF NOT EXISTS 'Country overview' (
                    country_id text,
                    'Chief of State' text,
                    'Head of Government' text,
                    'Government Type' text,
                    Capital text,
                    Legislature text,
                    Judiciary text,
                    'Ambassador to US' text,
                    'US Ambassador' text,
                    'Area total (sq km)' real,
                    'Area land (sq km)' real,
                    'Area water (sq km)' real,
                    Climate text,
                    'Economic Overview' text,
                    'GDP (Purchasing Power Parity)' integer,
                    'GDP year of update' integer,
                    'GDP per capita (Purchasing Power Parity)' text,
                    'GDP per capita year of update' integer,
                    Exports integer,
                    'Exports year of update' integer,
                    Imports integer,
                    'Imports year of update' integer,
                    Population integer,
                    'Population year of update' text,
                    'Population growth % per year' real,
                    'Population growth year of update' integer,
                    'Rate of urbanization 2015-2020' real,
                    'Urban population %' real,
                    'Urban population year of update' integer,
                    'Literacy % pupulation' real,
                    'Literacy year of update' integer,
                    'Last update of data' text,
                    primary key(country_id))
                    """
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS 'Natural resources' (
                    country_id text,
                    Resource text,
                    primary key(country_id,Resource))
                    """
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS Religion (
                    country_id text,
                    Religion text,
                    "population %" real,
                    'Year of data' integer,
                    primary key(country_id,Religion))
                    """
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS Language (
                    country_id text,
                    Language text,
                    "Population %" real,
                    Official text,
                    'Year of data' integer,
                    primary key(country_id,Language,Official))
                    """
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS Ethnicity (
                    country_id text,
                    Ethnicity text,
                    "population %" real,
                    'Year of data' integer,
                    primary key(country_id,Ethnicity))
                    """
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS 'Export partners' (
                    country_id text,
                    'Export partners' text,
                    "Export %" real,
                    'Year of data' integer,
                    primary key(country_id,'Export partners'))
                    """
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS 'Import partners' (
                    country_id text,
                    'Import partners' text,
                    "Import %" real,
                    'Year of data' integer,
                    primary key(country_id,'Import partners'))
                    """
        )


def write_to_db(db_file, table, db_obj):
    """Writer function, that takes DB_file, tables and
    prepared db objects and writes content as column values,
    depending of the table and db object it uses different
    ways to write"""

    with conn:
        for country in db_obj:
            if type(db_obj[country]) == dict:
                db_val = db_obj[country].values()
                db_val = str(tuple(db_val)).replace("'NULL'", "NULL")
                c.execute(f"INSERT INTO '{table}' values {db_val}")

            else:
                for item in db_obj[country]:
                    if type(item) == str:
                        db_val = [country] + [item]
                    else:
                        db_val = [country] + item

                    db_val = str(tuple(db_val)).replace("'NULL'", "NULL")
                    c.execute(f"INSERT INTO '{table}' values {db_val}")


links = pdf_link_scraper()  # make dictionary of links for downloading PDF
print("Donwloading PDFs...")
download_pdf(links)  # download PDF to folder "pdf"
print("Starting scraping PDFs for text...")
obj = pdf_scraper("pdf")  # parse pdf, return dict object with text sorted by fields

db_objects = preparing_db_objects(
    obj
)  # preparing 7 objects, that we use to create 7 tables
print("Finished preparing objects")

# name of tables
tables = [
    "Country overview",
    "Natural resources",
    "Religion",
    "Language",
    "Ethnicity",
    "Export partners",
    "Import partners",
]

# create folder for "DB"
if not os.path.exists("db"):
    os.mkdir("db")

# DB name
db_file = "db/summaries.db"

create_db(db_file)  # creates DB with 7 tables
print("Finished creating db")

# open connection to DB
conn = sqlite3.connect(db_file)
c = conn.cursor()

# pair 7 db objects with 7 table names and pass their content to DB
for i in zip(tables, db_objects):
    write_to_db(db_file, i[0], i[1])

# close connection to db
conn.close()
print("Finished filling up db")

