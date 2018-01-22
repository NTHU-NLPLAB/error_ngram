# Error Ngram

The aim of this project is to generate error sentences from correct sentences given a large number of patterns.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
python 3.6+
nltk
spacy
```

### Installing

A step by step series of examples that tell you have to get a development env running

```
git clone https://github.com/NTHU-NLPLAB/error_ngram.git
```

Put your patterns file, named gec.pat.txt, in data/ and then run the following command.
gen_rules.py generates rules based on the patterns.

```
python ./pattern_to_rule/gen_rules.py -i <input_file> -o <output_file>
```
or to get instruction
```
python ./pattern_to_rule/gen_ruless.py -h
```

After gaining gec.age.txt (the rules), run:
```
python ./pattern_to_rule/gec.age.py [-c] -r <rule_file> -i <input_file> -o <output_file>
```
If you want to combine two actions together, use `-c`, which will convert patterns to rules and then modify every sentence. On the other hand, just command `-i <file>` and `-o <file>`.

### TODO:
* So far, we use test sentences, which are hard-coded.
* Add some commands for automation. (run one .py rather than two .py)
