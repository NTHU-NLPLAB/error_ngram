
# coding: utf-8

# In[1]:

# test_data = '''
# {+I　am//MW+} [-Fine//C-]{+fine//C+} , thank you !
# Garlic and Echinacea tea : drink it when {+you//PS+} have infection , 　 it is simple but {+an//AR+} excellent antibiotic .
# Hot mixture of vinegar , olive oil and eucalyptus : place it on aches and pains , itis {+a//AR+} fast and effective way to relieve aches and pains .
# [-everyone//C-]{+Everyone//C+} may use it in {+his　or　her//PS+} daily life .
# Hi , my name is yanjun .I favorite day is sunday .
# on sunday I get up at 8 o'clock in the morning I have a shower and brush my teeth , I have breakfast at 8:30 o'clock in a restaurant then I go running and read book .
# I have lunch at 11:30 o'clock in the afternoon .I go to libary and learn english .
# I have dinner at 6 o'clock in the evening .I go to movies and play dancing .at night I go to bad at 11 o'clock .
# I like sunday .what do you do on sunday ?
# I ' m 42 years old on sunday .
# december 25th .I'm having a birthday party .
# '''


# In[2]:

# 1. 把標點符號edit token，變成after
# 2. 簡化修改標記:  {+word+}, [-word-], [-word>>word+}
# 3. 再斷句一次
# 4. 把一句多錯誤，變成多句個含一個錯誤


# In[3]:


import fileinput, re
from pprint import pprint
from nltk.tokenize import sent_tokenize

def simple_tag(tags):
    if tags['d'] and tags['i']:    # d >> i
        return '[-{d}>>{i}+}}'.format(d=tags['d'], i=tags['i'])
    elif tags['d']:
        return '[-{d}-]'.format(d=tags['d'])
    elif tags['i']:
        return '{{+{i}+}}'.format(i=tags['i'])
    else:
        print("Should not be here in simple_tag()")

re_tag = r'(\[-(?P<d>.+)//(?P<d_tag>.+)-\])?({\+(?P<i>.+)//(?P<i_tag>.+)\+})?'
def correct_punc(line):
    new_line = []
    for token in line.split(' '):
        tags = re.match(re_tag, token).groupdict()
        if not tags['d_tag'] and not tags['i_tag']:  # no edit, 原字
            new_line.append(token)
        elif tags['i_tag'] == 'PU':                  # PU 錯誤類型不管，因此遇到 PU 則改成正確句子，只管被新增的符號
            for item in tags['i'].split():           # TODO: 照原本寫法，不確定 split 用意
                new_line.append(item)
        elif tags['d_tag'] != 'PU':                  # error type not 'PU'
            new_line.append(simple_tag(tags))   
    return' '.join(new_line)

def restore_line_break(text):
    return text.replace('<br/>', '\n').replace('<br>', '\n').replace('<br />', '\n')

def restore_xmlescape(text):
    while '&amp;' in text:
        text = text.replace('&amp;', '&')
    text = text.replace('&quote;', '"')
    text = text.replace('&quot;', '"')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    return text

def mask_edits(text):
    edits, tokens = [], []
    for token in text.split(' '):
        if token.startswith('{+') or token.startswith('[-'):
            masked_token = "{{{0}}}".format(len(edits))
            tokens.append(masked_token)
            edits.append(token)
        else:
            tokens.append(token.replace('{', '{{').replace('}', '}}'))
    return ' '.join(tokens), edits


def tokenize_doc(text):
    text = restore_line_break(text)
    text = restore_xmlescape(text)

    # mask edit tokens first to prevent being segmented
    # I have {+a+} pen. => I have {0} pen.
    text_masked, edits = mask_edits(text)

    for line in text_masked.splitlines():
        for sent in sent_tokenize(line.strip()):
            yield sent.format(*edits) 

def to_after(tokens):
    def to_after_token(token):
        token = token.replace('\u3000', ' ')
        if token.endswith('-]'):
            return None
        elif token.endswith('+}'):
            return token[token.rfind('>>')+2:-2]  if token.startswith('[-') else token[2:-2]  
        else:
            return token
    return ' '.join(token for token in map(to_after_token, tokens) if token)

