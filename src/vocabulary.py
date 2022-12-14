import numpy as np
import string
from split_label import SplitLabel
import torch
import torch.nn as nn
from glove import read_glove
from global_parser import parser
import random
class Vocabulary:
    UNK_token = 0
    def __init__(self, name, dim):
        self.name = name
        self.word2ind = {}
        self.word2count = {}
        self.word_embeddings = None
        self.word2vec = {}
        self.ind2word = ["#UNK#"]
        self.num_words = 1
        self.stopwords = []
        self.dim = dim

    def read_stop_words(self, path):
        with open(path) as file:
            words = file.read().split("\n")
            words = list(filter(None, words))
            self.stopwords  = words


    def add_word(self, word):
        word = word.lower()
        if word not in self.word2count and word not in self.stopwords:
            self.word2count[word] = 1
            #self.word2vec[word]
        elif word in self.word2count:
            self.word2count[word] += 1

    def add_sentence(self, sentence):
        for word in sentence.split(' '):
            self.add_word(word)

    def set_word_embeddings(self):
        torch.manual_seed(1)
        random.seed(1)
        self.word_embeddings = nn.Embedding(self.num_words, int(self.dim))


    def set_word_vector(self, word_vector):
        self.word2vec = word_vector


    def from_word2vect_wordEmbeddings(self, freeze):
        words = self.word2vec.keys()
        out = []
        for word in words:
            out.append(self.word2vec[word].tolist())
        out = torch.FloatTensor(out)
        self.word_embeddings = nn.Embedding.from_pretrained(out, freeze = freeze)

    def from_word2vect_word2ind(self):
        words = list(self.word2vec.keys())

        for i in range(len(words)):
            self.word2ind[words[i]] = i


    def set_word2vector(self):
        num_eb = self.word_embeddings.weight.detach().numpy()
        words = list(self.word2ind.keys())
        for i in range(len(words)):
            self.word2vec[words[i]] = torch.tensor(num_eb[i,:].tolist())#, requires_grad=True)


    def filter(self, threshold):
        self.word2count = {k: v for k, v in self.word2count.items() if v >= threshold}
        other_words = self.word2count.keys()
        self.ind2word += other_words
        for i in range(len(self.ind2word)):
            self.word2ind[self.ind2word[i]]= i
        self.num_words = len(self.ind2word)
        self.set_word_embeddings()
        self.set_word2vector()

    def get_word_embeddings(self):
        return self.word_embeddings

    def get_word_vector(self, word):

        return self.word2vec[word]

    def get_word2vector(self):
        return self.word2vec


    def get_sentence_ind(self, sentence, method):
        output = []
        if method == "Bilstm":
            for word in sentence.split(' '):
                word = word.lower()
                if word in self.word2ind:
                    output.append(int(self.word2ind[word]))
                else:
                    output.append(int(self.word2ind["#UNK#"]))
        else:
            for word in sentence.split(' '):
                word = word.lower()
                if word not in string.punctuation:
                    if word in self.word2ind:
                        output.append(int(self.word2ind[word]))
                    else:
                        output.append(int(self.word2ind["#UNK#"]))


        output = torch.tensor(output, dtype=torch.long)

        return output

    def setup(self, cor):
        corpus = SplitLabel(cor)
        features,_ = corpus.generate_sentences()
        self.read_stop_words('../data/stopwords.txt')
        for s in features:
            self.add_sentence(s)
        self.filter(int(parser['Hyperparameters']['vocab_threshold']))
