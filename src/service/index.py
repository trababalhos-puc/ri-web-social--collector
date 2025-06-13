import json
import math
import pickle
import re
import time
import unicodedata
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import nltk
from nltk import tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("rslp", quiet=True)
nltk.download("punkt_tab", quiet=True)


class TextProcessor:
    def __init__(self, language="portuguese"):
        self.language = language
        self.stopwords = set(stopwords.words(language))
        self.stemmer = RSLPStemmer()

    @staticmethod
    def normalize_text(text):
        """Remove acentos, pontuação e converte para minúsculas"""
        text = text.lower()
        text = (
            unicodedata.normalize("NFKD", text)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\d+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def tokenize(self, text):
        """Tokeniza o texto"""
        return tokenize.word_tokenize(text, language=self.language)

    def remove_stopwords(self, tokens):
        """Remove stopwords"""
        return [token for token in tokens if token.lower() not in self.stopwords]

    def apply_stemming(self, tokens):
        """Aplica stemming"""
        return [self.stemmer.stem(token) for token in tokens]

    @staticmethod
    def create_ngrams(tokens, n=2):
        """Cria n-gramas a partir dos tokens"""
        return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]

    def create_shingles(self, tokens, max_n=3):
        """Cria shingles (1 até max_n gramas)"""
        shingles = []
        for n in range(1, max_n + 1):
            shingles.extend(self.create_ngrams(tokens, n))
        return shingles

    def process_text(
        self,
        text,
        remove_stop=True,
        apply_stem=True,
        create_grams=False,
        n_gram=2,
        create_shing=False,
        max_n=3,
    ):
        """Processa o texto aplicando todas as transformações"""
        normalized_text = self.normalize_text(text)
        tokens = self.tokenize(normalized_text)

        if remove_stop:
            tokens = self.remove_stopwords(tokens)

        if apply_stem:
            tokens = self.apply_stemming(tokens)

        result = {"tokens": tokens}

        if create_grams:
            result["ngrams"] = self.create_ngrams(tokens, n_gram)

        if create_shing:
            result["shingles"] = self.create_shingles(tokens, max_n)

        return result


class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.documents = {}
        self.tf = defaultdict(Counter)
        self.df = Counter()
        self.vocabulary = set()
        self.total_docs = 0

    def add_document(self, doc_id, tokens):
        """Adiciona um documento ao índice invertido"""
        self.documents[doc_id] = len(tokens)
        self.total_docs += 1
        term_count = Counter(tokens)

        for term, count in term_count.items():
            self.index[term].append((doc_id, count))
            self.tf[doc_id][term] = count
            self.df[term] += 1
            self.vocabulary.add(term)

    def get_postings(self, term):
        """Retorna a lista de postings para um termo"""
        return self.index.get(term, [])

    def get_term_frequency(self, term, doc_id):
        """Retorna a frequência de um termo em um documento"""
        return self.tf.get(doc_id, Counter()).get(term, 0)

    def get_document_frequency(self, term):
        """Retorna a frequência de documentos que contém o termo"""
        return self.df.get(term, 0)

    def get_idf(self, term):
        """Calcula o IDF (Inverse Document Frequency) para um termo"""
        return math.log10(self.total_docs / (1 + self.get_document_frequency(term)))

    def get_tf_idf(self, term, doc_id):
        """Calcula o TF-IDF para um termo em um documento"""
        tf = self.get_term_frequency(term, doc_id)
        idf = self.get_idf(term)
        return tf * idf

    def search(self, query_terms):
        """Busca documentos que contêm todos os termos da consulta"""
        if not query_terms:
            return []

        result = set(doc_id for doc_id, _ in self.get_postings(query_terms[0]))
        for term in query_terms[1:]:
            result.intersection_update(doc_id for doc_id, _ in self.get_postings(term))

        return list(result)

    def rank_search(self, query_terms):
        """Busca documentos e retorna ranking baseado em TF-IDF"""
        if not query_terms:
            return []

        docs = set()
        for term in query_terms:
            docs.update(doc_id for doc_id, _ in self.get_postings(term))

        scores = {}
        for doc_id in docs:
            score = sum(self.get_tf_idf(term, doc_id) for term in query_terms)
            scores[doc_id] = score

        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked_docs

    def save_index(self, filepath):
        """Salva o índice no disco"""
        with open(filepath, "wb") as f:
            pickle.dump(
                {
                    "index": dict(self.index),
                    "documents": self.documents,
                    "tf": dict(self.tf),
                    "df": self.df,
                    "vocabulary": self.vocabulary,
                    "total_docs": self.total_docs,
                },
                f,
            )

    def load_index(self, filepath):
        """Carrega o índice do disco"""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
            self.index = defaultdict(list, data["index"])
            self.documents = data["documents"]
            self.tf = defaultdict(Counter, data["tf"])
            self.df = data["df"]
            self.vocabulary = data["vocabulary"]
            self.total_docs = data["total_docs"]

    def get_stats(self):
        """Retorna estatísticas sobre o índice"""
        return {
            "num_documents": self.total_docs,
            "vocabulary_size": len(self.vocabulary),
            "mean_terms_per_doc": sum(self.documents.values())
            / max(1, self.total_docs),
            "postings_size": sum(len(postings) for postings in self.index.values()),
        }