def to_single_edit_sents(sents):
    for sent in sents:
        for s in tokenize_doc(sent):
            tokens =correct_punc(s).split(' ')
            for i, token in enumerate(tokens):
                if token.startswith('[-') or token.startswith('{+'):
                    new_sent = to_after(tokens[:i]) + ' ' + token + ' ' + to_after(tokens[i+1:])
                    yield new_sent.strip()


# In[ ]:




# In[4]:

import fileinput
import spacy
from spacy.tokens import Doc


# In[5]:

class WhitespaceTokenizer(object):
    def __init__(self, vocab):
        self.vocab = vocab

    def __call__(self, text):
        words = text.split(' ')
        # All tokens 'own' a subsequent space character in this tokenizer
        spaces = [True] * len(words)
        return Doc(self.vocab, words=words, spaces=spaces)


# In[6]:

# nlp = spacy.load('en')
nlp = spacy.load('en_core_web_lg')
nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)


# In[18]:

# 用來抓 edit word
re_words = r'(\[-(?P<d>.+)-\]|{\+(?P<i>.+)\+}|\[-(?P<rd>.+)>>(?P<ri>.+)\+})?'
def correct(origin_tokens):
    correct_tokens, pairs = [], []
    for ot in origin_tokens:
        ot = ot.replace('\u3000', ' ')
        words = re.match(re_words, ot).groupdict()
        if words['rd'] and words['ri']:
            pairs.append(('Replace', words['rd'], words['ri'], len(correct_tokens))) # 最後一欄位是對應 correct_tokens 用的
            for ri in words['ri'].split():
                correct_tokens.append(ri)
        elif words['i']:
            pairs.append(('Insert', "", words['i'], len(correct_tokens)))
            for i in words['i'].split():
                correct_tokens.append(i)
        elif words['d']:
            pairs.append(('Delete', words['d'], "", len(correct_tokens)))
        else:
            correct_tokens.append(ot)
            
    return correct_tokens, pairs

    
def format_edit(line, line_edits):
    edit_type, origin_token, new_token, correct_token = line_edits[0]
    
    template = {
        "edit_type": edit_type,
        "sent": line,
        "edits": []
    }
    
    for e in line_edits:
        edit_type, origin_token, new_token, correct_token = e
        
        for t in correct_token: # Insert or Replace
            temp = {
                "Head": {
                    "token": t.head.text,
                    "lemma": t.head.lemma_,
                    "tag": t.head.tag_,
                    "dep": None
                },
                "Target": {
                    "token": t.text,
                    "lemma": t.lemma_,
                    "tag": t.tag_,
                    "dep": t.dep_
                },
                "Child": [{"token": child.text, "lemma": child.lemma_, "tag": child.tag_, "dep": child.dep_} for child in t.children],
                "Delete": [{"token": ot.text, "lemma": ot.lemma_, "tag": ot.tag_} for ot in nlp(origin_token)] if origin_token else []
            }
            template['edits'].append(temp)  

    return template

import json
if __name__ == '__main__':
    data = []
#     for sent in to_single_edit_sents(test_data.split('\n')):
    for sent in to_single_edit_sents(fileinput.input()):
        origin_tokens = sent.strip().split(' ')
        correct_tokens, edit_pairs = correct(origin_tokens) # get edit pairs
        if not correct_tokens or not edit_pairs: continue # skip no edit or empty string
        
        correct_tokens = list(filter(lambda x: x != '', correct_tokens))
        correct_tokens = nlp(' '.join(correct_tokens))
        
        line_edits = []
        for pair in edit_pairs: # 照理只有一個 pair
            edit_type, origin_token, new_token, index = pair
            
            if edit_type == "Delete":
                if index < len(correct_tokens):
                    line_edits.append((edit_type, origin_token, new_token, correct_tokens[index-1:index]))
                if index > 0:
                    line_edits.append((edit_type, origin_token, new_token, correct_tokens[index:index+1]))
            else:
                line_edits.append((edit_type, origin_token, new_token, correct_tokens[index:index+len(new_token.split())]))

        data.append(format_edit(sent, line_edits))
    print(json.dumps(data))


# In[ ]:



