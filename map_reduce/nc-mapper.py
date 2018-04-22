import nltk, re, sys
import fileinput
from collections import Counter

def to_after(tokens, reserved='about'):
    def to_after_token(token):
        token = token.replace('\u3000', ' ')
        if token == ' ': return ''
        
        if token.endswith('-]'):
            return None
        
        # 保留字邏輯區，但是可能有誤，像是 is+} 可能抓到 his+}
        elif reserved and (token.endswith(reserved + '+}') or token.startswith('[-' + reserved)):
            # 丟掉多於一個單字的，目前是 before/after 都丟
            return token[token.rfind('>>')+2:-2] if ' ' in token else token
        
        elif token.endswith('+}'):
            return token[token.rfind('>>')+2:-2]  if token.startswith('[-') else token[2:-2]  
        else:
            return token
        
    tokens = [e for token in map(to_after_token, tokens) if token for e in token.split(' ')]
    indices = [i for i, t in enumerate(tokens) if '+}' in t or '[-' in t ]
    return tokens, [-1] + indices + [len(tokens)]

# 擔心有一句包含兩個 about+} 所以換個邏輯
def divide_triedit_noedit(aft_tokens, indices):
    noedit_list, triedit_list = [], []

    segs = zip(indices, indices[1:])
    for i, (start, end) in enumerate(segs):
        if i != 0 and start > 0 and start+1 < indices[-1]:
            triedit_list.append(tuple(aft_tokens[start-1:start+2]))
        noedit_list.append(aft_tokens[start+1:end])
        
    return noedit_list, triedit_list

def get_bigram(tokens):
    return list(nltk.bigrams(tokens))

def get_trigram(tokens):
    return list(nltk.trigrams(tokens))

edit_list = [] # trigram edit
bigrams, trigrams = [], []
    
# for line in open('ef.diff.simplize.despace.txt', 'r', encoding='utf8').readlines():# fileinput.input():
# for line in open('test.txt', 'r', encoding='utf8').readlines():# fileinput.input():
for line in sys.stdin:
    tokens = line.strip().split(' ')

    aft_tokens, indices = to_after(tokens, reserved='about')

    noedit_list, edit_tokens = divide_triedit_noedit(aft_tokens, indices)

    # if edit_tokens:
    #     print(edit_tokens)
    # print(noedit_list)
    # print(triedit_tokens)
    edit_list.extend(edit_tokens)
    # print(edit_list)

    # 會有 [] 出現，若是長度不夠
    for no_edit in noedit_list:
        bigrams.extend(get_bigram(no_edit))
        trigrams.extend(get_trigram(no_edit))
        
uniq_edit = set(edit_list)

def bi_vs_edit(bigram, uniq_edit_list):
    group = set()
    for edit in uniq_edit_list:
        if bigram[0] == edit[0] and bigram[1] == edit[2]:
            group.add(edit)
    return group

def tri_vs_edit(trigram, uniq_edit_list, reserved='about'):
    group = set()
    for edit in uniq_edit_list:
        if edit[0] == trigram[0] and edit[2] == trigram[2]:
            temp = edit[1][2:-2].split('>>')[0] if edit[1].startswith('[-' + reserved) else edit[1]
            if temp == trigram[1]:
                group.add(edit)
    return group

cache = {}
for bi in bigrams:
    if bi in cache:
        print(cache[bi])
        continue

    group = list(bi_vs_edit(bi, uniq_edit))
    if group: 
        line = "%s\t%s" % (' '.join(bi), '\t'.join([' '.join(edit) for edit in group]))
        cache[bi] = line
        print(line)
    
for tri in trigrams:
    if tri in cache:
        print(cache[tri])
        continue
        
    group = list(tri_vs_edit(tri, uniq_edit))
    if group: 
        line = "%s\t%s" % (' '.join(tri), '\t'.join([' '.join(edit) for edit in group]))
        cache[tri] = line
        print(line)

