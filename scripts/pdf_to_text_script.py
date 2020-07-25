"""Takes PDF, converts them to text and scrapes data from it."""
import os
import ast
from pdfminer import high_level, layout


def create_index(fields, text_split, country_id):
    """Builds index dictionary with index for every field.

    Args:
        fields (list of str): list of field names.
        text_split (list of str): text split to list, where every word
            is an element of list.
        country_id (str): name of the country, used to handle minor
            errors in text while indexing specific countries.

    Returns:
        dict: dictionary, with field name as a key and tuple as a value.
        Each tuple contains two int. First int - index of a first word of
        a field name in text as list, second int is an index +1 of a last
        word of a field name in text as list.

    Examples:
        print(create_index(["Climate", "Natural Resources"], ["Climate",
        "and", "Natural", "Resources"], "Russia"))
        {"Climate":(0,1), "Natural Resources":(2,4)}  
    """

    index_dict = {}

    # deleting unnecesary headers in text_split
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

    # geting index for each field
    for item in fields:

        item_list = item.split()

        # this part handles some exception for some pages that contain errors in naming
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

        # this part finds build indexes for every field name
        # every index consists of start index (index of the first word of field name)
        # and end index (index of the last word of field name) inside a tuple inside a list
        # in most cases there is only one tuple for each field name.
        index = [
            (i, i + len(item_list))
            for i in range(len(text_split))
            if text_split[i: i + len(item_list)] == item_list
        ]

        # but some times there are more than one occurence of the field name
        # in text and so there are more than one index tuple.
        # With field "US ambassador" we always use second occurence of fieldname
        # (second tuple in list of tuples)
        # with other - we always use first.
        if len(index) > 1 and item == "US Ambassador":
            index = [i for i in index[1]]
        elif len(index) > 0:
            index = [i for i in index[0]]

        index_dict[item] = index

    return index_dict


def pdf_scraper(path_to_pdf):
    """this functiion takes path to pdf folder then scrapes
    each pdf for text, then splits text down as list, where every word is an element.
    Then it slices text by field names.
    Returns a dict object which consists of country names as a key
    and nested dictionaris as values.
    Nested dictionaries use fields for keys, and use content of the field as a value.
    Return object can be used to make a csv file or fill a table in DB.
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

        # scraping unformated text using pdfminer.six
        text = high_level.extract_text(filepath, laparams=la_params)

        # here we extract country name from text
        text = text.split("\n", 1)
        country_id = text.pop(0)
        if country_id == "SAO TOMEAND PRINCIPE":
            country_id = "SAO TOME AND PRINCIPE"
        # we split text by whitespaces and end-line characters, so text is presented as a list
        # where every word and set of any characters such as numbers has index
        text = text[0].split()

        nested_dict[country_id] = {}

        # searching for the date of last update for PDF and removing it from text
        last_update_index = [
            (i, i + 2) for i in range(len(text)) if text[i: i + 2] == ["as", "of"]
        ]

        last_update = " ".join(
            text[last_update_index[0][1]: last_update_index[0][1] + 2]
        )
        last_update = last_update.strip()
        del text[last_update_index[0][0]: last_update_index[0][0] + 4]

        nested_dict[country_id]["last_update"] = last_update

        # We index text with get_index function
        index_dict = create_index(fields, text, country_id)

        # we work with fieldnames in reverse order, since we need to parse
        # text from end to begining
        for fieldname in fields[::-1]:

            # this handles some expections for Sudan and Chad, where
            # fields Chief of State and Head of Government are joined
            if index_dict[fieldname] == [] and fieldname == "Chief of State":
                nested_dict[country_id][fieldname] = " ".join(text[5:])

            # some countries don't have some fields, like Literacy
            # so with such countries we set value for this fields to NULL
            elif index_dict[fieldname] == []:
                nested_dict[country_id][fieldname] = "NULL"

            # This is main part, that works with most of the text.
            # It starts with the end of text and finds the last field
            # based on index that we got from get_index function
            # It creates fieldname as a key, and content of text as a value
            # then it deletes fieldname and content from the splited text we work on.
            # So one by one we delete each field from end to begining.

            else:
                start_field = index_dict[fieldname][0]
                start_content = index_dict[fieldname][1]

                nested_dict[country_id][fieldname] = " ".join(
                    text[start_content:])
                del text[start_field:]

    # some coutries have field content NA or N/A, we replace them with NULL for consistency
    nested_dict = str(nested_dict).replace("'NA'", "'NULL'")
    nested_dict = nested_dict.replace("N/A", "NULL")

    nested_dict = ast.literal_eval(nested_dict)

    print("Finished scraping text")
    return nested_dict
