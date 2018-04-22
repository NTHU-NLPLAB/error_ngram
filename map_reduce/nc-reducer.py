import sys
from collections import Counter

groups = {} # bi/tri: similar pattern
counts = Counter()

for line in sys.stdin:
    ngrams = line.strip().split('\t')
    
    for ngram in ngrams:
        counts[ngram] += 1
   
    if ngrams[0] not in groups:
        groups[ngrams[0]] = ngrams[1:]

# sort groups?
        
all_ngrams = []
for key, sims in groups.items(): # bi/tri, sims
    scores = { key: counts[key] }
    for sim in sims:
        scores[sim] = [counts[sim], counts[sim]/counts[key]]
    all_ngrams.append(sorted(scores.items(), key=lambda item: len(item[0])))



def sort(temp):
    return sorted(temp, key=lambda item: (item[1][1][1]))

for ngram in sort(all_ngrams):
    for freq in ngram:
        print(freq[0], ': ', freq[1], sep = '')
    print('='*50)
