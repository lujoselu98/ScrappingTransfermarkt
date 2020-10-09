from os import listdir
from os.path import isfile, join


def is_alpha_and_spaces(string):
    return string.replace(' ', '') \
        .replace('-', '') \
        .replace('\'', '') \
        .isalpha()


def onlyfiles(path, extension=""):
    return [f.replace(extension, "") for f in listdir(path) if isfile(join(path, f))]
