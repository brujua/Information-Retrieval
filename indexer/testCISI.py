import sys
import time
from tqdm import tqdm

from tokenizer.tokenizer import tokenizar_con_stemming
from tokenizer.tokenizer import sacar_palabras_vacias
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem.porter import PorterStemmer

FILE_PATH = "CISI.ALL"
DATA_START = ".W"
DATA_END = ".X"
lancaster = LancasterStemmer()
porter = PorterStemmer()

empty_words_porter = []
empty_words_lancaster = []
remove_empty_words = (len(sys.argv) == 2)
if remove_empty_words:
    empty_words_file = sys.argv[1]
    with open(empty_words_file, "r", encoding="utf-8") as file:
        empty_words_porter = tokenizar_con_stemming(file.read(), stemm_algorithm="porter")
    with open(empty_words_file, "r", encoding="utf-8") as file:
        empty_words_lancaster = tokenizar_con_stemming(file.read(), stemm_algorithm="lancaster")
with open(FILE_PATH, "r", encoding="utf-8") as file:
    tokens_porter = []
    tokens_lancaster = []
    terms_porter = {}
    terms_lancaster = {}
    tokenize = False
    lines = file.readlines()
    progress_bar = tqdm(total=len(lines), unit="line")
    for line in lines:
        if line.find(DATA_START) == 0:
            tokenize = True
        if line.find(DATA_END) == 0:
            tokenize = False

        if tokenize:
            tokens_p = tokenizar_con_stemming(line, stemm_algorithm="porter")
            tokens_l = tokenizar_con_stemming(line, stemm_algorithm="lancaster")
            if remove_empty_words:
                tokens_p = sacar_palabras_vacias(tokens_p, empty_words_porter)
                tokens_l = sacar_palabras_vacias(tokens_l, empty_words_lancaster)
            tokens_porter.extend(tokens_p)
            tokens_lancaster.extend(tokens_l)
        progress_bar.update(1)
    progress_bar.close()
    tokens_porter_count = len(tokens_porter)
    tokens_lancaster_count = len(tokens_lancaster)
    for token in tokens_porter:
        terms_porter[token] = terms_porter.get(token, 0) + 1
    for token in tokens_lancaster:
        terms_lancaster[token] = terms_lancaster.get(token, 0) + 1

    lancaster_ordered = sorted(terms_lancaster, key=terms_lancaster.get, reverse=True)
    porter_ordered = sorted(terms_porter, key=terms_porter.get, reverse=True)
    with open("porter-terms", "w") as porter_terms_file:
        for token in porter_ordered:
            porter_terms_file.write(token + "\t" + str(terms_porter[token]) + "\n")
    with open("lancaster-terms", "w") as porter_terms_file:
        for token in lancaster_ordered:
            porter_terms_file.write(token + "\t" + str(terms_lancaster[token]) + "\n")

    lancaster_1_terms = [term for term, value in terms_lancaster.items() if value < 4]
    porter_1_terms = [term for term, value in terms_porter.items() if value < 4]
    with open("Lancaster-Porter-stats.txt", "w") as stats_file:
        stats_file.write("Lancaster: " + str(len(lancaster_1_terms)) + "\n")
        stats_file.write("Porter: " + str(len(porter_1_terms)))

    print(" Tokens count: " + str(tokens_lancaster_count))
    print("Lancaster terms: " + str(len(terms_lancaster)))
    print("Porter terms: " + str(len(terms_porter)))