class IndexAnalyzer:
    def __init__(self, processor, documents):
        self.processor = processor
        self.documents = documents
        self.indices = {}
        self.stats = {}
        self.times = {}
        self.memory_usage = {}

    def create_index(self, name, params=None):
        """Cria um índice com os parâmetros especificados"""
        t0 = time.time()
        default_params = {
            "remove_stop": True,
            "apply_stem": True,
            "create_grams": False,
            "n_gram": 2,
            "create_shing": False,
            "max_n": 3,
        }

        if params:
            params = {**default_params, **params}
        else:
            params = default_params

        index = InvertedIndex()

        for doc_id, doc_text in self.documents.items():
            result = self.processor.process_text(
                doc_text,
                remove_stop=params["remove_stop"],
                apply_stem=params["apply_stem"],
                create_grams=params["create_grams"],
                n_gram=params["n_gram"],
                create_shing=params["create_shing"],
                max_n=params["max_n"],
            )

            if params["create_grams"] and not params["create_shing"]:
                index.add_document(doc_id, result["ngrams"])
            elif params["create_shing"]:
                index.add_document(doc_id, result["shingles"])
            else:
                index.add_document(doc_id, result["tokens"])

        self.indices[name] = index
        self.stats[name] = index.get_stats()
        self.times[name] = time.time() - t0
        index_size = len(pickle.dumps(index.index))
        self.memory_usage[name] = index_size

        return index

    def compare_indices(self):
        """Compara os diferentes índices criados"""
        if not self.indices:
            print("Nenhum índice foi criado ainda.")
            return

        plt.figure(figsize=(12, 8))
        plt.subplot(2, 2, 1)
        plt.bar(self.times.keys(), self.times.values())
        plt.title("Tempo de Indexação")
        plt.ylabel("Tempo (s)")
        plt.xticks(rotation=45)

        plt.subplot(2, 2, 2)
        vocab_sizes = [stats["vocabulary_size"] for stats in self.stats.values()]
        plt.bar(self.stats.keys(), vocab_sizes)
        plt.title("Tamanho do Vocabulário")
        plt.ylabel("Número de Termos")
        plt.xticks(rotation=45)

        plt.subplot(2, 2, 3)
        mean_sizes = [stats["mean_terms_per_doc"] for stats in self.stats.values()]
        plt.bar(self.stats.keys(), mean_sizes)
        plt.title("Média de Termos por Documento")
        plt.ylabel("Número de Termos")
        plt.xticks(rotation=45)

        plt.subplot(2, 2, 4)
        plt.bar(
            self.memory_usage.keys(),
            [size / 1024 / 1024 for size in self.memory_usage.values()],
        )
        plt.title("Tamanho do Índice")
        plt.ylabel("Tamanho (MB)")
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig("index_comparison.png")
        plt.close()

        print("\nEstatísticas dos Índices:")
        for name, stats in self.stats.items():
            print(f"\n{name}:")
            print(f"  Documentos: {stats['num_documents']}")
            print(f"  Tamanho do Vocabulário: {stats['vocabulary_size']}")
            print(f"  Média de Termos por Documento: {stats['mean_terms_per_doc']:.2f}")
            print(f"  Tamanho do Índice: {self.memory_usage[name]/1024/1024:.2f} MB")
            print(f"  Tempo de Indexação: {self.times[name]:.2f} s")

    def test_search(self, query, top_n=5):
        """Testa a busca em todos os índices criados"""
        if not self.indices:
            print("Nenhum índice foi criado ainda.")
            return

        print(f"\nResultados da busca para: '{query}'")

        for name, index in self.indices.items():
            processed_query = self.processor.process_text(query)

            start_time = time.time()
            results = index.rank_search(processed_query["tokens"])
            end_time = time.time()

            print(f"\n{name}:")
            print(f"  Tempo de busca: {(end_time - start_time)*1000:.2f} ms")
            print(f"  Documentos encontrados: {len(results)}")

            if results:
                print(f"  Top {min(top_n, len(results))} resultados:")
                for i, (doc_id, score) in enumerate(results[:top_n]):
                    print(f"    {i+1}. Documento {doc_id} (score: {score:.4f})")
            else:
                print("  Nenhum documento encontrado.")

    def search_top_5(self, query, top_n=5):
        """Retorna lista com (nome_do_indice, resultados_ranked) para a query."""
        if not self.indices:
            print("Nenhum índice foi criado ainda.")
            return []

        results = []
        processed = self.processor.process_text(query)["tokens"]
        for name, index in self.indices.items():
            ranked = index.rank_search(processed)[:top_n]
            results.append((name, ranked))
        return results


