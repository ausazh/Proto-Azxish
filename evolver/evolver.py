# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 17:23:17 2020

@author: Andi

Used to convert systematically convert Vuhinkam vocab to new

To use:
(to be used in an interpreter environment coz I'm lazy)

run the script, then use evolve()

evolve() takes two optional arguments:
    src - the source of the vocab to evolve, defaults to vocab/old-vocab.csv
    dest - the destination to place evolved vocab, defaults to vocab/new-vocab.csv
    *Note that evolve will OVERWRITE files

source file should be a csv file with 3 columns: word, word class, translation
destination file will be a similar format with 4 columns: word, word class, translation, old word (for reference)

LATER:
    write a specaialised verb evolver, which will derive all 4 roots
        (part, neg part, perf, imperf)
    as well as all 24 conjugations (perf-impf * aff-neg-emp * inf-prox-med-dist)
    will need a specialised source file with verbs marked for PERF or IMPERF base
        also irregular words will need to be manually edited from original source
        
"""

import csv, warnings
from first_shift import first_shift
from second_shift import second_shift

DEFAULT_SRC = '../vocab/old-vocab'
DEFAULT_DEST = '../vocab/new-vocab'

MD_HEADER = '''
# New vocab

Auto-derived from original

|Final form|IPA|Word type|Meaning|Original form|Middle Form|
|---|---|---|---|---|---|
'''

# Import vocab list from source
def import_vocab(src):
    with open(src + '.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

# Export vocab list to dest
def export_vocab(dest, vocab, sort, md):
    # sort vocab
    if sort:
        vocab.sort(key=lambda x: x[0])
        vocab.sort(key=lambda x: x[2])

    with open(dest + '.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(vocab)

    if md:
        with open(dest + '.md', 'w', newline='', encoding='utf-8') as f:
            f.write(MD_HEADER)
            for line in vocab:
                for w in line:
                    f.write('|')
                    f.write(w)
                f.write('|\n')
    return

# Evolve a word
def evolve_word(line):
    if len(line) == 3:
        word, word_type, translation = line
        root_2 = None
    else:
        word, root_2, word_type, translation = line

    mid_words = first_shift(word, word_type, translation, root_2)
    new_words = []
    for first_word, phones, new_type, new_desc in mid_words:
        second_word, ipa = second_shift(phones)
        new_words.append([second_word, ipa, new_type, new_desc, word, first_word])

    return new_words

# the final function
def evolve(src=DEFAULT_SRC, dest=DEFAULT_DEST, sort=False, md=False):
    print ('importing vocab from ' + src)
    old_vc = import_vocab(src)
    
    print ('evolving vocab...')
    new_vc = [word for line in old_vc if line for word in evolve_word(line)]
    
    print('exporting vocab to ' + dest)
    export_vocab(dest, new_vc, sort, md)
    return new_vc

vc = evolve(sort=True, md=True)
# oriv = evolve('../vocab/text', '../vocab/text-ev')
