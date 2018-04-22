
# coding: utf-8

# In[150]:

import nltk, re
import fileinput
from collections import Counter


# In[151]:

def to_after(tokens, reserved='about'):
    def to_after_token(token):
        token = token.replace('\u3000', ' ')
        if token == ' ': return ''
        
        if token.endswith('-]'):
            return None
        # key part, may happen is+} get his+}
        elif reserved and (token.endswith(reserved + '+}') or token.startswith('[-' + reserved)):
            return token
        elif token.endswith('+}'):
            return token[token.rfind('>>')+2:-2]  if token.startswith('[-') else token[2:-2]  
        else:
            return token
    return [e for token in map(to_after_token, tokens) if token for e in token.split(' ')]

def to_before(tokens, reserved=''):
    def to_before_token(token):
        token = token.replace('\u3000', ' ')
        if token == ' ': return ''
        
        if token.endswith('-]'):
            return token[2:-2]
        elif token.endswith('+}'):
            return token[2:token.rfind('>>')]  if token.startswith('[-') else None
        else:
            return token
    return [ token for token in map(to_before_token, tokens) if token ]


# In[152]:

# to_after(['hello','[-about-]', '[-asdf\u3000asdfccc>>about\u3000qqqq+}', '[-about>>ddd+}', 'asdfdf'], reserved='about')
# # to_before(['hello','[-about-]', '[-asdf>>about+}', '[-vvv>>ddd+}', 'asdfdf'])


# In[153]:

# 擔心有一句包含兩個 about+} 所以換個邏輯
def divide_triedit_noedit(aft_tokens, reserved='about'):
    noedit_list, triedit_list = [[]], []

    for i, tk in enumerate(aft_tokens):
        if '+}' in tk: # reserved word ，應該是不會有 [--] 出現
            if i > 0 and i+1 < len(aft_tokens):
                triedit_list.append(tuple(aft_tokens[i-1:i+2]))
            
            noedit_list.append([])
        else: 
            noedit_list[-1].append(tk)

    return noedit_list, triedit_list


# In[154]:

# divide_triedit_noedit(['hello', '[-asdf>>about+}', 'ddd', 'asdfdf', '[-fff>>about+}', 'asdss'])
# divide_triedit_noedit(['hello', '[-asdf>>about+}', 'ddd', 'asdfdf', 'asdss'])
# divide_triedit_noedit(['hello', '[-about>>ddd+}', 'ddd', 'asdfdf', 'asdss', '[-asdsfas>>about+}'])


# In[155]:

def get_bigram(tokens):
    return list(nltk.bigrams(tokens))

def get_trigram(tokens):
    return list(nltk.trigrams(tokens))


# In[156]:

# get_trigram(['one'])
# get_trigram(['one', 'asd', 'aaa'])


# In[157]:

edit_list = [] # trigram edit
bigrams, trigrams = [], []
    
for line in open('ef.diff.simplize.despace.txt', 'r', encoding='utf8').readlines():# fileinput.input():
# for line in open('test.txt', 'r', encoding='utf8').readlines():# fileinput.input():
    tokens = line.strip().split(' ')
    # print(tokens)
    aft_tokens = to_after(tokens, reserved='about')

    noedit_list, edit_tokens = divide_triedit_noedit(aft_tokens)
    # print(noedit_list)
    # print(triedit_tokens)
    edit_list.extend(edit_tokens)
    # print(edit_list)

    # 會有 [] 出現，若是長度不夠
    for no_edit in noedit_list:
        bigrams.extend(get_bigram(no_edit))
        trigrams.extend(get_trigram(no_edit))

    # print(edit_list)  
    # print(bigrams)

uniq_edit = set(edit_list)


# In[158]:

def bi_vs_edit(bigram, uniq_edit_list, reserved='about'):
    group = set()
    for edit in uniq_edit_list:
        if edit[1].endswith(reserved + '+}'): # only insertion and replace
            if bigram[0] == edit[0] and bigram[1] == edit[2]:
                group.add(edit)
    return group

def tri_vs_edit(trigram, uniq_edit_list, reserved='about'):
    group = set()
    for edit in uniq_edit_list:
        tri_befs = []
        for token in edit:
            # care deletion and replace and retrace
            tri_befs.append(token[2:-2].split('>>')[0] if token.startswith('[-' + reserved) else token)

        if trigram == tuple(tri_befs):
            group.add(edit)
    return group


# In[159]:

# tri_vs_edit(('discuss', 'about', 'it'), 
#            [('discuss','[-about-]','it'), ('discuss','[-about>>abc+}','it'), 
#             ('discuss','[-abc>>about+}','it'), ('discuss', '{+about+}', 'it')])


# In[160]:

bi_edit_group = dict()
for bi in set(bigrams):
    group = list(bi_vs_edit(bi, uniq_edit))
    if group: bi_edit_group[bi] = group
    # print(bi_edit_group[bi])
    # print('='*50) 
    
tri_edit_group = dict()
for tri in set(trigrams):
    group = list(tri_vs_edit(tri, uniq_edit))
    if group: tri_edit_group[tri] = group
    # print(tri_edit_group[tri])
    # print('='*50) 
    
tri_edit_group


# In[161]:

def count_bi_edit(bi_edit, bigrams_count, edit_list_count):
    dic = { bi_edit[0]: bigrams_count[bi_edit[0]] }
    for ngram in bi_edit[1:]:
        dic[ngram] = [edit_list_count[ngram], edit_list_count[ngram] / dic[bi_edit[0]]]
    return sorted(dic.items(), key = lambda item: len(item[0]))


def count_tri_edit(tri_edit, trigrams_count, edit_list_count):
    dic = { tri_edit[0]: trigrams_count[tri_edit[0]] }
    for ngram in tri_edit[1:]:
        dic[ngram] = [edit_list_count[ngram], edit_list_count[ngram] / dic[tri_edit[0]]]
    return sorted(dic.items(), key = lambda item: len(item[0]))


def sort(count_bi):
    return sorted(count_bi, key=lambda item: (item[1][1][1]))


# In[162]:

count_bi, count_tri = [], []

bigrams_count = Counter(bigrams)
trigrams_count = Counter(trigrams)
edit_list_count = Counter(edit_list)

for bi, edit in bi_edit_group.items():
    c_bi_edit = count_bi_edit([bi] + edit, bigrams_count, edit_list_count)
    count_bi.append(c_bi_edit)
#     print(c_bi_edit)
    # print('='*50)
    
for tri, edit in tri_edit_group.items():
    c_tri_edit = count_tri_edit([tri] + edit, trigrams_count, edit_list_count)
    count_tri.append(c_tri_edit)
    # print(c_tri_edit)


# In[163]:

if __name__ == '__main__':
#     print(count_bi)
#     print(sort(count_bi))
#     print(count_tri)
    # print(sort(counts_tri))

    for count_bi in sort(count_bi):
        for freq in count_bi:
            print(' '.join(freq[0]), ': ', freq[1], sep = '')
        print('='*50)

    for count_tri in sort(count_tri):
        for freq in count_tri:
            print(' '.join(freq[0]), ': ', freq[1], sep = '')
        print('='*50)


# In[ ]:




# In[ ]:



