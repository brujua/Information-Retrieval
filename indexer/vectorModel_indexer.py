import sys
import uuid

import numpy as np
from tqdm import tqdm
from typing import List, Callable, Dict
from math import log2

from classes.Document import Document
from classes.Term import Term
from tokenizer.tokenizer import tokenizar
from tokenizer.tokenizer import sacar_palabras_vacias
from utils import get_files

ERROR_ARGS = "Invalid Arguments. \nUsage: python " + sys.argv[0] + " <corpus-dir> <stop-words-file>"
EXIT_QUERY = "--exit"
MAX_RESULTS = 10
corpus_terms = {}
documents = {}


def main(*args):
    empty_words = get_empty_words(args[1])
    files = get_files(args[0])
    index(files, empty_words)
    while True:
        print("Enter Query: (or type", EXIT_QUERY, " )")
        query = input()
        if query == EXIT_QUERY:
            break
        result_docs = resolve_query(query, empty_words)
        print("Documents: ")
        for doc in result_docs[:MAX_RESULTS]:
            print(doc.file_name)


def index(files: List[str], empty_words: List[str]):
    print("indexing...")
    progress_bar = tqdm(total=len(files), unit="file")
    for file_name in files:
        doc = Document(file_name, {}, uuid.uuid4())
        documents[file_name] = doc
        with open(file_name, encoding="utf-8", errors="ignore") as file:
            tokens = tokenizar(file.read())
            tokens = sacar_palabras_vacias(tokens, empty_words)
            for token in tokens:
                if token in corpus_terms:
                    term = corpus_terms.get(token)
                else:
                    term = Term(token, [], uuid.uuid4())
                    corpus_terms[token] = term
                doc.has_term(term)
                term.found_in(doc)
        progress_bar.update(1)

    calculate_idfs()
    progress_bar.close()


def resolve_query(query: str, empty_words: List[str]) -> List[Document]:
    query_tokens = tokenizar(query)
    query_terms_with_duplicates = sacar_palabras_vacias(query_tokens, empty_words)
    query_terms, query_vector = get_query_vector(query_terms_with_duplicates)
    documents_vectors = get_documents_vectors(query_terms)
    document_similitudes = {}
    for doc, doc_vector in documents_vectors.items():
        document_similitudes[doc] = calculate_similitude(query_vector, doc_vector)
    return sorted(document_similitudes, key=document_similitudes.get, reverse=True)


def get_query_vector(query_terms: List[str]) -> (List[str], List[float]):
    query_term_freqs = {}
    query_terms_aux = []
    vector = []
    max_freq = 1
    for term in query_terms:
        if term in corpus_terms:      # only consider terms that appear on the corpus
            if term not in query_term_freqs:
                query_term_freqs[term] = 1
                query_terms_aux.append(term)
            else:
                query_term_freqs[term] += 1
                if query_term_freqs[term] > max_freq:
                    max_freq = query_term_freqs[term]
    for term in query_terms_aux:
        term_idf = corpus_terms[term].get_idf()
        # Wq = 0.5 + 0.5 + TF / max(TF) * log (N / Ni)
        weight = 0.5 + 0.5 * query_term_freqs[term] / max_freq * term_idf
        vector.append(weight)
    return query_terms_aux, vector


def get_documents_vectors(query_terms: List[str]) -> Dict:
    documents_vectors = {}
    documents_of_interest = []
    for term_name in query_terms:
        for doc in corpus_terms[term_name].documents:
            if doc not in documents_of_interest:
                documents_of_interest.append(doc)
    for doc in documents_of_interest:
        vector = []
        for term_name in query_terms:
            term = corpus_terms[term_name]
            vector.append(doc.get_weight(term))
        documents_vectors[doc] = vector
    return documents_vectors


def calculate_similitude(query_vector: List[float], doc_vector: List[float]):
    #  Angle between vectors = D . Q / |D| * |Q|
    return np.dot(query_vector, doc_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(doc_vector))


def calculate_idfs():
    for term in corpus_terms.values():
        term.set_idf(log2(len(documents) / term.doc_freq))


def get_empty_words(file_name: str):
    with open(file_name, encoding="utf-8") as file:
        return tokenizar(file.read())


if __name__ == '__main__':
    if len(sys.argv) is not 3:
        print(ERROR_ARGS)
    else:
        main(*sys.argv[1:])
