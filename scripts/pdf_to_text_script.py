from pdfminer import high_level, layout
import os
import csv

###раздел для функций
def get_index(fields, text, country_id):
    """this function builds dict of indexes
    for every country with indexes of elements,
    that represent the rows in the csv
    returns a dict of indexes"""

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


def pdf_scraper(path_to_pdf):
    """this functiion takes path to pdf folder then scrapes 
    each pdf for text, then breaks text down and sorts it by fields.
    Returns a dict object which consists of country names as a key
    and nested dictionaris as values.
    Nested dictionaries use fields for keys.
    Return can be used to make a json file or csv file.
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

    nested_dict = {}

    for name in os.listdir(path_to_pdf):
        filepath = os.path.join(path_to_pdf, name)

        text = high_level.extract_text(filepath, laparams=la_params)

        text = text.split("\n", 1)

        country = text.pop(0)
        if country == "SAO TOMEAND PRINCIPE":
            country = "SAO TOME AND PRINCIPE"

        text = text[0].split()
        text = [country] + text

        # list_file.write(str(text))
        country_id = text.pop(0)
        nested_dict[country_id] = {}

        # ищем индекс элемент, в котором хранится данные о дате последнего апдейта пдф.
        last_update_index = [
            (i, i + 2) for i in range(len(text)) if text[i : i + 2] == ["as", "of"]
        ]

        last_update = " ".join(
            text[last_update_index[0][1] : last_update_index[0][1] + 2]
        )

        del text[last_update_index[0][0] : last_update_index[0][0] + 4]

        nested_dict[country_id]["last_update"] = last_update

        # далее получаем для каждой строки индекс и будем работать от него
        # функция get index для этого

        index_dict = get_index(fields, text, country_id)

        for item in fields[::-1]:

            nested_dict[country_id][item] = []

            if index_dict[item] == [] and item == "Chief of State":
                nested_dict[country_id][item] = " ".join(text[5:])

            elif index_dict[item] == []:
                nested_dict[country_id][item] = "NA"

            else:
                starting_index = index_dict[item][0]
                nested_dict[country_id][item] = " ".join(
                    text[starting_index + len(item.split()) :]
                )
                del text[starting_index:]

    print("Finished scraping text")
    return nested_dict


# country_dict = pdf_scraper("pdf")

