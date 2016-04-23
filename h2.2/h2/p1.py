#coding: utf-8

import sys
import json

class Rarewords:
	def __init__(self):
		self.counts={}
		self.rare_words=[]
		self.threshold = 5
		self.vocab = set()

	def show(self):
		for word in self.rare_words:
			print word
	def count(self, tree):
		symbol = tree[0]
		if len(tree) == 3:
			self.count(tree[1])
			self.count(tree[2])
		elif len(tree) == 2:
			self.counts.setdefault(tree[1], 0)
			self.counts[tree[1]] += 1
			self.vocab.add(tree[1])
	def vocab_out(self, vocab_file):
		vocab = vocab_file
		for word in self.vocab:
			vocab.write(word+"\n")
	def get_rare_words(self):
		for word, count in self.counts.items():
			if count < self.threshold:
				self.rare_words.append(word)
	def output(self,tree, output_file):
		out = output_file
		out.write("[\"")
		if len(tree) == 2:
			if tree[1] in self.rare_words:
				out.write(tree[0]+"\", "+"\"_RARE_\"]")
			else:
				out.write(tree[0]+"\", "+"\""+tree[1]+"\"]")
		elif len(tree) == 3:
			out.write(tree[0]+"\",")
			self.output(tree[1], output_file)
			out.write(", ")
			self.output(tree[2], output_file)
			out.write("]")
def main(parse_file, output_file, vocab_file):
	counter = Rarewords()
	out = open(output_file, "a+")
	for l in open(parse_file):
		t = json.loads(l)
		counter.count(t)
	counter.vocab_out(vocab_file)
	counter.get_rare_words()
	for l in open(parse_file):
		t = json.loads(l)
		counter.output(t, out)
		out.write('\n')
	counter.show()

if __name__=="__main__":
	parse_file = sys.argv[1]
	output_file = sys.argv[2]
	vocab_file = open("vocab.list", "w")
 	main(parse_file, output_file, vocab_file)


			