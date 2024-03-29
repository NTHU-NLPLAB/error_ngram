from collections import defaultdict
import sys, getopt
import re
import json

# nltk wordnet
import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

# Spacy and pre-trained Eng model
import spacy
nlp = spacy.load('en')

NOT_CARE = '_'

def boilerplate(edit):
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
        word, rule
    '''
    target, edit, loc, count = pattern.split('\t')

    pos = nlp(target, disable=['parser', 'ner'])[0].pos_ # only one word, directly 
    if pos == 'VERB': target = lemmatizer.lemmatize(target,'v')
    elif pos == 'NOUN': target = lemmatizer.lemmatize(target)

    loc = int(loc)
    rule = [NOT_CARE for i in range(abs(loc)+1)]
    rule[(loc > 0)-1] = pos # tricky, haha. loc > 0 then first location is pos, vice versa.
    rule[loc if loc > 0 else loc-1] = boilerplate(edit)
    return target, ' '.join(rule)

def get_rules(pat_file):
    '''Read all patterns from text file and parse each rule
    Args:
        file (str): The patterns file

    Returns:
        Dict: (key: word, value: rules (list))
    '''
    rules = defaultdict(lambda: [])
    for pat in open(pat_file, 'r', encoding='utf8').readlines():
        target, rule = gen_rule(pat)
        rules[target].append(rule)
    return rules  

def write_rules(target_file, rules):
    with open(target_file, 'w', encoding='utf8') as fs:
        fs.write(json.dumps(rules))      

if __name__ == '__main__':
    # read argv from command line
    try:
        inputfile, outputfile = '', ''
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input=","output="])
        for opt, arg in opts:
            if opt in ('-h', "--help"):
                print (sys.argv[0], '-i <inputfile> -o <outputfile>')
                sys.exit()
            elif opt in ("-i", "--input") and arg:
                inputfile = arg
            elif opt in ("-o", "--output") and arg:
                outputfile = arg
        if not inputfile or not outputfile: # one of i/o is empty
            raise getopt.GetoptError('')
    except getopt.GetoptError:
        print(sys.argv[0], '-i <inputfile> -o <outputfile>')
        sys.exit(2)

    # main
    print("Converting rules...")
    rules = get_rules(inputfile)
    print("Writing rules into file...")
    write_rules(outputfile, rules)
