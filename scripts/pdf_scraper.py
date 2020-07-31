"""Module for converting PDF to text and scraping data from it."""
import os
import re
from pdfminer import high_level, layout
import scripts.classes as cl


def create_index(fields, text_split, country_id):
    """Return dictionary with index for every field name.

    Args:
        fields (list of str): list of field names.
        text_split (list of str): text split to list, where every word
            is an element of list.
        country_id (str): name of the country, used to handle minor
            errors in text while indexing specific countries.

    Returns:
        dict: dictionary, with field name as a key and list as a value.
        Each list contains two int. First int - index of a first word of
        a field name in text as list, second int is an index +1 of a last
        word of a field name in text as list.

    Examples:
        >>>print(create_index(["Climate", "Natural Resources"],
        ["Climate", "and", "Natural", "Resources"], "Russia"))
        {"Climate":[0,1], "Natural Resources":[2,4]}
    """
    index_dict = {}

    # deleting unnecessary headers in text_split
    del text_split[text_split.index("GOVERNMENT")]
    del text_split[text_split.index("GEOGRAPHY")]

    pep_soc = [
        (i, i + 3)
        for i in range(len(text_split))
        if text_split[i: i + 3] == ["PEOPLE", "&", "SOCIETY"]
    ]
    del text_split[pep_soc[0][0]: pep_soc[0][1]]

    if "'Economic', 'Overview'" in str(text_split):
        del text_split[text_split.index("ECONOMY")]

    for item in fields:

        item_list = item.split()

        # this part handles some exception for some pages that contain
        # errors in naming
        if country_id == "GERMANY" and item == "GDP (Purchasing Power Parity)":
            item_list = "GDP Purchasing Power Parity)".split()
        elif country_id == "MOLDOVA" and item == "US Ambassador":
            item_list = ["Ambassador"]
        elif country_id == "IRAQ" and item == "Area":
            item_list = ["Area,"]
        elif country_id == "IRAQ" and item == "Urbanization":
            item_list = ["2003Urbanization"]
        elif (country_id in ("TURKMENISTAN", "MAURITIUS")
              and item == "Economic Overview"):
            item_list = ["ECONOMY"]

        # This part finds indexes for every field name.
        # While searching, indexes stored inside a tuple inside a list.
        # In most cases there is only one tuple for each field name, but
        # there are some exceptions.
        index = [
            (i, i + len(item_list))
            for i in range(len(text_split))
            if text_split[i: i + len(item_list)] == item_list
        ]

        # If there are more than one occurrence of the field name in text
        # list will have more than one tuple.
        # When this happens we use first tuple as index, except for the
        # field "US Ambassador" where we always use second tuple.
        if len(index) > 1 and item == "US Ambassador":
            index = list(index[1])
        elif len(index) > 0:
            index = list(index[0])

        index_dict[item] = index

    return index_dict


def convert_big_str_numbers(big_num):
    """Convert big number written with numbers and words to int.

    Args:
        big_num (str): number, written with numbers and words.

    Returns:
        int: same number as an int.

    Examples:
        >>>print(convert_big_str_numbers('101.11 billions'))
        101110000000
    """
    big_num = big_num.replace("$", "")

    big_num = big_num.split(" ")

    if "million" in str(big_num):
        zero = "000000"
    elif "billion" in str(big_num):
        zero = "000000000"
    elif "trillion" in str(big_num):
        zero = "000000000000"
    else:
        zero = "000000000"

    big_num = big_num[0].split(".")
    try:
        big_num = f"{big_num[0]}{big_num[1]}{zero[len(big_num[1]):]}"
    except IndexError:
        big_num = f"{big_num[0]}{zero}"

    return int(big_num)


