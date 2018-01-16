from gecVerbForm import droping, adding
import json
import spacy
nlp = spacy.load('en')

UD_POS = ['NOUN', 'ADJ', 'ADV', 'ADP', 'AUX',' CCONJ', 'DET', 'INTJ', 'NUM',
'PART','PRON','PROPN','PUNCT','SCONJ', 'SYM', 'VERB', 'X']
# agePat = dict([ 
#     ('ability', ['N -to+of add_ing(%s)', ]), \
#     ('discuss', ['V +about']), \
#     ('commented', ['V -on']), \
#     ('abroad', ['to+ ADV']), \
#     ('abroad', ['+to']), \
# ])

def add_ing(verb):
    if verb in adding: return adding[verb]
    else:              return verb+'ing'

def drop_ing(verb):
    if verb in droping:      return droping[verb]
    elif verb[-3:] == 'ing': return verb[:-3]
    else:                    return verb

def getRules(sent):
    for i, word in enumerate(sent):
        if word in agePat: return (i, agePat[word])
            
def genAGE(sent, loc, pats):
    # sent, 句子中對應的單字位置 0, ['ADJ -to+for', 'was-is+ ADJ']
    
    res = []
    for pat in pats: # 針對 each rule
        pat = pat.split()
        # TODO: 假設 rule 裡面只有一個 POS tag
        locs = [ i for i, p in enumerate(pat) if p in UD_POS ] # 找 rule 中單字(POS)的位置
        loc = loc - locs[0] if locs else loc # TODO: 萬一沒找到的情況
        #if pat[0].isupper(): loc -= 1
        for i, p in enumerate(pat):
            word = sent[loc+i]
            prevword = sent[loc+i-1] if sent[loc+i-1] else None
            nextword = sent[loc+i+1] if sent[loc+i+1] else None

            if p in UD_POS:
                res += [ sent[loc+i]]
            elif p[0] == '-' and '+' in p: # replace
                minus, plus = p[1:p.index('+')], p[p.index('+')+1:]
                if word == minus:   res += [ plus ]
                else:               return sent
            elif p[0] == '+': # insert BEFORE
                if p[1:] in [word, prevword]: return sent
                res += [ p[1:], word ]
            # elif p[-1] == '+': # insert AFTER
            #     if p[:-1] in [word, nextword]: return sent # avoid creating double
            #     res += [ word, p[:-1] ]
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
        rule = getRules(sent) #TODO: 會不會只檢查到一個符合
        if rule:
            sent_age = genAGE(sent, *rule) # * -> deconstruct
            print('fake err =', ' '.join(sent_age))
        