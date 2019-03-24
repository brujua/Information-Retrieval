import unidecode
import re
TERMS_FILE_NAME = "terminos.txt"
STATS_FILE_NAME = "estadisticas.txt"
FREQ_FILE_NAME = "frecuencias.txt"
TOKEN_MAX_LEN = 12
TOKEN_MIN_LEN = 2
SPACE = " "
NUMBER_REGEX = "( |\n)[0-9]+"
SPECIAL_CHARS = [
    ".",
    "!",
    "=",
    "+",
    "-",
    "/",
    ",",
    ":",
    ";",
    "'",
    "{",
    "}",
    "[",
    "]",
    "?",
    "¿",
    ">",
    "<",
    "/",
    '\\',
    "|",
    "\"",
    "\'",
    "_",
    "`",
    "~",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
    "(",
    ")",
    "\n",
    "\t"
]


def tokenizar(line: str):
    line = line.casefold()
    for char in SPECIAL_CHARS:
        line = line.replace(char, SPACE)
    line = unidecode.unidecode(line)  # remove accents
    line = re.sub(NUMBER_REGEX, SPACE, line)  # remove numbers
    return [token for token in line.split() if TOKEN_MIN_LEN <= len(token) <= TOKEN_MAX_LEN]


def sacar_palabras_vacias(lista_tokes: [str], lista_vacias: [str]):
    return [token for token in lista_tokes if token not in lista_vacias]