def split_percents(field_name, a_list):
    """Split each element in a list of str to str and float/None.

    Takes a list of str, in each element searches for number and coverts
    it to a list of two elements - a string and a number as a float, if
    number is found. If number is not found, second element is a None.

    Args:
        field_name (str): name of the field for handling special cases.
        a_list (list of str): data for the field.

    Returns:
        List of lists, each nested list has two elements: str and float.
        If field_name is "Language" each nested list also contains a
        bool. Bool shows if there is a word "Official" in a str.

    Examples:
        >>>print(split_percents("Language",[Russian 65% (Official),
        English 3.7%]))
        [['Russian', 65.0, True], ["English", 3.7, False]]
        >>>print(split_percents("Religion", [Muslim 97.1%, other]))
        [['Muslim', 97.1],['other', None]]
        >>>print(split_percents("Imports",['Brazil 31.9%',
        'Argentina 15.9%', 'Chile 6.9%']))
        [['Brazil', 31.9], ['Argentina', 15.9], ['Chile', 6.9]]


    """
    return_list = []
    language_list = []
    if a_list is None and field_name == "Language":
        return [[None, None, False]]

    if a_list is None:
        return [[None, None]]

    for element in a_list:

        if element[:4] == "and ":
            element = element[4:]
        elif element[:5] == "also ":
            element = element[5:]
        elif element[:9] == "but also ":
            element = element[9:]
        elif element[:11] == "there is a ":
            element = element[11:]

        if field_name == "Language":

            element = element.replace(";", ",")

            officiality = "official" in element

            element = element.replace(" (official)", "")

        element = element.strip()

        element_listed = element.split()

        index = [element_listed.index(i) for i in element_listed if "%" in i]

        try:
            index = index[0]

            if field_name == "Religion":
                if (not element_listed[index - 1].isalpha()
                        and "non-" not in element_listed[index - 1]
                        and "/" not in element_listed[index - 1]):

                    percentage = "".join(element_listed[index - 1: index + 1])
                    parted = " ".join(element_listed[: index - 1])
                else:
                    percentage = element_listed[index]
                    parted = " ".join(element_listed[:index])

            else:
                percentage = element_listed[index]
                parted = " ".join(element_listed[:index])

        except IndexError:
            percentage = None
            parted = " ".join(element_listed)

        try:
            percentage = percentage.replace("%", "")
            percentage = float(percentage)
        except (AttributeError, ValueError):
            pass

        # for Language we build two identical lists, since we need value
        # country+language to be unique and we need to remove duplicates

        if field_name == "Language":
            return_list.append([parted, percentage, officiality])
            language_list.append([parted, percentage, officiality])
        else:
            return_list.append([parted, percentage])

    # we remove duplicate languages from main list, by turning it to
    # dictionary with the language + percent as a key
    if field_name == "Language":
        return_list = list(dict((x[0] + str(x[1]), x)
                                for x in return_list).values())

        # To check that the language official status isn't lost, we
        # compare elements from the second list, wich we didn't modify.
        # If the language with official status was removed as a duplicate
        # we replace it in the main list
        for item in language_list:
            if item not in return_list and item[2] == "Yes":
                item_index = return_list.index(item[:2] + ["No"])
                return_list[item_index] = item

    for item in return_list:
        if item[0] == "":
            del return_list[return_list.index(item)]

    return return_list


