from pdfminer import high_level, layout
import os


def pdf_scraper(path_to_pdf):

    path_to_text = "pdf_text"
    path_to_listed_text = "list_text"

    if not os.path.exists(path_to_text):
        os.mkdir(path_to_text)

    if not os.path.exists(path_to_listed_text):
        os.mkdir(path_to_listed_text)

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

    for name in os.listdir(path_to_pdf):
        filepath = os.path.join(path_to_pdf, name)

        with open(os.path.join(path_to_text, f"{name[:-3]}txt"), "w") as text_file:
            with open(
                os.path.join(path_to_listed_text, f"{name[:-3]}list.txt"), "w"
            ) as list_file:

                text = high_level.extract_text(filepath, laparams=la_params)

                text_file.write(text)

                text = text.split("\n", 1)

                country = text.pop(0)
                if country == "SAO TOMEAND PRINCIPE":
                    country = "SAO TOME AND PRINCIPE"

                text = text[0].split()
                text = [country] + text

                list_file.write(str(text))

    print("Finished scraping text")
