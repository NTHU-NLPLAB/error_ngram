def to_after(tokens):
    def to_after_token(token):
        token = token.replace('\u3000', ' ')
        if token == ' ': return ''
        
        if token.endswith('-]'):
            return None
        elif token.endswith('+}'):
            return token[token.rfind('>>')+2:-2]  if token.startswith('[-') else token[2:-2]  
        else:
            return token
        
    tokens = [e for token in map(to_after_token, tokens) if token for e in token.split(' ')]
    return tokens

def to_before(tokens):
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

after_fs = open('ef.after.txt', 'w', encoding='utf8')
before_fs = open('ef.before.txt', 'w', encoding='utf8')
for line in open('ef.diff.simplize.despace.txt', 'r', encoding='utf8'):
    tokens = line.strip().split(' ')
    aft_tokens = to_after(tokens)
    print(' '.join(aft_tokens), file=after_fs)
    
    bef_tokens = to_before(tokens)
    print(' '.join(bef_tokens), file=before_fs)
    
after_fs.close()
before_fs.close()
    
    