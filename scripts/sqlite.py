"""This module will contain all function for working with sqlite DB."""
import sqlite3


def create_db(dbfile):
    """Create sqlite DB with 7 tables.

    Args:
        dbfile (str): path to DB file.
    """

    with sqlite3.connect(dbfile) as connection:

        cur = connection.cursor()

        cur.execute(
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
                    'Literacy % population' real,
                    'Literacy year of update' integer,
                    'Last update of data' text,
                    primary key(country_id))
                    """
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS 'Natural resources' (
                    country_id text,
                    Resource text,
                    primary key(country_id,Resource))
                    """
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS Religion (
                    country_id text,
                    Religion text,
                    "population %" real,
                    'Year of data' integer,
                    primary key(country_id,Religion))
                    """
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS Language (
                    country_id text,
                    Language text,
                    "Population %" real,
                    Official text,
                    'Year of data' integer,
                    primary key(country_id,Language,Official))
                    """
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS Ethnicity (
                    country_id text,
                    Ethnicity text,
                    "population %" real,
                    'Year of data' integer,
                    primary key(country_id,Ethnicity))
                    """
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS 'Export partners' (
                    country_id text,
                    'Export partners' text,
                    "Export %" real,
                    'Year of data' integer,
                    primary key(country_id,'Export partners'))
                    """
        )

        cur.execute(
            """CREATE TABLE IF NOT EXISTS 'Import partners' (
                    country_id text,
                    'Import partners' text,
                    "Import %" real,
                    'Year of data' integer,
                    primary key(country_id,'Import partners'))
                    """
        )


def connect_to_db(dbfile):
    """Create connection to sqlite DB.

    Args:
        dbfile (str): path to sqlite DB.

    Returns:
        Connection object.
    """
    conn = sqlite3.connect(dbfile)
    return conn


def write_to_db(executor, table, instances_container):
    """Write data to sqlite DB.

    Args:
        executor (sqlite3.Cursor): sqlite3 cursor object.
        table (str): table name.
        instances_container (list): list, containing data as class
            instances.
        """

    for item in instances_container:
        placeholder = tuple(':'+row for row in vars(item))
        placeholder = str(placeholder).replace("\'", "")
        executor.execute(
            f"INSERT INTO '{table}' values {placeholder}", vars(item))
