import sys
from collections import Counter, defaultdict

groups = defaultdict(Counter)
# groups = {} # bi/tri: similar pattern
# counts = Counter()

for line in sys.stdin:
    head, count, ngrams = line.strip().split('\t', maxsplit=2)
    ngrams = ngrams.split('\t')
    
    for ngram in ngrams:
        edit, cnt = ngram.split('|')
        groups[(head, int(count))][edit] = int(cnt)


all_ngrams = []
for head, sims in groups.items(): # bi/tri, sims
    head, head_count = head
    scores = { head: head_count }
    for sim, count in sims.items():
        scores[sim] = [count, count / head_count]
    all_ngrams.append(sorted(scores.items(), key=lambda item: len(item[0])))


def sort(temp):
    return sorted(temp, key=lambda item: (item[1][1][1]))

for ngram in sort(all_ngrams):
    for freq in ngram:
        print(freq[0], ': ', freq[1], sep = '')
    print('='*50)
