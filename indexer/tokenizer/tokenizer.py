import unidecode
import re

TERMS_FILE_NAME = "terminos.txt"
STATS_FILE_NAME = "estadisticas.txt"
FREQ_FILE_NAME = "frecuencias.txt"
TOKEN_MAX_LEN = 30
TOKEN_MIN_LEN = 2
SPACE = " "
NUMBER_REGEX = r"(?<![a-zA-Z])\d+((\.|,)\d+)?(?![a-zA-Z])"  # r"( |\n)+[0-9]+"
ACRONYMS_ABBREVIATIONS_REGEX = r"([A-Z]([a-zA-Z]*)\.)+"
MAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
#  from a response in https://stackoverflow.com/questions/6718633/python-regular-expression-again-match-url
URL_REGEX = r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:.,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"
NAME_REGEX = r"[A-Z][a-záéóúí]+( [A-Z][a-záéóúí]+)+"
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


def tokenizar_con_reglas(line: str) -> [str]:
    tokens = []
    abreviaturas = get_abreviaturas(line)
    mails_y_urls = get_mails_and_urls(line)
    numeros = get_numeros(line)
    nombres = get_names(line)

    tokens.extend(tokenizar(line))
    tokens.extend(abreviaturas)
    tokens.extend(mails_y_urls)
    tokens.extend(numeros)
    tokens.extend(nombres)
    return tokens


def sacar_palabras_vacias(lista_tokens: [str], lista_vacias: [str]):
    return [token for token in lista_tokens if token not in lista_vacias]


def get_abreviaturas(string: str) -> [str]:
    return extract_by_rule(string, ACRONYMS_ABBREVIATIONS_REGEX)


def get_mails_and_urls(string: str) -> [str]:
    tokens = extract_by_rule(string, MAIL_REGEX)
    tokens.extend(extract_by_rule(string, URL_REGEX))
    return tokens


def get_names(string: str) -> [str]:
    return extract_by_rule(string, NAME_REGEX)


def get_numeros(string: str) -> [str]:
    return extract_by_rule(string, NUMBER_REGEX)


def extract_by_rule(string: str, rule: str) -> [str]:
    tokens = []
    for match in re.finditer(rule, string):
        token = match.group(0)
        if TOKEN_MIN_LEN <= len(token) <= TOKEN_MAX_LEN:
            tokens.append(token)
    return tokens

