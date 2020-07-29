"""This module contains all classes used in the project."""


class CountryGeneral:
    """Class for storing general info for each country."""

    def __init__(self, name, chief_of_state,
                 head_of_government, government_type, capital,
                 legislature, judiciary, ambassador_to_us,
                 us_ambassador, area_total, area_land, area_water,
                 climate, economic_overview, gdp_ppp, gdp_last_update,
                 gdp_per_capita, gdp_per_capita_last_update,
                 exports_size, exports_last_update, imports_size,
                 imports_last_update, population, population_last_update,
                 population_growth, population_growth_last_update,
                 rate_of_urbanization, urban_population,
                 urban_population_last_update, literacy,
                 literacy_last_update, last_update_of_pdf):
        #: str: name of the country
        self.name = name

        #: str: name of current Chief of State
        self.chief_of_state = chief_of_state

        #: str: name of current Head of Government
        self.head_of_government = head_of_government

        #: str: description of government type
        self.government_type = government_type

        #: str: name of the capital of the country
        self.capital = capital

        #: str: type of legislature
        self.legislature = legislature

        #: str: judiciary system description
        self.judiciary = judiciary

        #: str: name of the ambassador to US
        self.ambassador_to_us = ambassador_to_us

        #: str: name of the US ambassador to the country
        self.us_ambassador = us_ambassador

        #: int: total area of the country, sq km
        self.area_total = area_total

        #: int: land area of the country, sq km
        self.area_land = area_land

        #: int: water area of the country, sq km
        self.area_water = area_water

        #: str: description of climate of the country
        self.climate = climate

        #: str: short economic overview
        self.economic_overview = economic_overview

        #: int: GDP (purchasing power parity) size, $
        self.gdp_ppp = gdp_ppp

        #: int: year of the last update of GDP (ppp) data
        self.gdp_last_update = gdp_last_update

        #: int: GDP per capita (PPP) size, $
        self.gdp_per_capita = gdp_per_capita

        #: int: year of the last update of GDP per capita data
        self.gdp_per_capita_last_update = gdp_per_capita_last_update

        #: int: exports size, $
        self.exports_size = exports_size

        #: int: year of the last update of exports data
        self.exports_last_update = exports_last_update

        #: imports size, $
        self.imports_size = imports_size

        #: int: year of the last update of imports data
        self.imports_last_update = imports_last_update

        #: int: size of population
        self.population = population

        #: str: year and month of the last update of population data
        self.population_last_update = population_last_update

        #: int: population growth, %
        self.population_growth = population_growth

        #: int: year of the last update of population growth data
        self.population_growth_last_update = population_growth_last_update

        #: int: rate of urbanization, %
        self.rate_of_urbanization = rate_of_urbanization

        #: int: size of urban population in country, %
        self.urban_population = urban_population

        #: int: year of the last update of urban population data
        self.urban_population_last_update = urban_population_last_update

        #: int: literacy among population, %
        self.literacy = literacy

        #: int: last update of literacy data
        self.literacy_last_update = literacy_last_update

        #: str: year and month of the last update of data in PDF
        self.last_update_of_pdf = last_update_of_pdf


class CountryNaturalResources:
    """Class for storing data for natural resources in countries."""

    def __init__(self, country, resource):
        #: str: name of the country
        self.country = country

        #: str: natural resource name
        self.resource = resource


class CountryLanguage:
    """Class for storing data for languages in a country."""

    def __init__(self, country_name, language, percent, officiality, year):
        #: str: name of the country
        self.country_name = country_name
        #: str: language name
        self.language = language
        #: int: language in population, %
        self.percent = percent
        #: bool: language official status in country or it's parts
        self.officiality = officiality
        #: int: year of the last update of language data
        self.year = year


class CountryReligion:
    """Class for storing data for religions in a country."""

    def __init__(self, country_name, religion, percent, year):
        #: str: name of the country
        self.country_name = country_name
        #: str: religion name
        self.religion = religion
        #: int: religion in population, %
        self.percent = percent
        #: int: year of the last update of religion data
        self.year = year


class CountryEthnicity:
    """Class for storing ethnicity data of a country."""

    def __init__(self, country_name, ethnicity, percent, year):
        #: str: name of the country
        self.country_name = country_name
        #: str: ethnicity name
        self.ethnicity = ethnicity
        #: int: ethnicity in population, %
        self.percent = percent
        #: int: year of the last update of ethnicity data.
        self.year = year


class CountryImportPartners:
    """Class for storing data for import partnerships of a country."""

    def __init__(self, country_name, import_partner, import_percent,
                 import_year):
        #: str: name of the country
        self.country_name = country_name
        #: str: name of partner country
        self.import_partner = import_partner
        #: int: share of import with partner, %
        self.import_percent = import_percent
        #: int: year of the last update of imports data.
        self.import_year = import_year


class CountryExportPartners:
    """Class for storing data for export partnerships of a country."""

    def __init__(self, country_name, export_partner, export_percent,
                 export_year):
        #: str: name of the country
        self.country_name = country_name
        #: str: name of partner country
        self.export_partner = export_partner
        #: int: share of export with partner, %
        self.export_percent = export_percent
        #: int: year of the last update of exports data.
        self.export_year = export_year
