# coding = utf-8
import sys
import math
from collections import defaultdict

class Hmm(object):
	def __init__(self, n = 3):
		assert n>=2, "n>=2"
		self.n = n
		self.emission_counts = defaultdict(int)
		self.ngram_counts = [defaultdict(int) for i in xrange(self.n)]
		self.all_states = set()

	def train(self, corpus_file):
		ngram_iterator = get_ngrams(get_sentence_iterator(get_corpus_pair_iterator(corpus_file)), self.n)

		#取出每个长度为n的ngram，然后进行统计其中tag组成的1-gram，2-gram，...，n-gram
		for ngram in ngram_iterator:
			tags = tuple([tag for word, tag in ngram])
			for i in xrange(2, self.n + 1):
				self.ngram_counts[i-1][tags[-i:]] += 1
			if ngram[-1][0] is not None:
				self.ngram_counts[0][tags[-1:]] += 1 
				#tags[-1:] 就是最后一个词的tag
				#统计1-gram的时候不考虑最开始的None和最后的None
				self.emission_counts[ngram[-1]] += 1 
			if ngram[-2][0] is None: #最开始的None的部分
				self.ngram_counts[self.n-2][tuple((self.n - 1) * ["*"])] += 1
				#单独考虑一次最开始的n-1个连续None补充的部分的计数
				#用来计算q(y_i|y_(i-2),y_(i-1))的情况, y_(i-1),y(i-2)都为None的时候
	#考虑最开始的n-1个None连在一起的n-1_gram，不考虑小于n-1的None的gram，最后一次None也不考虑1-gram


#得到(word, tag)的pair的iterator
def get_corpus_pair_iterator(corpus_file):
	f = file(corpus_file, "r")
	l = f.readline()
	while l:
		line = l.strip()
		if line:
			fields = line.split(' ')
			tag = fields[-1]
			word = " ".join(fields[:-1])
			yield (word, tag)
		else:
			yield (None, None)
		l = corpus_file.readline()

#将pair对放到sentence的list中
def get_sentence_iterator(corpus_pair_iterator):
	current_sentence = []
	for pair in corpus_iterator:
		if pair == (None, None):
			if current_sentence:
				yield current_sentence
				current_sentence = []
			else:
				sys.stderr.write("empty input")
		else:
			current_sentence.append(pair)
	if current_sentence:
		yield current_sentence

#每个sentence加上头部的(None, "*")和尾部的(None, "STOP")组成新的list，然后得到长度为n的ngram的tuple
def get_ngram(sentence_iterator, n):
	for sentence in sentence_iterator:
		w_boundary = (n-1)*[(None, "*")]
		w_boundary.extend(sentence) #sentence is the list of (word, tag) pair
		w_boundary.append((None, "STOP"))
		ngrams = (tuple(w_boundary[i:i+n]) for i in xrange(len(w_boundary) - n + 1)) 
		#得到最长的ngram的一个tuple的list
		for ngram in ngrams:
			yield ngram


