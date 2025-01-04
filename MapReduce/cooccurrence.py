#!/usr/bin/env python3

import collections
import heapq
import re

import simplemr

WORD_RE = re.compile(r'\w+')

with open("stopwords") as f:
    STOPWORDS = set(f.read().split())

class PairCoOccurrence(simplemr.MapReduceCombine):
    def __init__(self, window):
        self.window = window
    
    def map(self, line):
        line = line.lower()
        words = [w for w in WORD_RE.findall(line) if w not in STOPWORDS]
        for i, w1 in enumerate(words):
            for w2 in words[i+1:i + self.window]:
                pair = (w1, w2) if w1 < w2 else (w2, w1)
                yield pair, 1
        
    def combine(self, k, vs):
        yield k, sum(vs)

    def reduce(self, k, vs):
        yield k, sum(vs)
        

class StripesCoOccurrence(simplemr.MapReduceCombine):
    def __init__(self, window):
        self.window = window
    
    def map(self, line):
        line = line.lower()
        words = [w for w in WORD_RE.findall(line) if w not in STOPWORDS]
        # res = collections.defaultdict(collections.Counter)
        res = {w: collections.Counter() for w in words}
        for i, w1 in enumerate(words):
            for w2 in words[i+1:i+self.window]:
                if w1 < w2:
                    res[w1][w2] += 1
                else:
                    res[w2][w1] += 1
        return res.items()
        # equivalent to
        # for k, v in res.items():
        #     yield k, v
        # also equivalent to
        # yield from res.items()
        # # hints:
        # - use collections.Counter()
        # - to iterate on all (key, value) pairs of a dictionary or
        #   collections.Counter, use the .items() method
    
    def combine(self, k, counters):
        # hint: have a look at the .update() method of collections.Counter()
        res = collections.Counter()
        for c in counters:
            res.update(c)
        yield k, res

    def reduce(self, w1, counters):
        res = collections.Counter()
        for c in counters:
            res.update(c)
        for w2, count in res.items():
            yield (w1, w2), count

if __name__ == '__main__':
    print("Pairs")
    with open('mobydick.txt') as f:
        print(heapq.nlargest(10, PairCoOccurrence(4).run(f), key=simplemr.second))

    print("Stripes")
    with open('mobydick.txt') as f:
        output = StripesCoOccurrence(4).run(f)
        print(heapq.nlargest(10, output, key=simplemr.second))

