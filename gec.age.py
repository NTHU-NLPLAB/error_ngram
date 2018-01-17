from gecVerbForm import droping, adding
import json
import spacy
nlp = spacy.load('en')

UD_POS = ['NOUN', 'ADJ', 'ADV', 'ADP', 'AUX',' CCONJ', 'DET', 'INTJ', 'NUM',
'PART','PRON','PROPN','PUNCT','SCONJ', 'SYM', 'VERB', 'X']
# agePat = dict([ 
#     ('ability', ['NOUN -to+of add_ing(%s)', ]), \
#     ('discuss', ['VERB +about']), \
#     ('commented', ['VERB -on']), \
#     ('abroad', ['to+ ADV']), \
    # ('abroad', ['+to']), \
# ])

def add_ing(verb):
    if verb in adding: return adding[verb]
    else:              return verb+'ing'

def drop_ing(verb):
    if verb in droping:      return droping[verb]
    elif verb[-3:] == 'ing': return verb[:-3]
    else:                    return verb

def getRules(sent):
    return [(i, agePat[word]) for i, word in enumerate(sent) if word in agePat]
        # if word in agePat: return (i, agePat[word])
            
def genAGE(sent, loc, pats):
    # sent, 句子中對應的單字位置 0, ['ADJ -to+for', 'was-is+ ADJ']

    res = []
    for pat in pats: # 針對 each rule
        pat = pat.split()
        # TODO: 萬一 rule 裡面有很多個 POS tag，不過應該不會發生
        pos_locs = [ i for i, p in enumerate(pat) if p in UD_POS ] # 找 rule 中單字(POS)的位置
        pos_loc = pos_locs[0]
        # TODO: 萬一沒找到的情況
        loc = loc - pos_loc if pos_locs else loc # 從 sent 中 rule 起始位置開始

        for i, p in enumerate(pat):
            word = sent[loc+i]
            prevword = sent[loc+i-1] if loc+i-1 < 0 else '' # None
            nextword = sent[loc+i+1] if loc+i+1 > len(sent) else '' # None

            if p in UD_POS:
                res += [ sent[loc+i] ] # 本身那個字 sent[4+0] if loc==0 是 pos
            elif p[0] == '-' and '+' in p: # replace
                minus, plus = p[1:p.index('+')], p[p.index('+')+1:]
                if word == minus:   res += [ plus ]
                else:               return sent
            elif p[0] == '+': # 擔心修改後邏輯有誤，以原邏輯稍做修改
                if pos_loc > i: # insert BEFORE
                    if p[1:] in [word, prevword]: return sent
                    res += [ word, p[1:] ]
                elif pos_loc < i: # insert AFTER
                    if p[1:] in [word, nextword]: return sent # avoid creating double
                    res += [ p[1:], word ]
                else:
                    print("Should not be here!")
            elif p[0] == '-': # delete
                if p[1:] == sent[loc+i]: pass
                else:                    return sent
            elif '(%s)' in p:
                try:    res += [eval(p % 'sent[loc+i]')]
                except: return sent
            else: return sent
        return sent[:loc]+res+sent[loc+len(pat):]

if __name__ == '__main__':
    agePat = json.load(open('gec.age.txt', 'r'))
    lines = '''What \'s more , his ability to speak was perfect .
We must not doubt women of ability in work places .
He commented on the topic .
We plan to go abroad this summer .
We plan to go to abroad this summer .
This sentence matches no rules .
We will discuss this issue later .
able to able to'''.split('\n')
    for sent in lines:
        print('\noriginal =', sent)
        sent = sent.split(' ')
        rules = getRules(sent) #TODO: 會不會只檢查到一個符合
        for i in range(len(rules)):
            sent = genAGE(sent, *rules[i])
        if rules: print('fake err =', ' '.join(sent))
            
        