def format_field_data(field_name):
    """Take field name and return appropriate function to format data.

    Args:
        field_name (str): name of the current field.

    Returns:
        Another function.
    """

    def literacy_field(field_data):
        """Take data as str and return it as  list with float and int.

        Takes literacy data and extracts two data points -  year of the
        last update of data and share of literate population.

        Args:
            field_data (str): data for the current field.

        Returns:
            list: contains two elements, int and float.

        Example:
            >>>print(literacy_field('94.7% (2018)')
            [2018, 94.7]
        """
        if field_data is None:
            lit_year, lit_percent = field_data, field_data
        else:
            pattern = re.compile(r"([0-9\.]{0,4}%).*\((20..)")
            match = re.search(pattern, field_data)
            lit_year = match[2]
            lit_percent = match[1]

        try:
            lit_percent = float(lit_percent.replace("%", ""))
            lit_year = int(lit_year)

        except (ValueError, AttributeError):
            pass

        return [lit_year, lit_percent]

    def urbanization_field(field_data):
        """Take data as str and return it as list with int and float.

        Takes urbanization data and extracts three data points - year of
        the last update of data, share of urban population and annual
        rate of change of urbanization for 2015-2020.

        Args:
            field_data (str): data for the current field.

        Returns:
            list: contains three elements, int and two floats.

        Example:
            >>>print(urbanization_field('urban population: 62.2% of total
            population (2020)rate of urbanization: 1.71% annual rate of
            change (2015-20 est.)'))
            [2020, 62.2, 1.71]
        """
        pattern = re.compile(
            r"\s?([0-9\. ]{1,5}\%).*\((20..)\)?.*urbanization: ([\-0-9\. ]{1,5}\%)"
        )
        match = re.search(pattern, str(field_data))

        if field_data is None:
            rate_urb, urb_pop_year, urb_pop = field_data, field_data, field_data
        else:
            if match[3][0] != ".":
                rate_urb = match[3].replace(" ", "")
            else:
                rate_urb = "0" + match[3].replace(" ", "")

            urb_pop = match[1].replace(" ", "")
            urb_pop_year = match[2]
        try:
            rate_urb = float(rate_urb[:-1])
            urb_pop = float(urb_pop[:-1])
            urb_pop_year = int(urb_pop_year)
        except (ValueError, TypeError):
            pass

        return [urb_pop_year, urb_pop, rate_urb]

    def population_growth_field(field_data):
        """Take data as str and return it as a list with int and float.

        Takes population growth data and extracts two data points - year
        of the last update of data and population growth %

        Args:
            field_data (str): data for the current field.

        Returns:
            list: contains two elements, int and float.

        Example:
            >>>print(population_growth_field('1.16% (2020 est.)'))
            [2020, 1.16]
        """
        pattern = re.compile(r"([\-\.0-9 ]*\%).*(20\d\d)")
        match = re.search(pattern, str(field_data))

        if field_data is None:
            pop_grow_year, pop_grow = field_data, field_data
        else:
            pop_grow_year = match[2]
            if match[1][0] == ".":
                pop_grow = "0" + match[1].replace(" ", "")
            elif match[1][:2] == "-.":
                pop_grow = "-0" + match[1].split("-.0", 1)[1]
            else:
                pop_grow = match[1].replace(" ", "")
        try:
            pop_grow = float(pop_grow[:-1])
            pop_grow_year = int(pop_grow_year)
        except (ValueError, TypeError):
            pass
        return [pop_grow_year, pop_grow]

    def population_field(country, field_data):
        """Take data as str and return it as list with str and int.

        Takes country name and population data and extracts two data
        points - year of the last update of data and population size

        Args:
            country (str): country name, used for handling exceptions.
            field_data (str): data for the current field.

        Returns:
            list: contains two elements, str and int.

        Example:
            >>>print(population_field('7.2 million (July 2020 est.)'))
            ['July 2020', 7200000]
        """
        if country == "FRENCH SOUTHERN AND ANTARCTIC LANDS":
            pop_year = None
            population = "0"

        else:
            if "million" in str(field_data) or "billion" in str(field_data):

                pattern = re.compile(
                    r"([0-9\.,]*)\s(million|billion).*\((.*)est"
                )
                match = re.search(pattern, field_data)

                population = " ".join([match[1], match[2]])

                population = convert_big_str_numbers(population)

                pop_year = match[3].strip()

            else:
                pattern = re.compile(r"([0-9\,]*) \((.*) est")
                match = re.search(pattern, field_data)

                population = match[1].replace(",", "")

                pop_year = match[2]
                try:
                    pop_year = pop_year.strip()
                except AttributeError:
                    pass
        return [pop_year, int(population)]

    def imports_exports_field(country, field_data, field_name):
        """Take imports|exports data and return it as a tuple.

        This function takes data from imports|exports field and extracts
        two lists from it.

        Args:
            country (str): name of country for handling exceptions.
            field_data (str): data for the current field.
            field_name (str): name of the current field for handling
                exceptions.

        Returns:
            Tuple containing two lists.

            First list has two elements - year of the last update of data
            as int and size of activity as int.

            Second list contains lists as elements. Each nested list has
            four elements - country name as str, name of partner as str,
            share of total activity for this partner as float, year of
            the last update of data as int.

        Example:
            >>>print(imports_exports_field('ARMENIA', '$2.36 billion
            (2017 est.)partners: Russia 24.2%, Bulgaria 12.8%,
            Switzerland 12% (2017)', "Exports"))

            ([2017, 2360000000], [['ARMENIA', 'Russia', 24.2, 2017],
            ['ARMENIA', 'Bulgaria', 12.8, 2017],
            ['ARMENIA', 'Switzerland', 12.0, 2017]])
        """
        if field_data is None:
            activity_size, partners, act_year = (
                field_data,
                field_data,
                field_data,
            )

        else:
            pattern = re.compile(
                r"(\$[0-9\.]*)\s(billion|million|trillion)\s.(\d\d\d\d)"
            )
            match = re.search(pattern, field_data)

            if field_name == "Imports" and country == "ETHIOPIA":
                partners = field_data.split(") ")[1]

            else:
                # this block handles countries which don't have
                # import|export partners written
                try:
                    partners = field_data.split(
                        "partners")[1].replace(": ", "")
                except IndexError:
                    partners = None

            try:
                act_year = match[3]
                activity_size = f"{match[1]} {match[2]}"
            # exception handles some country with error in formating
            except TypeError:
                act_year = field_data.split("(")[1][:5]
                activity_size = "".join(field_data.split()[:2])

        if act_year is not None:
            act_year = int(act_year.strip())

        if activity_size is not None:
            activity_size = convert_big_str_numbers(activity_size)

        if partners is not None and partners != 'N/A':
            pattern = re.compile(r"\s\(.*?\)")
            match = re.search(pattern, partners)

            # we clean unnecessary info with year, which
            # duplicates imports|export year of update
            if field_name == "Imports" and country == "SUDAN":
                pass
            else:
                partners = partners.replace(match[0], "")

            if field_name == "Imports" and country == "FRANCE":
                partners = partners.replace("Belgium", "Belgium ")

            # returning , that were skipped in the text
            partners = partners.replace("% ", "%,")

            partners = partners.split(",")

            # fixing forgotten % symbols
            for item in partners:
                ind = partners.index(item)
                item = item.strip()
                if item != "" and item is not None and item[-1] != "%":
                    item = item + "%"
                partners[ind] = item

            # we create content for import|exports partners dictionary
            # with percent_taker function
            partners_listed = split_percents(field_name, partners)
        else:
            partners_listed = [[None, None]]

        for partner in partners_listed:
            partner[:0] = [country]
            partner.append(act_year)

        return [act_year, activity_size], partners_listed

    def area_field(country, field_data):
        """Take data for area as str and return it as a list of float.

        Args:
            country (str): country name, used for handling exceptions.
            field_data (str): data about current field.

        Returns:
            List of float.

        Example:
            >>>print(area_field('RUSSIA', 'Total: 17,098,242 sq km Land:
            16,377,742 sq km Water: 720,500 sq km'))
            [720500.0, 16377742.0, 17098242.0]
        """
        if country == "FRENCH SOUTHERN AND ANTARCTIC LANDS":
            total, land, water = None, None, None

        elif country == "GREENLAND":
            total = field_data.lower().split("total: ")
            total = total[1][: total[1].index(
                " sq km")].replace(",", "")

            land = None
            water = None

        else:
            total = field_data.lower().split("total: ")
            total = total[1][: total[1].index(
                " sq km")].replace(",", "")

            land = field_data.lower().split("land")
            land = land[1][: land[1].index(" sq km")].replace(",", "")
            land = land.replace(":", "").strip()
            land = land.replace("-", "")

            if country == "SAUDI ARABIA":
                total = convert_big_str_numbers(total)
                land = convert_big_str_numbers(land)

            try:
                water = field_data.lower().split("water: ")
                water = water[1][: water[1].index(
                    " sq km")].replace(",", "")
            except ValueError:
                water = "0"

        try:
            total = float(total)
            land = float(land)
            water = float(water)
        except TypeError:
            pass

        return [water, land, total]

    def gdp_ppp_field(field_data):
        """Take data as str and return it as a list of int.

        Args:
            field_data (str): data for the current field.

        Returns:
            List of int.

        Example:
            >>>print(gdp_ppp_field('$20.44 billion (2017 est.)'))
            [2017, 20440000000]
        """
        pattern = re.compile(
            r"(\$[0-9\.]+)\s(bi+llion|million|trillion)\s\((20[0-9]{2})"
        )
        match = re.search(pattern, str(field_data))

        try:
            gdp = f"{match[1]} {match[2].replace('ii','i')}"
            gdp_year = match[3]
        except TypeError:
            gdp, gdp_year = None, None

        if gdp_year is not None:
            gdp_year = int(gdp_year)

        if gdp is not None:
            gdp = convert_big_str_numbers(gdp)

        return [gdp_year, gdp]

    def per_capita_field(field_data):
        """Take data as str and return it as a list of int.

        Args:
            field_data (str): data for the current field.

        Returns:
            List of int.

        Example:
            >>>print(per_capita_field('$15,100 (2017 est.)'))
            [2017, 15100]
        """
        try:
            per_capita = field_data.split(" (")[0]
            per_capita_year = field_data.split(" (")[1][:5]
            per_capita_year = per_capita_year.strip().replace(")", "")
        except AttributeError:
            per_capita, per_capita_year = None, None

        if per_capita is not None and per_capita_year is not None:
            per_capita = int(per_capita[1:].replace(",", ""))
            per_capita_year = int(per_capita_year)

        return [per_capita_year, per_capita]

    def natural_resources_field(country, field_data):
        """Take data as str and return it as a list of lists.

        Args:
            country (str): country name forming return.
            field_data (str): data for the current field.

        Returns:
            List of lists.

            Each nested list contains two elements - country name and
            resource name, both as str.

        Example:
            >>>print(natural_resources_field('URUGUAY', hydropower,
            minor minerals'))
            [['URUGUAY', 'hydropower'], ['URUGUAY', 'minor minerals']]
        """
        resource_list = field_data.split("note")[0]
        resource_list = [resource.strip()
                         for resource in resource_list.split(",")]

        temp_resources = []

        for resource in resource_list:

            if resource[:4] == "and ":
                resource = resource[4:]

            if ";" in resource:
                temp_resources.extend(resource.split(";"))
            elif "(" in resource:
                temp_resources.append(resource[: resource.find(" (")])
            else:
                temp_resources.append(resource)

        resource_list = [[country, item.strip()]
                         for item in temp_resources if item != '']

        return resource_list

    def religion_field(country, field_data, field_name):
        """Take data as str and return it as list of lists.

        Args:
            country (str): for handling exceptions and forming return.
            field_data (str): data for current field.
            field_name (str): for passing to split_percents() func.

        Return:
            List of lists.

            Each nested list contains four elements: country name as str,
            religion name as str, share of population for religion as
            float and year of the last update of data as int.

        Example:
            >>>print(religion_field('CHAD', 'Muslim 52%, Christian 44%
            (2014-15 est.)', 'Religion'))
            [['CHAD', 'Muslim', 52.0, 2014],
            ['CHAD', 'Christian', 44.0, 2014]]
        """
        try:
            religion_list = field_data.split("note")[0]
        except AttributeError:
            religion_list = field_data

        pattern = re.compile(r"\d\d\d\d")
        match = re.search(pattern, str(religion_list))

        try:
            year = int(match[0].strip())
        except TypeError:
            year = None

        # handles specific formating for ukraine
        if country == "UKRAINE":
            religion_list = re.sub(r"\(.*?\)\)", "", religion_list)
        # cleans code of things in parenthesis
        if religion_list is not None:
            religion_list = re.sub(r"\(.*?\)1?", "", religion_list)

            religion_list = [
                relig.strip() for relig in religion_list.split(",")
            ]

        religion_list = split_percents(field_name, religion_list)

        for religion in religion_list:
            religion[:0] = [country]
            religion.append(year)

        return religion_list

    def language_field(country, field_data, field_name):
        """Take data as str and return it as list of lists.

        Args:
            country (str): for handling exceptions and forming return.
            field_data (str): data for current field.
            field_name (str): for passing to split_percents() func.

        Return:
            List of lists.

            Each nested list contains five elements: country name as str,
            language name as str, share of population for language as
            float, official status for language in country as bool and
            year of the last update of data as int.

        Example:
            >>>print(language_field('CHILE', 'Spanish 99.5% (official),
            English 10.2%, indigenous 1%, other 2.3%, unspecified 0.2%1
            (2012 est.)', 'Language'))
            [['CHILE', 'Spanish', 99.5, True, 2012],
            ['CHILE', 'English', 10.2, False, 2012],
            ['CHILE', 'indigenous', 1.0, False, 2012],
            ['CHILE', 'other', 2.3, False, 2012],
            ['CHILE', 'unspecified', 0.2, False, 2012]]
        """
        language_list = field_data

        pattern = re.compile(r"\s\((\d\d\d\d) (est.|census)\)")
        matches = re.search(pattern, str(language_list))

        try:
            year = int(matches[1].strip())
            language_list = re.sub(pattern, "", language_list)
        except TypeError:
            year = None

        try:
            language_list = language_list.split(" note")[0]
            language_list = language_list.replace(";", ",")
        except AttributeError:
            pass

        pattern = re.compile(r"\(.*?\)")
        matches = re.finditer(pattern, str(language_list))

        for inst in matches:
            language_list = language_list.replace(
                inst.group(0), inst.group(0).replace(",", ";")
            )
        try:
            language_list = language_list.replace("%1", "%")
            language_list = [i.strip()
                             for i in language_list.split(",")]

        except AttributeError:
            language_list = None

        # handles exception with formating on some countries
        if country == "SPAIN":
            language_list[4:] = [" ".join(language_list[4:])]
        elif country == "KAZAKHSTAN":
            language_list = language_list[0].split(
                " and ") + language_list[1:]
        elif country == "MOZAMBIQUE":
            language_list[3] = language_list[3] + "%"

        language_list = split_percents(field_name, language_list)
        for language in language_list:
            language[:0] = [country]
            language.append(year)

        return language_list

    def ethnicity_field(country, field_data, field_name):
        """Take data as str and return it as list of lists.

        Args:
            country (str): for handling exceptions and forming return.
            field_data (str): data for current field.
            field_name (str): for passing to split_percents() func.

        Return:
            List of lists.

            Each nested list contains four elements: country name as str,
            ethnicity name as str, share of population for ethnicity as
            float and year of the last update of data as int.

        Example:
            >>>print(ethnicity_field('DENMARK', 'Danish (includes
            Greenlandic (who are predominantly Inuit) and Faroese)
            86.3%, Turkish 1.1%, other 12.6% (largest groups are Polish,
            Syrian, German, Iraqi, and Romanian) (2018 est.) note: data
            represent population by ancestry', 'Ethnicity'))

            [['DENMARK', 'Danish', 86.3, '2018'],
            ['DENMARK', 'Turkish', 1.1, '2018'],
            ['DENMARK', 'other', 12.6, '2018']]
        """
        ethnicity_list = field_data.replace(" %", "%")

        pattern = re.compile(r"\s\((\d\d\d\d).*?\)1?")
        match = re.search(pattern, ethnicity_list)

        try:
            year = match[1].strip()
            ethnicity_list = ethnicity_list.replace(match[0], "")
        except TypeError:
            year = None

        pattern = re.compile(r"\s?\(.*?\)\s?")
        matches = re.finditer(pattern, ethnicity_list)

        for inst in matches:
            ethnicity_list = ethnicity_list.replace(inst.group(0), " ")

        # exception in formating for some countries
        if country == "DENMARK":
            ethnicity_list = ethnicity_list.replace("and Faroese)", "")
        elif country == "BURUNDI":
            ethnicity_list = ethnicity_list.replace(",000", "000")
        elif country == "GHANA":
            ethnicity_list = ethnicity_list.replace("47.5", "47.5%")

        ethnicity_list = ethnicity_list.split("note")[0]
        ethnicity_list = ethnicity_list.replace(";", ",")

        ethnicity_list = [
            ethnicity.strip() for ethnicity in ethnicity_list.split(",")
        ]

        # more exceptions
        if country == "PORTUGAL":
            ethnicity_list[1:3] = [",".join(ethnicity_list[1:3])]
            ethnicity_list = ethnicity_list[:2]

        elif country == "REPUBLIC OF THE CONGO":
            ethnicity_list[1:1] = ethnicity_list[1].split("% ")[:2]
            ethnicity_list[1] = ethnicity_list[1] + "%"
            del ethnicity_list[3]
        elif country == "MALDIVES":
            ethnicity_list = [
                ", ".join(ethnicity_list).split(" resulting")[0]]
        elif country == "DEMOCRATIC REPUBLIC OF THE CONGO":
            ethnicity_list = [ethnicity_list[0]]

        ethnicity_list = split_percents(field_name, ethnicity_list)
        for ethnos in ethnicity_list:
            ethnos[:0] = [country]
            ethnos.append(year)
        return ethnicity_list

    def other_fields(field_data):
        """Take data as str and return this str inside a list.

        Args:
            field_data (str): data for current field.

        Return:
            List with a single element.

        Example:
            >>>print(other_fields('Ambassador Carla SANDS'))
            ['Ambassador Carla SANDS']
        """
        try:
            field_data = field_data.replace(
                "'", "’")
        except AttributeError:
            pass
        return [field_data]

    func_dict = {"Literacy": literacy_field,
                 "Urbanization": urbanization_field,
                 "Population Growth": population_growth_field,
                 "Population": population_field,
                 "Imports": imports_exports_field,
                 "Exports": imports_exports_field,
                 "Area": area_field,
                 "GDP (Purchasing Power Parity)": gdp_ppp_field,
                 "GDP per capita (Purchasing Power Parity)": per_capita_field,
                 "Natural Resources": natural_resources_field,
                 "Religion": religion_field,
                 "Language": language_field,
                 "Ethnicity": ethnicity_field}

    return_func = func_dict.get(field_name, other_fields)

    return return_func


