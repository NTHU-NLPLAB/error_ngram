# -*- coding: utf-8 -*-
import fileinput
from nltk.tokenize import sent_tokenize


def restore_line_break(text):
    return text.replace('<br/>', '\n').replace('<br>', '\n')


def restore_xmlescape(text):
    while '&amp;' in text:
        text = text.replace('&amp;', '&')
    text = text.replace('&quote;', '"')
    text = text.replace('&quot;', '"')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    return text


def tokenize_doc(text):
    text = restore_line_break(text)
    text = restore_xmlescape(text)

    for line in text.splitlines():
        for sent in sent_tokenize(line.strip()):
            # restore masked edit tokens and return
            yield sent


def main():
    for doc in fileinput.input():
        doc = doc.strip()
        # print('#', 'doc', '=', doc)

        for sent in tokenize_doc(doc):
            print(sent)


if __name__ == '__main__':
    main()
