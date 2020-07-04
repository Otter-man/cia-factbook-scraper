import os
import ast
import re

###раздел для функций
def get_index(fields, text, country_id):
    """this function builds dict of indexes
    for every country with indexes of elements,
    that represent the fields in the base"""

    index_dict = {}

    for item in fields:

        item_list = item.split()

        # исключения для некоторых страниц с ошибкой в заполнении.
        if country_id == "GERMANY" and item == "GDP (Purchasing Power Parity)":
            item_list = "GDP Purchasing Power Parity)".split()
        elif country_id == "MOLDOVA" and item == "US Ambassador":
            item_list = ["Ambassador"]
        elif country_id == "IRAQ" and item == "Area":
            item_list = ["Area,"]
        elif country_id == "IRAQ" and item == "Urbanization":
            item_list = ["2003Urbanization"]
        elif country_id == "TURKMENISTAN" or country_id == "MAURITIUS":
            item_list = ["ECONOMY"]

        index = [
            (i, i + len(item_list))
            for i in range(len(text))
            if text[i : i + len(item_list)] == item_list
        ]

        if len(index) > 1 and item == "US Ambassador":
            index = [i for i in index[1]]
        elif len(index) > 0:
            index = [i for i in index[0]]

        index_dict[item] = index

    return index_dict


def cleaner(text):
    """this function cleans text as list from four
    recurring unnecesary elements"""

    indexer = text.index

    del text[indexer("GOVERNMENT")]
    del text[indexer("GEOGRAPHY")]

    pep_soc = [
        (i, i + 3)
        for i in range(len(text))
        if text[i : i + 3] == ["PEOPLE", "&", "SOCIETY"]
    ]
    del text[pep_soc[0][0] : pep_soc[0][1]]

    if "Economic Overview" in str(text):
        del text[indexer("ECONOMY")]

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
            (i, i + 2) for i in range(len(text)) if text[i : i + 2] == ["as", "of"]
        ]

        last_update = " ".join(
            text[last_update_index[0][1] : last_update_index[0][1] + 2]
        )

        del text[last_update_index[0][0] : last_update_index[0][0] + 4]

        main_sheet[country_id]["last_update"] = last_update

        # далее чистим весь документ от лишних элементов с учетом исключений
        # для этого функция cleaner
        text = cleaner(text)

        # далее получаем для каждой строки индекс и будем работать от него
        # функция get index для этого
        print(country_id)
        index_dict = get_index(fields, text, country_id)
        print(index_dict)
        print(" ")

        # нужно переписать функцию index_dict с учетом того, что новый список состоит из отдельных слов.

        # if "Literacy" not in index_dict.keys():
        #     main_sheet[country_id]["Literacy"] = ("N/A", "N/A")
        # elif country_id == "SVALBARD":
        #     main_sheet[country_id]["Literacy"] = ("N/A", "N/A")
        #     del text[index_dict["Literacy"] :]
        # else:
        #     literacy = text[index_dict["Literacy"] :]

        #     literacy = literacy[1].split(" ")
        #     literacy = literacy[0], literacy[1][1:5]
        #     main_sheet[country_id]["Literacy"] = literacy

        # urbanization = text[index_dict["Urbanization"] :]
        # del text[index_dict["Urbanization"] :]

        # try:
        #     urbanization = (
        #         urbanization[1].split(" ")[2],  # urban population
        #         urbanization[1].split("(")[1][:4],  # year of update for population
        #         urbanization[2].split(" ")[3],  # rate of urbanization
        #     )
        # except IndexError as e:
        #     urbanization = ("N/A", "N/A", "N/A")

        # main_sheet[country_id]["urbanization"] = urbanization

        # religion = text[index_dict["Religion"] + 1 :]
        # del text[index_dict["Religion"] :]
        # religion = " ".join(religion)
        # religion = " ".join(religion.split())
        # main_sheet[country_id]["religion"] = religion

        # language = text[index_dict["Language"] + 1 :]
        # del text[index_dict["Language"] :]
        # language = " ".join(language)
        # language = " ".join(language.split())
        # main_sheet[country_id]["language"] = language

        # ethnicity = text[index_dict["Ethnicity"] + 1 :]
        # del text[index_dict["Ethnicity"] :]
        # ethnicity = " ".join(ethnicity)
        # ethnicity = " ".join(ethnicity.split())
        # main_sheet[country_id]["ethnicity"] = ethnicity

        # pop_grow = text[index_dict["Population Growth"] + 1 :]
        # del text[index_dict["Population Growth"] :]
        # pop_grow = " ".join(pop_grow)
        # pop_grow = " ".join(pop_grow.split())
        # main_sheet[country_id]["pop_grow"] = pop_grow

        # population = text[index_dict["Population"] + 1 :]
        # del text[index_dict["Population"] :]
        # population = " ".join(population)

        # мы определяем нужный элемент по длине стринга
        # и форматируем их, чтобы оставить только месяц и год  изменения.
        # for number in last_update_index:
        #     if len(text[number]) < 22:
        #         last_update = text.pop(number)
        #         last_update = " ".join(last_update.split(" ")[2:4])
        #         main_sheet[country_id]["last_update"] = last_update
        #         break
