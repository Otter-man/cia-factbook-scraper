"""This module contains all classes used in the project."""


class CountryGeneral:
    '''Class with general info for each country.'''

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

        self.name = name
        self.chief_of_state = chief_of_state
        self.head_of_government = head_of_government
        self.government_type = government_type
        self.capital = capital
        self.legislature = legislature
        self.judiciary = judiciary
        self.ambassador_to_us = ambassador_to_us
        self.us_ambassador = us_ambassador
        self.area_total = area_total
        self.area_land = area_land
        self.area_water = area_water
        self.climate = climate
        self.economic_overview = economic_overview
        self.gdp_ppp = gdp_ppp
        self.gdp_last_update = gdp_last_update
        self.gdp_per_capita = gdp_per_capita
        self.gdp_per_capita_last_update = gdp_per_capita_last_update
        self.exports_size = exports_size
        self.exports_last_update = exports_last_update
        self.imports_size = imports_size
        self.imports_last_update = imports_last_update
        self.population = population
        self.population_last_update = population_last_update
        self.population_growth = population_growth
        self.population_growth_last_update = population_growth_last_update
        self.rate_of_urbanization = rate_of_urbanization
        self.urban_population = urban_population
        self.urban_population_last_update = urban_population_last_update
        self.literacy = literacy
        self.literacy_last_update = literacy_last_update
        self.last_update_of_pdf = last_update_of_pdf


class CountryNaturalResources:
    def __init__(self, country, resource):
        self.country = country
        self.resource = resource


class CountryLanguage:
    def __init__(self, country_name, language, percent, officiality, year):
        self.country_name = country_name
        self.language = language
        self.percent = percent
        self.officiality = officiality
        self.year = year


class CountryReligion:
    def __init__(self, country_name, religion, percent, year):
        self.country_name = country_name
        self.religion = religion
        self.percent = percent
        self.year = year


class CountryEthnicity:
    def __init__(self, country_name, ethnicity, percent, year):
        self.country_name = country_name
        self.ethnicity = ethnicity
        self.percent = percent
        self.year = year


class CountryImportPartners:
    def __init__(self, country_name, import_partner, import_percent,
                 import_year):
        self.country_name = country_name
        self.import_partner = import_partner
        self.import_percent = import_percent
        self.import_year = import_year


class CountryExportPartners:
    def __init__(self, country_name, export_partner, export_percent,
                 export_year):
        self.country_name = country_name
        self.export_partner = export_partner
        self.export_percent = export_percent
        self.export_year = export_year
