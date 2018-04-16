import nltk
import fileinput


def to_after(tokens):
    aft_tokens = [] 
    for token in tokens:
        token = token.replace('\u3000', ' ')
        if token != ' ':     
            if token.endswith('about+}') or token.startswith('[-about'):
                if len(token.split(' ')) == 1:
                    aft_tokens.append(token)
                else:
                    if token.endswith('-]'):
                        None
                    elif token.endswith('+}'):
                        if token.startswith('[-'):
                            token = token[:-2].split('>>')[1]
                        else: 
                            token = token[2:-2]
                        aft_tokens.extend(token.split(' '))
                
            else:
                if token.endswith('-]'):
                    None
                elif token.endswith('+}'):
                    if token.startswith('[-'):
                        token = token[:-2].split('>>')[1]
                    else: 
                        token = token[2:-2]
                    aft_tokens.extend(token.split(' '))

                else: 
                    aft_tokens.extend(token.split(' '))
    return aft_tokens


def divide_triedit_noedit(aft_tokens):
    noedit_list = []
    triedit_list = []
    if not '+}' in str(aft_tokens) and not '-]' in str(aft_tokens):
        noedit_list.append(aft_tokens)
    else:
        for i, token in enumerate(aft_tokens):
            if token.endswith('about+}') or token.startswith('[-about'): 
                if len(aft_tokens[:i]) > 1:
                    noedit_list.append(aft_tokens[:i])
                if len(aft_tokens[i+1:]) > 1:
                    noedit_list.append(aft_tokens[i+1:])
                if i > 0 and i + 2 <= len(aft_tokens):
                    triedit_list.append(tuple(aft_tokens[i-1:i+2]))
    return noedit_list, triedit_list


def bi_noedit_tokens(noedit_part):
    return list(nltk.bigrams(noedit_part))


def tri_noedit_tokens(noedit_part):
    return list(nltk.trigrams(noedit_part))


def bi_vs_tri(bi_noedit, triedit_list):
    bi_com_tri = set()
    for tri_edit in set(triedit_list):
        if tri_edit[1].endswith('about+}'):
            if bi_noedit[0] == tri_edit[0] and bi_noedit[1] == tri_edit[2]:
                bi_com_tri.add(bi_noedit)
                bi_com_tri.add(tri_edit)
    return sorted(bi_com_tri, key = len)


def tri_vs_tri(tri_noedit, triedit_list):
    tri_com_tri = set()
    for tri_edit in set(triedit_list):
        tri_befs = []
        for token in tri_edit:
            if token.startswith('[-about'):
                token_bef = tri_edit[1][2:-2].split('>>')[0]
                tri_befs.append(token_bef)
            else:
                tri_befs.append(token)  
            
        if tri_noedit == tuple(tri_befs):
            tri_com_tri.add(tri_edit)
            tri_com_tri.add(tri_noedit)
                      
    return sorted(tri_com_tri, reverse = True)


def counting_bvst(bitri, bi_noedit_list, triedit_list):
    dict = {}
    dict[bitri[0]] = bi_noedit_list.count(bitri[0])
    for ngram in bitri[1:]:
        dict[ngram] = [triedit_list.count(ngram), triedit_list.count(ngram)/dict[bitri[0]]]
    return sorted(dict.items(), key = lambda item: len(item[0]))


def counting_tvst(tritri, tri_noedit_list, triedit_list):
    dict = {}
    dict[tritri[0]] = tri_noedit_list.count(tritri[0]) 
    for ngram in tritri[1:]:
        dict[ngram] = [triedit_list.count(ngram), triedit_list.count(ngram)/dict[tritri[0]]]
    return sorted(dict.items(), key = lambda item: len(item[0]))


def sort(counts_bi):
    return sorted(counts_bi, key = lambda item: (item[1][1][1]))


def main():
    triedit_list = []

    bi_noedit_list = []
    tri_noedit_list = []
    
    triedit_bef_list = []
    bi_com_tri_set = set()
    tri_com_tri_set = set()

    counts_bi = []
    counts_tri = []

    for line in fileinput.input():
        line = line.strip()
        tokens = line.split(' ')
        aft_tokens = to_after(tokens)
        # print(tokens)
        noedit_list, triedit_tokens = divide_triedit_noedit(aft_tokens)
        # print(noedit_list)
        triedit_list.extend(triedit_tokens)
    #     print(noedit_list)
    # print(triedit_list)
        for noedit_part in noedit_list:
            bi_noedit_list.extend(bi_noedit_tokens(noedit_part))
            if len(noedit_part) > 2:
                tri_noedit_list.extend(tri_noedit_tokens(noedit_part))


    # print(triedit_list)  
    # print(bi_noedit_list)      
                              
    for bi_noedit in set(bi_noedit_list):
        bi_com_tri = bi_vs_tri(bi_noedit, triedit_list)
        if bi_com_tri:
    #         # print(bi_com_tri) 
            bi_com_tri_set.add(tuple(bi_com_tri))
    #         # print('='*50)        

    for tri_noedit in set(tri_noedit_list):
        tri_com_tri = tri_vs_tri(tri_noedit, triedit_list)
        if tri_com_tri:        
            tri_com_tri_set.add(tuple(tri_com_tri))

    # print(bi_com_tri_set)      
    
    for bitri in bi_com_tri_set:
    #     # print(bitri)
        count_bvst = counting_bvst(bitri, bi_noedit_list, triedit_list)
        counts_bi.append(count_bvst)
        # print(count_bvst)
        # print('='*50)

     # print(tri_noedit_list)
    print(tri_com_tri_set)   
    #  
    for tritri in tri_com_tri_set:
    #     # print(tritri)
        count_tvst = counting_tvst(tritri, tri_noedit_list, triedit_list)
    #     # print(count_tvst)
        # counts_tri.append(count_tvst)

        for freq in count_tvst:
            print(' '.join(freq[0]), ': ', freq[1], sep = '')
        print('='*50)


    print(counts_bi)
    print(sort(counts_bi))
    print(counts_tri)
    # print(sort(counts_tri))


    for count_bi in sort(counts_bi):
        for freq in count_bi:
            print(' '.join(freq[0]), ': ', freq[1], sep = '')
        print('='*50)

    # for count_tri in sort(counts_tri):
    #     for freq in count_tri:
    #         print(' '.join(freq[0]), ': ', freq[1], sep = '')
    #     print('='*50)


        # for freq in count_bvst:
        #     print(' '.join(freq[0]), ': ', freq[1], sep = '')
        # print('='*50)

   
        # for freq in count_tvst:
        #     print(' '.join(freq[0]), ': ', freq[1], sep = '')
        # print('='*50)


if __name__ == '__main__':
    main()