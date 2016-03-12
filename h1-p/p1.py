# coding: utf-8

import sys
import re
import math
from count_freqs import Hmm
from collections import defaultdict

rare_word_thread = 5
rare_word_tag = "_RARE_"

def process_rare_words(input_filename, rare_words, output_filename):
    input_file = file(input_filename, "r") #original training file
    output_file = file(output_filename, "w")

    l = input_file.readline()
    while l:
        line = l.strip()
        if line:
            fields = line.split(' ')
            word = fields[0]
            tag = fields[-1]
            if word in rare_words:
                output_file.write('{0} {1}\n'.format(rare_word_tag, tag));
            else:
                output_file.write('{0} {1}\n'.format(word, tag))
        else:
            output_file.write('\n')
        l = input_file.readline()

#继承Hmm
class Rare(Hmm):
    def __init__(self,n=3):
        super(Rare,self).__init__(n)
        self.word_counts = defaultdict(int)
        self.rare_words = []
        self.tags = set()
        self.words = set()
    def train(self, corpus_file):
        super(Rare, self).train(corpus_file)
        self.count_words()
        self.get_rare_words();
    def count_words(self):
        for word, tag in self.emission_counts:
            self.word_counts[word] += self.emission_counts[(word, tag)];
    def get_rare_words(self):
        for word in self.word_counts:
            if self.word_counts[word] < rare_word_thread:
                self.rare_words.append(word);


class Tagger(Hmm):
    def __init__(self, n=3):
        super(Tagger, self).__init__(n)
        self.word_counts = defaultdict(int)
        self.tag_counts = defaultdict(int)
        self.rare_words = []
        self.emission_para = defaultdict(float)
        self.tags = set()
        self.words = set()

    def train(self, corpus_file): #after train, get rare word, word count, emision_para
        super(Tagger, self).train(corpus_file)
        self.count_words()
        self.count_tags()
        self.get_word_tag()
        #self.print_tag()
        #self.get_rara_words()
        self.cal_emission_para()

    def count_words(self):
        for word, tag in self.emission_counts:
            self.word_counts[word] += self.emission_counts[(word, tag)]  
    def count_tags(self):
        for word, tag in self.emission_counts:
            self.tag_counts[tag] += self.emission_counts[(word, tag)];
    def cal_emission_para(self):
        for word, tag in self.emission_counts:
            self.emission_para[(word, tag)] = float(self.emission_counts[(word, tag)]) / float(self.tag_counts[tag])
    #def get_rara_words(self):
    #    for word in self.word_counts:
    #        if self.word_counts[word] < rare_word_thread:
    #            self.rare_words.append(word)
    def get_word_tag(self):
        for word, tag in self.emission_counts:
            self.words.add(word)
            self.tags.add(tag)

    def print_tag(self):
        for tag in self.tags:
            print("%s" % tag)

    def test_data_iterator(self, test_data_filename):
        f = file(test_data_filename, 'r')
        l = f.readline()
        while l:
            line = l.strip()
            if line:
                yield line
            else:
                yield None
            l = f.readline()

    def tag(self, test_data_filename, result_filename):
        output = file(result_filename, "w")

        max_e_rare_y, max_rare_y = -1.0, ''
        for tag in self.tags: #得到unseen word的最大的类标概率的类标
            e = self.emission_para[(rare_word_tag, tag)]
            if e > max_e_rare_y:
                max_e_rare_y, max_rare_y = e, tag

        word_iterator =  self.test_data_iterator(test_data_filename)
        for word in word_iterator:
            max_e, max_y = -1.0, ''
            if word is not None:
                if word == rare_word_tag or word not in self.words:
                    max_y = max_rare_y
                else:
                    for tag in self.tags:
                        e = self.emission_para[(word, tag)]
                        if e > max_e:
                            max_e, max_y = e, tag
                output.write('{0} {1}\n'.format(word, max_y))
            else:
                output.write('\n')

def main():
    train_data_filename = "gene.train"
    train_replace_filename = "gene.p1.train"
    test_data_filename = "gene.test"
    test_output_filenmae = "gene_test.p1.out"

    hmm_model = Rare(3)
    hmm_model.train(file(train_data_filename, 'r'))
    rare_words = hmm_model.rare_words

    process_rare_words(train_data_filename, rare_words, train_replace_filename)

    hmm_rare_model = Tagger(3)
    hmm_rare_model.train(file(train_replace_filename,'r'))
    hmm_rare_model.tag(test_data_filename, test_output_filenmae);

if __name__ == '__main__':
    main()

