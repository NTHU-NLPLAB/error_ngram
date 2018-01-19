from gecVerbForm import droping, adding
from gen_pat import get_rules
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

    err_sents = []
    for pat in pats: # 針對 each pattern
        pat = pat.split()
        pos_locs = [ i for i, p in enumerate(pat) if p in UD_POS ] # 找 rule 中單字(POS)的位置
        pos_loc = pos_locs[0]
        # TODO: 萬一沒找到的情況
        start_loc = loc - pos_loc if pos_locs else loc # 從 sent 中 rule 起始位置開始
        
        res = matching(sent, pat, start_loc, pos_loc)
        if res: 
            res = ' '.join(sent[:start_loc]+res+sent[start_loc+len(pat):]).replace('_', ' ')
            err_sents.append(res)
    return err_sents

def matching(sent, pat, start_loc, pos_loc):
    res = []
    for i, p in enumerate(pat):
        # TODO: not clear enough
        word = sent[start_loc+i] if start_loc+i < len(sent) else '' # None
        prevword = sent[start_loc+i-1] if start_loc+i-1 >= 0 else '' # None
        nextword = sent[start_loc+i+1] if start_loc+i+1 < len(sent) else '' # None

        if p in UD_POS:
            res += [ sent[start_loc+i] ]
        elif p[0] == '-' and '+' in p: # replace
            minus, plus = p[1:p.index('+')], p[p.index('+')+1:]
            if word == minus:   res += [ plus ]
            else:               return False # return sent
        elif p[0] == '+': # 擔心修改後邏輯有誤，以原邏輯稍做修改
            if pos_loc > i: # insert BEFORE
                if p[1:] in [word, prevword]: return False # return sent
                res += [ word, p[1:] ]
            elif pos_loc < i: # insert AFTER
                if p[1:] in [word, nextword]: return False # return sent # avoid creating double
                res += [ p[1:], word ]
            else:
                print("Should not be here!")
        elif p[0] == '-': # delete
            if p[1:] == word: continue
            else:             return False # return sent
        elif '(%s)' in p:
            try:    res += [eval(p % 'sent[start_loc+i]')]
            except: return False # return sent
        else: return False # return sent
    return res

test_lines = '''What \'s more , his ability to speak was perfect .
We must not doubt women of ability in work places .
He commented on the topic .
We plan to go abroad this summer .
We plan to go to abroad this summer .
This sentence matches no rules .
We will discuss this issue later .
able to able to'''.split('\n')

if __name__ == '__main__':
    print("Generating rules...")
    agePat = json.load(open('./data/gec.age.txt', 'r')) # Read rules from a file
    # agePat = get_patterns('data/gec.pat.txt') # Generate rules from the pattern file

    print("Modifying sentences...")
    fs = open('./data/result.txt', 'w', encoding='utf8')
    for sent in test_lines:
        print('\noriginal =', sent, file=fs)
        sent = sent.split(' ')
        rules = getRules(sent) # TODO: 會不會只檢查到一個符合
        for i in range(len(rules)):
            errs = genAGE(sent, *rules[i])
            for e in errs:
                print('fake err =', e, file=fs)
    fs.close()

            
        