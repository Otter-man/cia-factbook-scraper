"""This module contains all classes used in the project."""


class Country:
    '''Class for storing data for each country in readable form.'''

    def __init__(self, name, natural_resources, chief_of_state,
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
        self.natural_resources = natural_resources
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
