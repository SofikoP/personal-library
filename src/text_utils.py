import re


def normalize(text):

    text = text.casefold().replace(".", " ")
    return re.sub(r"\s+", " ", text).strip()