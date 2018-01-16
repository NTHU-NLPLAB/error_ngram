from collections import defaultdict
import re
import json
import spacy
nlp = spacy.load('en')

NOT_CARE = '_'

def format_rule(edit):
    group = re.match(r'(-(?P<deletion>[^\+]+))?(\+(?P<insertion>.+))?', edit).groupdict()

    template = ''
    if group['insertion'] and group['deletion']:
        template = '-{i}+{d}'
    elif group['insertion']:
        template = '-{i}'
    elif group['deletion']:
        template = '+{d}'
    else:
        print("Something Wrong in get_rule")
    
    return template.format(i=group['insertion'], d=group['deletion'])

def gen_rule(pattern):
    '''Get pattern and transform it into rule
    Args:
        pattern (str): Each line in file
    
    Returns:
        Tuple: (word, rule)
    '''
    target, edit, loc, count = pattern.split('\t')

    doc = nlp(target, disable=['parser', 'ner']) # for POS tag
    pos = doc[0].pos_

    loc = int(loc)
    rule = [NOT_CARE for i in range(abs(loc)+1)]
    if loc > 0:
        rule[0] = pos
        rule[loc] = format_rule(edit)
    elif loc < 0:
        rule[-1] = pos
        rule[loc-1] = format_rule(edit)
    else: 
        print('Should not be here!')

    return target, ' '.join(rule)

def get_patterns(file):
    '''Read all patterns from text file and parse each rule
    Args:
        file (str): The patterns file

    Returns:
        Dict: (key: word, value: rules (list))
    '''
    agePat = defaultdict(lambda: [])
    with open(file, 'r', encoding='utf8') as fs:
        patterns = fs.readlines()
        for pat in patterns:
            target, rule = gen_rule(pat)
            agePat[target].append(rule)
    return agePat        

if __name__ == '__main__':
    agePat = get_patterns('gec.pat.txt')
    with open('gec.age.txt', 'w', encoding='utf8') as fs:
        fs.write(json.dumps(agePat))
