import ast
import re


def percent_taker(category, a_list):
    """this function takes data from preparing_db_objects
    for language, ethnicity, religion, import and export partners
    and returns nested lists where every list contains item of category
    (religion, ethnos, language) and % of population that uses it for
    for every category. For language it also returns whethere language is
    official in country or part of the country"""

    return_list = []
    language_list = []

    for element in a_list:

        if element[:4] == "and ":
            element = element[4:]
        elif element[:5] == "also ":
            element = element[5:]
        elif element[:9] == "but also ":
            element = element[9:]
        elif element[:11] == "there is a ":
            element = element[11:]

        if category == "Language":

            element = element.replace(";", ",")

            if "official" in element:
                officiality = "Yes"
            else:
                officiality = "No"

            element = element.replace(" (official)", "")

        element = element.strip()

        element_listed = element.split()

        index = [element_listed.index(i) for i in element_listed if "%" in i]

        try:
            index = index[0]

            if category == "Religion":
                if (
                    not element_listed[index - 1].isalpha()
                    and "non-" not in element_listed[index - 1]
                    and "/" not in element_listed[index - 1]
                ):

                    percentage = "".join(element_listed[index - 1 : index + 1])
                    parted = " ".join(element_listed[: index - 1])
                else:
                    percentage = element_listed[index]
                    parted = " ".join(element_listed[:index])

            else:
                percentage = element_listed[index]
                parted = " ".join(element_listed[:index])

        except:
            percentage = "NULL"
            parted = " ".join(element_listed)

        try:
            percentage = percentage.replace("%", "")
            percentage = float(percentage)
        except:
            pass

        # for Language we build two identical lists, since sometimes
        # for language combo Country + language is not unique and we need to
        # sort it for duplicates later using two lists
        if category == "Language":
            return_list.append([parted, percentage, officiality])
            language_list.append([parted, percentage, officiality])
        else:
            return_list.append([parted, percentage])

    # we remove duplicate languages from main list, by turning it to
    # dictionary with the language + percent as a key
    # but this doesn't check the "official" part, so duplicate with
    # official status can be accidently removed
    if category == "Language":
        return_list = list(dict((x[0] + str(x[1]), x) for x in return_list).values())

        # To check that the language official status isn't lost, we
        # compare elements from the second list, wich we didn't modify.
        # If the langugae with official status was removed as a duplicate
        # we replace it in the main list
        for item in language_list:
            if item not in return_list and item[2] == "Yes":
                item_index = return_list.index(item[:2] + ["No"])
                return_list[item_index] = item

    for item in return_list:
        if item[0] == "":
            del return_list[return_list.index(item)]

    return return_list


def big_number_converter(big_number):
    """this function converts big numbers (like millions and trillions)
    from words to numbers"""

    big_number = big_number.replace("$", "")

    big_number = big_number.split(" ")

    if "million" in str(big_number):
        zero = "000000"
    elif "billion" in str(big_number):
        zero = "000000000"
    elif "trillion" in str(big_number):
        zero = "000000000000"
    else:
        zero = "000000000"

    big_number = big_number[0].split(".")
    try:
        big_number = f"{big_number[0]}{big_number[1]}{zero[len(big_number[1]):]}"
    except:
        big_number = f"{big_number[0]}{zero}"

    return int(big_number)


