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
DEFAULT_CLEAN_DEST = '../vocab/new-vocab-clean'

TABLIFY_DEFAULT_SRC = '../vocab/irregular-vocab'
TABLIFY_DEFAULT_DEST = '../vocab/irregular-vocab'
TABLIFY_DEFAULT_CLEAN_DEST = '../vocab/irregular-vocab-clean'

'''
CSV format (normal) --
word,TYPE,meaning OR
word,word2,TYPE,meaning

certain verbs have a (semi-)irregularly derived root
'''

MD_HEADER = '''
# New vocab

Auto-derived from original

|Final form|IPA|Word type|Meaning|Original form|Middle Form|
|---|---|---|---|---|---|
'''

'''
CSV format (irregs) --
word,ipa,TYPE,meaning,Original OR
word,ipa,TYPE,meaning,Original,Middle,Regular 
'''

IRREG_MD_HEADER = '''
# Irregular vocab

Manually derived from auto-derived original OR 100% manually derived

|Final form|IPA|Word type|Meaning|Original form|Middle Form|Regular Form|
|---|---|---|---|---|---|---|
'''

MD_HEADER_CLEAN = '''
# New vocab

Auto-derived from original

|Final form|IPA|Word type|Meaning|
|---|---|---|---|
'''

IRREG_MD_HEADER_CLEAN = '''
# Irregular vocab

Manually derived from auto-derived original OR 100% manually derived

|Final form|IPA|Word type|Meaning|
|---|---|---|---|
'''

# Import vocab list from source
def import_vocab(src):
    with open(src + '.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

# Export vocab list to dest
def export_vocab(dest, vocab, sort, md, clean_dest):
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

    if clean_dest != '':
        with open(clean_dest + '.md', 'w', newline='', encoding='utf-8') as f:
            f.write(MD_HEADER_CLEAN)
            for line in vocab:
                for i in range(4):
                    f.write('|')
                    f.write(line[i])
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
    for first_word, phones, orig_word, new_type, new_desc in mid_words:
        second_word, ipa = second_shift(phones)
        new_words.append([second_word, ipa, new_type, new_desc, orig_word, first_word])

    return new_words

# the final function
def evolve(src=DEFAULT_SRC, dest=DEFAULT_DEST, sort=False, md=False, clean_dest = DEFAULT_CLEAN_DEST):
    print ('importing vocab from ' + src)
    old_vc = import_vocab(src)
    
    print ('evolving vocab...')
    new_vc = [word for line in old_vc if line for word in evolve_word(line)]
    
    print('exporting vocab to ' + dest)
    export_vocab(dest, new_vc, sort, md, clean_dest)
    return new_vc

def tablify (src=TABLIFY_DEFAULT_SRC, dest=TABLIFY_DEFAULT_DEST, clean_dest=TABLIFY_DEFAULT_CLEAN_DEST):
    print('importing tablifying vocab from', src)
    data = []
    with open(src + '.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

    print('tablifying vocab to', dest)
    with open(dest + '.md', 'w', newline='', encoding='utf-8') as f:
        f.write(IRREG_MD_HEADER)
        for line in data:
            if line == []:
                continue
            if len(line) == 5:
                for w in line:
                    f.write('|')
                    f.write(w)
                f.write('---|---|')
            elif len(line) == 7:
                for w in line:
                    f.write('|')
                    f.write(w)
            else:
                raise ValueError('input csv columns incorrect: needs 5 or 7, received', str(line))
            f.write('|\n')
    with open(clean_dest + '.md', 'w', newline='', encoding='utf-8') as f:
        f.write(IRREG_MD_HEADER_CLEAN)
        for line in data:
            if line == []:
                continue
            for i in range(4):
                f.write('|')
                f.write(line[i])
            f.write('|\n')

# vc = evolve(sort=True, md=True)
vc = evolve(md=True)
# oriv = evolve('../vocab/text', '../vocab/text-ev')
tablify()
