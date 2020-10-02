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

DEFAULT_SRC = '../vocab/old-vocab.csv'
DEFAULT_DEST = '../vocab/new-vocab.csv'

# Import vocab list from source
def import_vocab(src):
    with open(src, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

# Export vocab list to dest
def export_vocab(dest, vocab, sort):
    # sort vocab
    if sort:
        vocab.sort(key=lambda x: x[0])
        vocab.sort(key=lambda x: x[2])

    with open(dest, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(vocab)
    return

# Evolve a word
def evolve_word(line):
    word, word_type, translation = line

    first_word, phones = first_shift(word)
    second_word, ipa = second_shift(phones)

    return [second_word, ipa, word_type, translation, word, first_word]

# the final function
def evolve(src=DEFAULT_SRC, dest=DEFAULT_DEST, sort=False):
    print ('importing vocab from ' + src)
    old_vc = import_vocab(src)
    
    print ('evolving vocab...')
    new_vc = [evolve_word(line) for line in old_vc if line]
    
    print('exporting vocab to ' + dest)
    export_vocab(dest, new_vc, sort)
    return new_vc

vc = evolve(sort=True)
oriv = evolve('../vocab/text.csv', '../vocab/text-ev.csv')