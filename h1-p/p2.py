#coding: utf-8

import sys
import re
import math
from collections import defaultdict
from count_freqs import Hmm

rare_word_tag = "_RARE_"
rare_word_threshold = 5

def process_rare_words(corpus_filename, output_filename, rare_words):
	corpus_file = file(corpus_filename, "r")
	output_file = file(output_filename, "w")

	l = corpus_file.readline()
	while l:
		line = l.strip()
		if line:
			fields = line.split(' ')
			word = fields[0]
			tag = fields[-1]
			if word in rare_words:
				output_file.write("%s %s\n" % (rare_word_tag, tag))
			else:
				output_file.write("%s %s\n" % (word, tag))
		else:
			output_file.write("\n")
		l = corpus_file.readline()

class Rare(Hmm):
	def __init__(self, n = 3):
		super(Rare, self).__init__(n)
		self.word_counts = defaultdict(int)
		self.rare_words = []
		
	def train(self,corpus_file):
		super(Rare, self).train(corpus_file)
		self.count_words()
		self.get_rare_words()

	def count_words(self):
		for word, tag in self.emission_counts:
			self.word_counts[word] += self.emission_counts[(word, tag)]
	def get_rare_words(self):
		for word in self.word_counts:
			if self.word_counts[word] < rare_word_threshold:
				self.rare_words.append(word)

def get_sentence_iterator(corpus_filename):
	corpus_file = file(corpus_filename, "r")
	current_sentence = []

	l = corpus_file.readline()
	while l:
		line = l.strip()
		if line:
			current_sentence.append(line)
		else: #None
			if current_sentence:
				yield current_sentence
				current_sentence = []
		l = corpus_file.readline()
	if current_sentence:
		yield current_sentence

class Viterbi(Hmm):
	def __init__(self, n = 3):
		super(Viterbi, self).__init__(n)
		self.trigram_para = defaultdict(float)
		self.emission_para = defaultdict(float)
		self.word_counts = defaultdict(int)
		self.tag_counts = defaultdict(int)
		self.tags = set()
		self.words = set()

	def train(self, corpus_file):
		super(Viterbi, self).train(corpus_file)
		self.get_word_tag_counts()
		self.get_emission_para()
		self.get_trigram_para()

	def get_word_tag_counts(self):
		for word, tag in self.emission_counts:
			self.word_counts[word] += self.emission_counts[(word, tag)]
			self.tag_counts[tag] += self.emission_counts[(word, tag)]
			self.tags.add(tag)
			self.words.add(word)

	#e(x|y)
	def get_emission_para(self):
		for word, tag in self.emission_counts:
			self.emission_para[(word, tag)] = float(self.emission_counts[(word, tag)])/ float(self.tag_counts[tag])

	#q(y_i|y_(i-1), y_(i-2))
	def get_trigram_para(self):
		#若是取1-gram的ngram_count，那么需要用tag为ngram_counts[0][(tag3,)] 括号必须有，存储时候是这样存
		for (tag1, tag2, tag3) in self.ngram_counts[2]:
			self.trigram_para[(tag1, tag2,tag3)] = float(self.ngram_counts[2][(tag1, tag2, tag3)]) / float(self.ngram_counts[1][(tag1, tag2)])
			#print ("%f %f %f\n" % (self.ngram_counts[2][(tag1, tag2, tag3)], self.ngram_counts[1][(tag1, tag2)], self.trigram_para[(tag1, tag2, tag3)]))
		#print(self.trigram_para[("*", "*", "O")])

	def viterbi_algorithm(self, test_corpus_filename, output_filename):
		output_file = file(output_filename, "w")

		sentence_iterator = get_sentence_iterator(test_corpus_filename)
		for sentence in sentence_iterator:
			current_sentence = []
			current_sentence.extend(sentence)
			sentence_len = len(current_sentence)

			replace_sentence = ['' for i in xrange(sentence_len)]
			for i in xrange(sentence_len):
				if current_sentence[i] not in self.words:
					replace_sentence[i] = rare_word_tag
				else:
					replace_sentence[i] = current_sentence[i]
			
			fpi = defaultdict(float)
			bp = defaultdict(str)
			y_tag = ['' for i in xrange(sentence_len)]

			fpi[(0, "*", "*" )] = 1.0
			#fpi(1,u,v)
			for v in self.tags:
				fpi[(1,"*", v)] = float(fpi[(0,"*", "*")] * self.trigram_para[("*", "*", v)] * self.emission_para[(replace_sentence[0], v)])
				bp[(1, "*", v)] = "*"
			#fpi(2,u,v)
			for u in self.tags:
				for v in self.tags:
					fpi[(2, u, v)] = float(fpi[(1, "*", u)] * self.trigram_para[("*", u, v)] * self.emission_para[(replace_sentence[1], v)])
					bp[(2, u, v)] = "*"
			
			for k in xrange(3, sentence_len+1):
				for u in self.tags:
					for v in self.tags:
						current_max = -100
						current_max_tag = ''
						for w in self.tags:
							temp = float(fpi[(k-1, w, u)] * self.trigram_para[(w,u,v)] * self.emission_para[(replace_sentence[k-1], v)])
							if temp > current_max:
								current_max = temp
								current_max_tag = w
						fpi[(k, u, v)] = current_max
						bp[(k, u, v)] = current_max_tag

			current_max = -100
			for u in self.tags:
				for v in self.tags:
					temp = float(fpi[(sentence_len, u, v)] * self.trigram_para[(u, v, "STOP")])
					if temp > current_max:
						current_max = temp
						y_tag[sentence_len - 2] = u
						y_tag[sentence_len - 1] = v

			for k in xrange(sentence_len - 3, -1, -1):
				y_tag[k] = bp[(k+3, y_tag[k+1], y_tag[k+2])]

			for k in xrange(sentence_len):
				output_file.write("%s %s\n" % (current_sentence[k], y_tag[k]))
			output_file.write("\n")


def main():
	train_data_filename = "gene.train"
	train_replace_filename = "gene.p2.train"
	test_data_filename = "gene.test"
	test_output_filename = "gene_test.p2.out"

	rare_model = Rare(3)
	rare_model.train(file(train_data_filename, "r"))
	rare_words = rare_model.rare_words

	process_rare_words(train_data_filename, train_replace_filename, rare_words)

	hmm_model = Viterbi(3)
	hmm_model.train(file(train_replace_filename, "r"))
	hmm_model.viterbi_algorithm(test_data_filename, test_output_filename)

if __name__ == "__main__":
	main()


