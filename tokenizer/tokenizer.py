import sys
from os import listdir
from os.path import isdir

TOKEN_MAX_LEN = 12
TOKEN_MIN_LEN = 2
SPACE = " "
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
    "\\",
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
    ")"
]


def get_files(path: str) -> [str]:
    """ recursively finds all the files within a directory and returns their path in a list.

    Parameters
    ----------
    path: the path of the directory to do the search

    Returns
    -------
    list
        a list of strings corresponding to the path of each file in the specified path
    """
    if not isdir(path):
        return [path]  # its expected to return a list each time even if its a single element
    return [file for fileOrDir in listdir(path) for file in get_files(path + '/' + fileOrDir)]
    # return list of each file returned by the recursive call getFiles(fileOrDir) on
    # each fileOrDir in listdir(path)


def tokenizar(line: str):
    line = line.casefold()
    for char in SPECIAL_CHARS:
        line = line.replace(char, SPACE)
    return [token for token in line.split() if TOKEN_MIN_LEN <= len(token) <= TOKEN_MAX_LEN]


def calculate_len_mean(terms: dict):
    total = 0
    for string in terms.keys():
        total += len(string)
    return total / len(terms)


def calculate_single_term_freq(terms: dict):
    count = 0
    for term in terms:
        corpus_freq, __ = terms[term]
        if corpus_freq == 1:
            count += 1
    return count


def main(*args):
    remove_empty_words = (len(args) == 2)
    if remove_empty_words:
        empty_words_file = args[1]
    corpus_dir = args[0]
    terms = {}  # in the form of {token: (corpus_freq, document_freq), }
    files = get_files(corpus_dir)
    file_count = 0
    token_count = 0
    largest_token_count = 0
    largest_term_count = 0
    smallest_token_count = -1
    smallest_term_count = 0
    for fileI in files:
        with open(fileI, errors="ignore") as file:
            file_count += 1
            tokens = []
            file_terms = []
            lines = file.readlines()
            for line in lines:
                tokens.extend(tokenizar(line))
            for token in tokens:
                token_count += 1
                if token not in terms:
                    terms[token] = 1, 1
                    file_terms.append(token)
                else:
                    corpus_freq, doc_freq = terms[token]
                    if token in file_terms:
                        terms[token] = (corpus_freq + 1, doc_freq)
                    else:
                        file_terms.append(token)
                        terms[token] = corpus_freq + 1, doc_freq + 1

            if len(tokens) > largest_token_count:
                largest_token_count = len(tokens)
                largest_term_count = len(file_terms)
            if len(tokens) < smallest_token_count or smallest_token_count == -1:
                smallest_token_count = len(tokens)
                smallest_term_count = len(file_terms)

    ordered_terms = sorted(terms, key=terms.get, reverse=True)

    # Terms
    with open("terminos.txt", 'w') as terms_file:
        for term in ordered_terms:
            corpus_freq, doc_freq = terms[term]
            terms_file.write(str(term) + "\t" + str(corpus_freq) + "\t" + str(doc_freq) + "\n")

    # Statistics
    term_count = len(terms)
    token_mean = token_count / file_count
    term_mean = term_count / file_count
    term_len_mean = calculate_len_mean(terms)
    one_freq_term_count = calculate_single_term_freq(terms)
    with open("estadisticas.txt", "w") as stats_file:
        stats_file.write(str(file_count) + "\n")
        stats_file.write(str(token_count) + "\t" + str(term_count) + "\n")
        stats_file.write(str(token_mean) + "\t" + str(term_mean) + "\n")
        stats_file.write(str(term_len_mean) + "\n")
        stats_file.write(str(smallest_token_count) + "\t" + str(smallest_term_count) + "\t"
                         + str(largest_token_count) + "\t" + str(largest_term_count) + "\n")
        stats_file.write(str(one_freq_term_count) + "\n")


if __name__ == '__main__':
    main(*sys.argv[1:])