def scrape_pdf(path_to_pdf):
    """Convert PDF to text and scrape data from text.

    Args:
        path_to_pdf (str): path to folder, containing PDFs.

    Returns:
        List of lists. Each nested list contains class objects as
        elements.
    """

    # making parameters for PDFminer for this specific PDFs
    la_params = layout.LAParams(
        line_overlap=0.4,
        char_margin=3.0,
        line_margin=1.0,
        word_margin=0.15,
        boxes_flow=0.3,
        detect_vertical=False,
        all_texts=False,
    )
    # defining fields
    fields = [
        "Chief of State",
        "Head of Government",
        "Government Type",
        "Capital",
        "Legislature",
        "Judiciary",
        "Ambassador to US",
        "US Ambassador",
        "Area",
        "Climate",
        "Natural Resources",
        "Economic Overview",
        "GDP (Purchasing Power Parity)",
        "GDP per capita (Purchasing Power Parity)",
        "Exports",
        "Imports",
        "Population",
        "Population Growth",
        "Ethnicity",
        "Language",
        "Religion",
        "Urbanization",
        "Literacy",
    ]

    country_general = []
    country_natural_resources = []
    country_language = []
    country_religion = []
    country_ethnicity = []
    country_import_partners = []
    country_export_partners = []

    for name in os.listdir(path_to_pdf):

        temp_general = []
        filepath = os.path.join(path_to_pdf, name)

        # scraping unformatted text using pdfminer.six
        text = high_level.extract_text(filepath, laparams=la_params)

        # here we extract country name from text
        text = text.split("\n", 1)
        country_id = text.pop(0)
        if country_id == "SAO TOMEAND PRINCIPE":
            country_id = "SAO TOME AND PRINCIPE"

        text = text[0].split()

        # searching for the date of last update for PDF and removing it
        last_update_index = [
            (i, i + 2) for i in range(len(text))
            if text[i: i + 2] == ["as", "of"]
        ]

        last_update = " ".join(
            text[last_update_index[0][1]: last_update_index[0][1] + 2]
        )
        last_update = last_update.strip()
        del text[last_update_index[0][0]: last_update_index[0][0] + 4]

        temp_general.append(last_update)

        # We index text with get_index function
        index_dict = create_index(fields, text, country_id)

        # we work with fieldnames in reverse order, since we need to parse
        # text from end to begining
        for field_name in fields[::-1]:

            field_func = format_field_data(field_name)
            # this handles some expections for Sudan and Chad, where
            # fields Chief of State and Head of Government are joined
            if index_dict[field_name] == [] and field_name == "Chief of State":
                field_data = " ".join(text[5:])

            # some countries don't have some fields, like Literacy
            # so with such countries we set value for this fields to None
            elif index_dict[field_name] == []:
                field_data = None

            # This is main part, that works with most of the text.
            # It starts with the end of text and finds the last field
            # based on index that we got from get_index function

            else:
                start_field = index_dict[field_name][0]
                start_content = index_dict[field_name][1]

                field_data = " ".join(text[start_content:])
                del text[start_field:]

            if field_data in ("NA", "N/A"):
                field_data = None

            three_arg_fields = ["Imports", "Exports",
                                "Religion", "Ethnicity", "Language"]
            two_arg_fields = ["Population", "Area", "Natural Resources"]

            if field_name in three_arg_fields:
                temp = field_func(country_id, field_data, field_name)

                if field_name == "Imports":
                    temp_general.extend(temp[0])
                    temp_list = [cl.CountryImportPartners(
                        *item) for item in temp[1]]
                    country_import_partners.extend(temp_list)

                elif field_name == "Exports":
                    temp_general.extend(temp[0])
                    temp_list = [cl.CountryExportPartners(
                        *item) for item in temp[1]]
                    country_export_partners.extend(temp_list)

                elif field_name == "Ethnicity":
                    temp_list = [cl.CountryEthnicity(*item) for item in temp]
                    country_ethnicity.extend(temp_list)

                elif field_name == "Religion":
                    temp_list = [cl.CountryReligion(*item) for item in temp]
                    country_religion.extend(temp_list)

                elif field_name == 'Language':
                    temp_list = [cl.CountryLanguage(*item) for item in temp]
                    country_language.extend(temp_list)

            elif field_name in two_arg_fields:
                temp = field_func(country_id, field_data)

                if field_name == "Natural Resources":
                    temp_list = [cl.CountryNaturalResources(
                        *item) for item in temp]
                    country_natural_resources.extend(temp_list)

                else:
                    temp_general.extend(temp)

            else:
                temp = field_func(field_data)
                temp_general.extend(temp)

        temp_general.append(country_id)
        temp_general = cl.CountryGeneral(*temp_general[::-1])
        country_general.append(temp_general)

    print("Finished scraping PDF")
    return [country_general,
            country_natural_resources,
            country_export_partners,
            country_import_partners,
            country_ethnicity,
            country_language,
            country_religion]
