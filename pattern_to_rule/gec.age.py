from gecVerbForm import droping, adding
from gen_rules import get_rules
import json
import sys, getopt

UD_POS = ['NOUN', 'ADJ', 'ADV', 'ADP', 'AUX','CCONJ', 'DET', 'INTJ', 'NUM',
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
            
def genAGE(sent, loc, pats):
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

        if p in UD_POS or p == '_':
            res += [ sent[start_loc+i] ]
        elif p[0] == '-' and '+' in p: # replace
            minus, plus = p[1:p.index('+')], p[p.index('+')+1:]
            if word == minus:   res += [ plus ]
            else:               return False 
        elif p[0] == '+': # 擔心修改後邏輯有誤，以原邏輯稍做修改
            if pos_loc > i: # insert BEFORE
                if p[1:] in [word, prevword]: return False 
                res += [ word, p[1:] ]
            elif pos_loc < i: # insert AFTER
                if p[1:] in [word, nextword]: return False # avoid creating double
                res += [ p[1:], word ]
            else:
                print("Insertion should not be in the same position with POS tag!")
        elif p[0] == '-': # delete
            if p[1:] == word: continue
            else:             return False 
        elif '(%s)' in p:
            try:    res += [eval(p % 'sent[start_loc+i]')]
            except: return False # return sent
        else: return False 
    return res

if __name__ == '__main__':
    # read argv from command line
    try:
        convert = False
        inputfile, outputfile, rule = '', '', ''
        opts, args = getopt.getopt(sys.argv[1:], "hcr:i:o:", ["help", "convert", "rule=", "input=","output="])
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                print (sys.argv[0], '[-c: convert] -r <rulefile> -i <inputfile> -o <outputfile>')
                sys.exit()
            elif opt in ("-c", "--convert"):
                convert = True
            elif opt in ("-r", "--rule") and arg:
                rule = arg  
            elif opt in ("-i", "--input") and arg:
                inputfile = arg
            elif opt in ("-o", "--output") and arg:
                outputfile = arg
        if rule and inputfile and outputfile: pass # one of i/o is empty
        else: raise getopt.GetoptError('')
    except getopt.GetoptError:
        print (sys.argv[0], '[-c: convert] -r <rulefile> -i <inputfile> -o <outputfile>')
        sys.exit(2)

    # Spacy with pre-trained English model
    import spacy
    nlp = spacy.load('en')

    print("Reading rules...")
    if convert: agePat = get_rules(rule) # Generate rules from the pattern file
    else: agePat = json.load(open(rule, 'r')) # Read rules from a file
    
    print("Modifying sentences...")
    fs = open(outputfile, 'w', encoding='utf8')
    for sent in open(inputfile, 'r', encoding='utf8').read().split('\n'):
        print('\noriginal =', sent, file=fs)
        sent = sent.split(' ')
        rules = getRules(sent) # TODO: 會不會只檢查到一個符合
        for i in range(len(rules)):
            errs = genAGE(sent, *rules[i])
            for e in errs:
                print('fake err =', e, file=fs)
    fs.close()