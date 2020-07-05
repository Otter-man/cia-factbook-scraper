import os
import ast
import re
import csv

###раздел для функций
def get_index(fields, text, country_id):
    """this function builds dict of indexes
    for every country with indexes of elements,
    that represent the rows in the csv"""

    index_dict = {}

    # deleting unnecesary headers in text
    del text[text.index("GOVERNMENT")]
    del text[text.index("GEOGRAPHY")]

    pep_soc = [
        (i, i + 3)
        for i in range(len(text))
        if text[i : i + 3] == ["PEOPLE", "&", "SOCIETY"]
    ]
    del text[pep_soc[0][0] : pep_soc[0][1]]

    if "'Economic', 'Overview'" in str(text):
        del text[text.index("ECONOMY")]

    # geting index for each field
    for item in fields:

        item_list = item.split()

        # exception for some pages that contain errors in naming
        if country_id == "GERMANY" and item == "GDP (Purchasing Power Parity)":
            item_list = "GDP Purchasing Power Parity)".split()
        elif country_id == "MOLDOVA" and item == "US Ambassador":
            item_list = ["Ambassador"]
        elif country_id == "IRAQ" and item == "Area":
            item_list = ["Area,"]
        elif country_id == "IRAQ" and item == "Urbanization":
            item_list = ["2003Urbanization"]
        elif (
            country_id == "TURKMENISTAN" or country_id == "MAURITIUS"
        ) and item == "Economic Overview":
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
        last_update_index = [
            (i, i + 2) for i in range(len(text)) if text[i : i + 2] == ["as", "of"]
        ]

        last_update = " ".join(
            text[last_update_index[0][1] : last_update_index[0][1] + 2]
        )

        del text[last_update_index[0][0] : last_update_index[0][0] + 4]

        main_sheet[country_id]["last_update"] = last_update

        # далее получаем для каждой строки индекс и будем работать от него
        # функция get index для этого

        index_dict = get_index(fields, text, country_id)

        for item in fields[::-1]:

            main_sheet[country_id][item] = []

            if index_dict[item] == [] and item == "Chief of State":
                main_sheet[country_id][item] = " ".join(text[5:])

            elif index_dict[item] == []:
                main_sheet[country_id][item] = "NA"

            else:
                starting_index = index_dict[item][0]
                main_sheet[country_id][item] = " ".join(
                    text[starting_index + len(item.split()) :]
                )
                del text[starting_index:]


# with open("csv_all.csv", "w") as csv_f:
#     csv_writer = csv.writer(csv_f, delimiter="|")
#     count = 1

#     csv_writer.writerow(
#         ["country_id"] + [field for field in fields] + ["last update of data"]
#     )
#     for country in main_sheet:

#         csv_writer.writerow(
#             [country] + [v for k, v in list(main_sheet[country].items())[::-1]]
#         )
#         print(country, count)
#         count += 1
#     print("finished")

