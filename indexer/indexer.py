import sys
import uuid
from tqdm import tqdm
from utils import get_files
from typing import List, Callable

from tokenizer.tokenizer import tokenizar
from tokenizer.tokenizer import sacar_palabras_vacias
from tokenizer.tokenizer import tokenizar_con_reglas
from tokenizer.tokenizer import tokenizar_con_stemming

TERMS_FILE_NAME = "terminos.txt"
STATS_FILE_NAME = "estadisticas.txt"
FREQ_FILE_NAME = "frecuencias.txt"
tokenizer_function = tokenizar


def get_len_mean(terms: dict) -> int:
    """
    :param terms: dictionary with the form of {'term' : (corpus_f, doc_f), ..}
    :return: the integer mean of the length of the terms in the dictionary
    """
    if len(terms) > 0:
        total = 0
        for string in terms.keys():
            total += len(string)
        return total // len(terms)


def get_single_term_freq(terms: dict) -> int:
    """
    Calculates the number of terms with their corpus frequency in 1
    :param terms: dictionary with the form of {'term' : (corpus_f, doc_f), ..}
    :return: the count of the 1 freq terms
    """
    count = 0
    for term in terms:
        corpus_freq, __ = terms[term]
        if corpus_freq == 1:
            count += 1
    return count


def enable_rule_based_tokenization():
    global tokenizer_function
    tokenizer_function = tokenizar_con_reglas


def enable_stemmed_tokenization():
    global tokenizer_function
    tokenizer_function = tokenizar_con_stemming


def main(*args):
    empty_words = []
    remove_empty_words = (len(args) == 2)
    if remove_empty_words:
        empty_words_file = args[1]
        with open(empty_words_file, encoding="utf-8") as file:
            empty_words = tokenizer_function(file.read())

    corpus_dir = args[0]
    terms = {}  # in the form of {token: (corpus_freq, document_freq), }
    files = get_files(corpus_dir)
    file_count = 0
    token_count = 0
    largest_token_count = 0
    largest_term_count = 0
    smallest_token_count = -1
    smallest_term_count = 0
    progress_bar = tqdm(total=len(files), unit="file")
    for fileI in files:
        with open(fileI, encoding="utf-8", errors="ignore") as file:
            file_count += 1
            tokens = []
            file_terms = []
            file_str = file.read()
            new_tokens = tokenizer_function(file_str)
            if remove_empty_words:
                new_tokens = sacar_palabras_vacias(new_tokens, empty_words)
            tokens.extend(new_tokens)
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
            progress_bar.update(1)

            if len(tokens) > largest_token_count:
                largest_token_count = len(tokens)
                largest_term_count = len(file_terms)
            if len(tokens) < smallest_token_count or smallest_token_count == -1:
                smallest_token_count = len(tokens)
                smallest_term_count = len(file_terms)

    ordered_terms = sorted(terms, key=terms.get, reverse=True)
    progress_bar.close()
    # Terms
    with open(TERMS_FILE_NAME, 'w') as terms_file:
        for term in ordered_terms:
            corpus_freq, doc_freq = terms[term]
            terms_file.write(str(term) + "\t" + str(corpus_freq) + "\t" + str(doc_freq) + "\n")

    # Statistics
    term_count = len(terms)
    token_mean = token_count // file_count
    term_mean = term_count // file_count
    term_len_mean = get_len_mean(terms)
    one_freq_term_count = get_single_term_freq(terms)
    with open(STATS_FILE_NAME, "w") as stats_file:
        stats_file.write(str(file_count) + "\n")
        stats_file.write(str(token_count) + "\t" + str(term_count) + "\n")
        stats_file.write(str(token_mean) + "\t" + str(term_mean) + "\n")
        stats_file.write(str(term_len_mean) + "\n")
        stats_file.write(str(smallest_token_count) + "\t" + str(smallest_term_count) + "\t"
                         + str(largest_token_count) + "\t" + str(largest_term_count) + "\n")
        stats_file.write(str(one_freq_term_count) + "\n")

    # 10 most and least frequent terms
    most_freq = ordered_terms[0:10]
    least_freq = ordered_terms[term_count - 10:term_count]
    with open(FREQ_FILE_NAME, "w") as freq_file:
        for term in most_freq:
            corpus_freq, __ = terms[term]
            freq_file.write(term + "\t" + str(corpus_freq) + "\n")
        for term in least_freq:
            corpus_freq, __ = terms[term]
            freq_file.write(term + "\t" + str(corpus_freq) + "\n")


if __name__ == '__main__':
    main(*sys.argv[1:])