def preparing_db_objects(obj):
    """
    this function takes dict object prepared by pdf_scraper()
    and breaks it into 7 different dictionaries, each with data
    for specific table in the sqlite DB.
    Tables will be 'Country overview' with overview of the country,
    Natural Resources, Religion, Language, Ethnicity, Export Partners
    and Import Partners.
    Function returns dict fo Country Overview, and list that contains all
    other dicts
    """

    db_obj_overview = {}
    db_obj_nat_res = {}
    db_obj_religion = {}
    db_obj_language = {}
    db_obj_ethnicity = {}
    db_obj_exp_part = {}
    db_obj_imp_part = {}

    for country in sorted(list(obj)):

        db_obj_overview[country] = {}
        db_obj_nat_res[country] = []
        db_obj_overview[country]["country_id"] = country

        for field in list(obj[country])[::-1]:

            field_data = obj[country][field]

            if field == "Literacy":
                pattern = re.compile(r"([0-9\.]{0,4}%).*\((20..)")
                match = re.search(pattern, field_data)
                # in literacy field we extract two columns - "literacy_%_of_population"
                # and "literacy year updated" using regexp
                if field_data == "NULL":
                    lit_year, lit_percent = field_data, field_data
                else:
                    lit_year = match[2]
                    lit_percent = match[1]

                try:
                    lit_percent = float(lit_percent.replace("%", ""))
                    lit_year = int(lit_year)

                except ValueError:
                    pass

                db_obj_overview[country]["literacy_%_of_population"] = lit_percent
                db_obj_overview[country]["literacy_year"] = lit_year

            elif field == "Urbanization":
                ##in urbanization field we extract three columns - "rate of urbanization"
                # and "urban population %" and "urban population year of update" using regexp
                pattern = re.compile(
                    r"\s?([0-9\. ]{1,5}\%).*\((20..)\)?.*urbanization: ([\-0-9\. ]{1,5}\%)"
                )
                match = re.search(pattern, field_data)

                if field_data == "NULL":
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
                except ValueError:
                    pass

                db_obj_overview[country]["rate_of_urbanization"] = rate_urb
                db_obj_overview[country]["urban_population"] = urb_pop
                db_obj_overview[country]["urban_population_year"] = urb_pop_year

            elif field == "Population Growth":
                # here we extract two columns pop. growth % and year of update
                pattern = re.compile(r"([\-\.0-9 ]*\%).*(20\d\d)")
                match = re.search(pattern, field_data)

                if field_data == "NULL":
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
                except ValueError as e:
                    pass

                db_obj_overview[country]["population_growth"] = pop_grow
                db_obj_overview[country]["population_growth_year"] = pop_grow_year

            elif field == "Population":
                # population field gives us population number and year of update

                # here we handle the only country in list wich is uninhabited
                if country == "FRENCH SOUTHERN AND ANTARCTIC LANDS":
                    pop_year = "NULL"
                    population = "0"

                else:
                    # we convert worded numbeer (like "1 billion") to an integer with
                    # using function big_number_converter()
                    if "million" in str(field_data) or "billion" in str(field_data):

                        pattern = re.compile(
                            r"([0-9\.,]*)\s(million|billion).*\((.*)est"
                        )
                        match = re.search(pattern, field_data)

                        population = " ".join([match[1], match[2]])

                        population = big_number_converter(population)

                        pop_year = match[3]

                    else:
                        pattern = re.compile(r"([0-9\,]*) \((.*) est")
                        match = re.search(pattern, field_data)

                        population = match[1].replace(",", "")

                        pop_year = match[2]

                db_obj_overview[country]["population"] = int(population)
                db_obj_overview[country]["population_year"] = pop_year.strip()

            elif field == "Imports" or field == "Exports":
                # this fields gives us two columns for each - import|export size and year of update
                # with function "percent taker" we also create separate dictionaries for
                # import|export partners
                if field_data == "NULL":
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

                    # thic block handles exception in formating in ETHIOPIA
                    if field == "Imports" and country == "ETHIOPIA":
                        partners = field_data.split(") ")[1]

                    else:
                        # this block handles countries wich don't have import|export partners written
                        try:
                            partners = field_data.split("partners")[1].replace(": ", "")
                        except IndexError as e:
                            partners = "NULL"

                    try:
                        act_year = match[3]
                        activity_size = f"{match[1]} {match[2]}"
                    except TypeError as e:  # exception handles some country with error in formating
                        act_year = field_data.split("(")[1][:5]
                        activity_size = "".join(field_data.split()[:2])

                if act_year != "NULL":
                    act_year = int(act_year.strip())

                if activity_size != "NULL":
                    activity_size = big_number_converter(activity_size)

                db_obj_overview[country][field] = activity_size
                if field == "Imports":
                    db_obj_overview[country]["imports_year"] = act_year
                elif field == "Exports":
                    db_obj_overview[country]["exports_year"] = act_year

                # here we handle import partners for the second dictionary
                pattern = re.compile(r"\s\(.*?\)")
                match = re.search(pattern, partners)

                # we clean unnecesary info with year, wich
                # duplicates imports|export year of update
                # it is presented in every country except for imports sudan
                if field == "Imports" and country == "SUDAN":
                    pass
                else:
                    if partners != "NULL" and partners != "N/A":
                        partners = partners.replace(match[0], "")

                # handles the mistake in text for France import partners
                if field == "Imports" and country == "FRANCE":
                    partners = partners.replace("Belgium", "Belgium ")

                # returning , that were skipped in the text
                partners = partners.replace("% ", "%,")

                partners = partners.split(",")

                # fixing forgotten % symbols
                for item in partners:
                    ind = partners.index(item)
                    item = item.strip()
                    if item != "" and item != "NULL" and item[-1] != "%":
                        item = item + "%"
                    partners[ind] = item

                # we create content for import|exports partners dictionary
                # with percent_taker function
                partners_listed = percent_taker(field, partners)

                if field == "Imports":
                    db_obj_imp_part[country] = partners_listed
                    for partner in db_obj_imp_part[country]:
                        partner.append(act_year)
                elif field == "Exports":
                    db_obj_exp_part[country] = partners_listed
                    for partner in db_obj_exp_part[country]:
                        partner.append(act_year)

            elif field == "Area":
                # this block makes 3 columns - area land, water and total area.
                if country == "FRENCH SOUTHERN AND ANTARCTIC LANDS":
                    total, land, water = "NULL", "NULL", "NULL"

                elif country == "GREENLAND":
                    total = field_data.lower().split("total: ")
                    total = total[1][: total[1].index(" sq km")].replace(",", "")

                    land = "NULL"
                    water = "NULL"

                else:
                    total = field_data.lower().split("total: ")
                    total = total[1][: total[1].index(" sq km")].replace(",", "")

                    land = field_data.lower().split("land")
                    land = land[1][: land[1].index(" sq km")].replace(",", "")
                    land = land.replace(":", "").strip()
                    land = land.replace("-", "")

                    if country == "SAUDI ARABIA":
                        total = big_number_converter(total)
                        land = big_number_converter(land)

                    try:
                        water = field_data.lower().split("water: ")
                        water = water[1][: water[1].index(" sq km")].replace(",", "")
                    except:
                        water = "0"

                try:
                    total = float(total)
                    land = float(land)
                    water = float(water)
                except ValueError as e:
                    pass

                db_obj_overview[country]["area_total_(sq_km)"] = total
                db_obj_overview[country]["area_land_(sq_km)"] = land
                db_obj_overview[country]["area_water_(sq_km)"] = water

            elif field == "GDP (Purchasing Power Parity)":
                # this field we make columns GDP size and year of update
                pattern = re.compile(
                    r"(\$[0-9\.]+)\s(bi+llion|million|trillion)\s\((20[0-9]{2})"
                )
                match = re.search(pattern, field_data)

                try:
                    gdp = f"{match[1]} {match[2].replace('ii','i')}"
                    gdp_year = match[3]
                except:
                    gdp, gdp_year = "NULL", "NULL"

                if gdp_year != "NULL":
                    gdp_year = int(gdp_year)

                if gdp != "NULL":
                    gdp = big_number_converter(gdp)

                db_obj_overview[country]["gdp"] = gdp
                db_obj_overview[country]["gdp_year"] = gdp_year

            elif field == "GDP per capita (Purchasing Power Parity)":
                # this blocks make two columns - gdp per capita and year of update
                try:
                    per_capita = field_data.split(" (")[0]
                    per_capita_year = field_data.split(" (")[1][:5]
                    per_capita_year = per_capita_year.strip().replace(")", "")
                except:
                    per_capita, per_capita_year = "NULL", "NULL"

                if per_capita != "NULL" and per_capita_year != "NULL":
                    per_capita = int(per_capita[1:].replace(",", ""))
                    per_capita_year = int(per_capita_year)

                db_obj_overview[country]["per_capita_$"] = per_capita
                db_obj_overview[country]["per_capita_year"] = per_capita_year

            elif field == "Natural Resources":
                # this block we use to create table "natural resources"
                resource_list = field_data.split("note")[0]
                resource_list = [
                    resource.strip() for resource in resource_list.split(",")
                ]

                for resource in resource_list:
                    temp_resources = []

                    if resource[:4] == "and ":
                        resource = resource[4:]

                    if ";" in resource:
                        temp_resources.extend(resource.split(";"))
                    elif "(" in resource:
                        temp_resources.append(resource[: resource.find(" (")])
                    else:
                        temp_resources.append(resource)

                    for item in temp_resources:
                        if item != "":
                            db_obj_nat_res[country].append(item.strip())

            elif field == "Religion":
                # this blocks is used to prepare 'Religion' table
                # with the help of percent_taker function
                religion_list = field_data.split("note")[0]

                pattern = re.compile(r"\d\d\d\d")
                match = re.search(pattern, religion_list)

                try:
                    year = match[0]
                except:
                    year = "NULL"

                # handles specific formating for ukraine
                if country == "UKRAINE":
                    religion_list = re.sub("\(.*?\)\)", "", religion_list)
                # cleans code of things in parenthesis
                religion_list = re.sub("\(.*?\)1?", "", religion_list)

                religion_list = [
                    religion.strip() for religion in religion_list.split(",")
                ]

                db_obj_religion[country] = percent_taker(field, religion_list)
                for religion in db_obj_religion[country]:
                    religion.append(year.strip())

            elif field == "Language":
                # this block used for "Language" table with percent_taker
                language_list = field_data

                pattern = re.compile(r"\s\((\d\d\d\d) (est.|census)\)")
                matches = re.search(pattern, language_list)

                try:
                    year = matches[1]
                    language_list = re.sub(pattern, "", language_list)
                except:
                    year = "NULL"

                language_list = language_list.split(" note")[0]
                language_list = language_list.replace(";", ",")

                pattern = re.compile(r"\(.*?\)")
                matches = re.finditer(pattern, language_list)

                for inst in matches:
                    language_list = language_list.replace(
                        inst.group(0), inst.group(0).replace(",", ";")
                    )
                language_list = language_list.replace("%1", "%")

                language_list = [i.strip() for i in language_list.split(",")]

                # handles exception with formating on some countries
                if country == "SPAIN":
                    language_list[4:] = [" ".join(language_list[4:])]
                elif country == "KAZAKHSTAN":
                    language_list = language_list[0].split(" and ") + language_list[1:]
                elif country == "MOZAMBIQUE":
                    language_list[3] = language_list[3] + "%"

                db_obj_language[country] = percent_taker(field, language_list)
                for language in db_obj_language[country]:
                    language.append(year.strip())

            elif field == "Ethnicity":
                # this block is for "Ethnicity" table
                ethnicity_list = field_data.replace(" %", "%")

                pattern = re.compile(r"\s\((\d\d\d\d).*?\)1?")
                match = re.search(pattern, ethnicity_list)

                try:
                    year = match[1]
                    ethnicity_list = ethnicity_list.replace(match[0], "")
                except:
                    year = "NULL"

                pattern = re.compile(r"\s?\(.*?\)\s?")
                matches = re.finditer(pattern, ethnicity_list)

                for inst in matches:
                    ethnicity_list = ethnicity_list.replace(inst.group(0), " ")

                # eception in formating for some countries
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
                    ethnicity_list = [", ".join(ethnicity_list).split(" resulting")[0]]
                elif country == "DEMOCRATIC REPUBLIC OF THE CONGO":
                    ethnicity_list = [ethnicity_list[0]]

                db_obj_ethnicity[country] = percent_taker(field, ethnicity_list)
                for ethnos in db_obj_ethnicity[country]:
                    ethnos.append(year.strip())

            else:
                # pass the rest of fields as is to main table "countrie overwiew"
                db_obj_overview[country][field] = field_data.replace("'", "’")

    return [
        db_obj_overview,
        db_obj_nat_res,
        db_obj_religion,
        db_obj_language,
        db_obj_ethnicity,
        db_obj_exp_part,
        db_obj_imp_part,
    ]

