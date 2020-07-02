import os
import ast
import re

###раздел для функций
def get_index(fields, text):
    """this function builds dict of indexes
    for every country with indexes of elements,
    that represent the fields in the base"""

    indexer = text.index

    index_dict = {}

    for item in fields:

        try:
            index_dict[item] = indexer(item)

        except ValueError as e:
            if (
                "Chief of State" in str(e)
                or "Head of Government" in str(e)
                or "Capital" in str(e)
                or "Ambassador to US" in str(e)
            ):
                index_dict[item] = -1

            elif "US Ambassador" in str(e) and country_id == "UNITED STATES":
                index_dict[item] = -1

            elif "US Ambassador" in str(e) and country_id == "MOLDOVA":
                index_dict[item] = indexer("Ambassador")

            elif "Area" in str(e):
                index_dict[item] = indexer("Area,")

            elif "Economic Overview" in str(e):
                index_dict[item] = indexer("ECONOMY")

            elif "GDP (Purchasing Power Parity)" in str(e):
                index_dict[item] = indexer("GDP Purchasing Power Parity)")

            elif "Religion" in str(e):
                index_dict[item] = indexer("Religion ")

            elif "Urbanization" in str(e):
                index_dict[item] = indexer("2003Urbanization")

    return index_dict


def cleaner(text):
    """this function cleans text as list from four
    recurring unnecesary elements"""

    poper = text.pop
    indexer = text.index

    poper(indexer("GOVERNMENT"))
    poper(indexer("GEOGRAPHY"))

    try:
        poper(indexer("PEOPLE & SOCIETY"))
    except ValueError as e:
        poper(indexer("PEOPLE & SOCIETY "))

    if "Economic Overview" in str(text):
        poper(indexer("ECONOMY"))
    return text


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

test = ""
index_of_fields = {}
main_sheet = {}
###вот тут начинаем работать с файлом
###открываем файл

for item in sorted(os.listdir("list_text")):
    with open(f"list_text/{item}", "r") as f:
        text = f.read()
        text = ast.literal_eval(text)

        # Взначение country_id записывается название страны.
        # Оно в файле всегда элемент 0. После этого элемент удаляется.
        country_id = text.pop(0)
        main_sheet[country_id] = {}

        # ищем индекс элемент, в котором хранится данные о дате последнего апдейта пдф.
        # т.к. ищем мы по неточному значению, то может быть несколько подходящих индексов
        last_update_index = [
            num for num, string in enumerate(text) if "as of" in string
        ]

        # мы определяем нужный элемент по длине стринга
        # и форматируем их, чтобы оставить только месяц и год  изменения.
        for number in last_update_index:
            if len(text[number]) < 22:
                last_update = text.pop(number)
                last_update = " ".join(last_update.split(" ")[2:4])
                main_sheet[country_id]["last_update"] = last_update
                break
        # далее чистим весь документ от лишних элементов с учетом исключений
        # для этого функция cleaner
        text = cleaner(text)

        # далее получаем для каждой строки индекс и будем работать от него
        # функция get index для этого
        index_dict = get_index(fields, text)

        if "Literacy" not in index_dict.keys():
            main_sheet[country_id]["Literacy"] = ("N/A", "N/A")
        elif country_id == "SVALBARD":
            main_sheet[country_id]["Literacy"] = ("N/A", "N/A")
            del text[index_dict["Literacy"] :]
        else:
            literacy = text[index_dict["Literacy"] :]
            del text[index_dict["Literacy"] :]
            literacy = literacy[1].split(" ")
            literacy = literacy[0], literacy[1][1:5]
            main_sheet[country_id]["Literacy"] = literacy

        urbanization = text[index_dict["Urbanization"] :]
        del text[index_dict["Urbanization"] :]
        print(urbanization)
        try:
            urbanization = (
                urbanization[1].split(": ")[0],
                urbanization[1].split(" ")[2],
                urbanization[1][-5:-1],
            )
        except IndexError as e:
            urbanization = urbanization[0].split(": ")[0], "N/A", "N/A"

        print(urbanization)