class Index:
    def __init__(self, json_file_path=None, documents=None):
        self.json_file_path = json_file_path
        self.documents = documents or {}

    def load_from_json(self):
        """
        Carrega documentos a partir do arquivo JSON no novo formato.

        Returns:
            Dict[str, str]: Dicionário de documentos (id -> texto)
        """
        if not self.json_file_path:
            print("Nenhum arquivo JSON especificado.")
            return self.documents

        try:
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            documents = {}
            doc_id = 1

            for date_key, date_content in data.get("ipea", {}).items():
                for subdir_name, subdir_content in date_content.items():
                    for file_name, file_info in subdir_content.items():
                        if isinstance(file_info, dict) and "content" in file_info:
                            doc_path = f"{date_key}/{subdir_name}/{file_name}"
                            content = file_info.get("content", "")
                            documents[doc_path] = content
                            doc_id += 1
                        elif isinstance(file_info, str):
                            doc_path = f"{date_key}/{subdir_name}/{file_name}"
                            documents[doc_path] = "Conteúdo não disponível"
                            doc_id += 1

            print(f"Carregados {len(documents)} documentos do arquivo JSON.")
            self.documents = documents
            return documents

        except Exception as e:
            print(f"Erro ao carregar o arquivo JSON: {e}")
            return self.documents

    def start(self):
        """
        Inicia o processo de indexação.

        Returns:
            IndexAnalyzer: O analisador de índices configurado.
        """
        if self.json_file_path and not self.documents:
            self.load_from_json()

        if not self.documents:
            print("Nenhum documento para indexar.")
            return None

        processor = TextProcessor()
        analyzer = IndexAnalyzer(processor, self.documents)
        analyzer.create_index("básico")

        analyzer.create_index(
            "sem_stopwords", {"remove_stop": True, "apply_stem": False}
        )

        analyzer.create_index("com_stemming", {"remove_stop": True, "apply_stem": True})

        analyzer.create_index(
            "bigramas",
            {
                "remove_stop": True,
                "apply_stem": True,
                "create_grams": True,
                "n_gram": 2,
            },
        )

        analyzer.create_index(
            "shingles",
            {"remove_stop": True, "apply_stem": True, "create_shing": True, "max_n": 3},
        )

        return analyzer

