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

# constants and defaults
DEFAULT_SRC = 'vocab/old-vocab.csv'
DEFAULT_DEST = 'vocab/new-vocab.csv'

EXAMPLE_LIST = [['uple', 'VERB', 'To drink'],
                ['omoq', 'VERB', 'To eat']]

IPA_VUHINKAM_DIGRAPHS = {'ts': 't͡s', 'ch': 't͡ʃ', 'sh': 'ç', 'gh': 'ʕ'}

IPA_VUHINKAM = {'m': 'm', 'n': 'n', 'ñ': 'ŋ',
                'p': 'p', 't': 't', 'k': 'k', 'q': 'q',
                'f': 'f', 's': 's', 'x': 'x', 'h': 'ħ',
                'v': 'v', 'z': 'z', 'g': 'ɣ',
                'w': 'w', 'l': 'l', 'j': 'j', 'r': 'r',
                'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
                'â': 'aː', 'ê': 'eː', 'î': 'iː', 'ô': 'oː', 'û': 'uː'}

IRREG_GEMINATE = {'t͡s': 't', 't͡ʃ': 't', 'd͡z': 'd', 'd͡ʒ': 'd', 'xʷ': 'x'}

VUHINKAM_VOWELS = ['a', 'e', 'i', 'o', 'u', 'aː', 'eː', 'iː', 'oː', 'uː']
VUHINKAM_LIQUIDS = ['r', 'w', 'l', 'j', 'm', 'n', 'ŋ']
VUHINKAM_NASALS = ['m', 'n', 'ŋ']
VUHINKAM_FRICS = ['f', 's', 'x', 'ħ', 'v', 'z', 'ɣ', 'ç', 'ʕ']

# First Shift changes
# Short and long vars given to all these due to fricatives
TO_NASALISE = {'iː': 'ĩː', 'uː': 'ũː', 'i': 'ĩ', 'u': 'ũ'}
TO_CLOSE = {'eː': 'iː', 'oː': 'uː', 'e': 'i', 'o': 'u'}
TO_OPEN = {'e': 'ɛ', 'o': 'ɔ', 'eː': 'ɛː', 'oː': 'ɔː'}
TO_BACK = {'aː': 'ɑː', 'a': 'ɑ'}
TO_FRONT = {'a': 'æ', 'aː': 'æː'}
# Exceptionally; unstressed long/short E and O centralise as actual long/short
TO_CENTRALISE = {'e': 'ɐ', 'o': 'ɐ', 'eː': 'ɘː', 'oː': 'ɘː'}

VUHINKAM_VOICED = {'m': 'm̥', 'n': 'n̥', 'ŋ': 'ŋ̊',
                   'v': 'f', 'z': 's', 'ɣ': 'x', 'ʕ': 'ħ',
                   'w': 'xʷ', 'l': 'ɬ', 'j': 'ç', 'r': 'r̥'}
VUHINKAM_UNVOICED = {'p': 'b', 't': 'd', 'k': 'g', 'q': 'ɢ',
                     't͡s': 'd͡z', 't͡ʃ': 'd͡ʒ',
                     'f': 'v', 's': 'z', 'ç': 'ʝ', 'x': 'ɣ', 'ħ': 'ʕ'}
ASSIMILATING_VOICED = VUHINKAM_VOICED.copy()
ASSIMILATING_VOICED.update({'b': 'p', 'd': 't', 'g': 'k', 'ɢ': 'q',
                            'd͡z': 't͡s', 'd͡ʒ': 't͡ʃ', 'w': 'ɸ', 'ʝ': 'ç'})
ASSIMILATING_UNVOICED = VUHINKAM_UNVOICED.copy()
ASSIMILATING_UNVOICED.update({'m̥': 'm', 'n̥': 'n', 'ŋ̊': 'ŋ',
                              'xʷ': 'ɣʷ', 'ɬ': 'l', 'r̥': 'r'})

def is_vuh_long_vowel(v):
    return v in VUHINKAM_VOWELS and len(v) > 1
def lengthen_vuh_vowel(v):
    if is_vuh_long_vowel(v):
        return v
    return v + 'ː'
def shorten_vuh_vowel(v):
    return v[:-1]

# is hiatus between i and i+1
def is_hiatus(word, i):
    if len(word) <= i+1:
        return False
    return (word[i].vowel_position == len(word[i]) - 1
                and word[i+1].vowel_position == 0)

''' 
update_vowel(new): change the vowel
update_vowel_length(l): change vowel length (True or False)
      'vowel length' is distinct from actual vowel length as it can be frozen by certain things
      remember to change vowel length when updating vowel if it is required!
      at the end of each Shift, vowel length will also be updated
swap_cons(pos, new): swap a consonant at position pos with a single other consonant 
add_cons(pos, new): add a new consonant at position X
remove_cons (pos): remove a consonant

Note: During formation, anything goes
however, after syllabification, all mutations should be done through specific methods!
Perform actions one at a time!
'''
class Syllable(list):
    def __init__(self, *args, **kwargs):
        super(Syllable, self).__init__(*args, **kwargs)
        self.stress = False
        self.vowel = None
        self.vowel_position = None
        self.is_long_vowel = None
    def is_vowel_initial(self):
        return self.vowel_position == 0
    def is_vowel_final(self):
        return self.vowel_position == len(self) - 1
    def set_vowel(self):
        for i in range(len(self)):
            s = self[i]
            if s in VUHINKAM_VOWELS:
                self.vowel = s
                self.vowel_position = i
                self.is_long_vowel = is_vuh_long_vowel(s)
                return s
        warnings.warn('Syllable ' + str(self) + ' has no vowel!')
        return None
    def update_vowel(self, new):
        self.vowel = new
        self[self.vowel_position] = new
    def swap_cons(self, pos, new):
        if self.vowel_position != pos:
            self[pos] = new
            return
        warnings.warn('Attempting to swap cons ' + new +
                      ' into pos ' + str(pos) +
                      'in syllable: '  + str(self))
    def add_cons(self, pos, new):
        # Doesn't check for phonotactic rule breaches
        # NOTE: as opposed to the insert function
        if pos < 0:
            pos += len(self) + 1 # just for the following comparison
        if self.vowel_position >= pos:
            self.vowel_position += 1
        self.insert(pos, new)
    def remove_cons(self, pos):
        if pos < 0:
            pos += len(self) # just for the following comparison
        if self.vowel_position == pos:
            warnings.warn('Attempting to remove consonant at vowel position ' + str(pos) + 'in syllable: '  + str(self))
        elif self.vowel_position > pos:
            self.vowel_position -= 1
        self.pop(pos)
            
# Import vocab list from source
def import_vocab(src):
    with open(src, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

# Export vocab list to dest
def export_vocab(dest, vocab):
    #print(vocab)
    return

# Evolution steps: First Shift
def ipaify(word):
    # retrieve corresponding IPA representation; otherwise is already correct
    # need to take into account digraphs, search for those first
    i = 0
    ipa_word = [] # needs to be as a list in order to keep affricates and long vowels as a single thing
    while i < len(word):
        if (i+1 < len(word) and
            word[i] + word[i+1] in IPA_VUHINKAM_DIGRAPHS):
            ipa_word.append(IPA_VUHINKAM_DIGRAPHS[word[i] + word[i+1]])
            i += 2
        elif word[i] in IPA_VUHINKAM:
            ipa_word.append(IPA_VUHINKAM[word[i]])
            i += 1
        else:
            warnings.warn('Illegal letter used in word: ' + word)
            i += 1
    return ipa_word    

# Apply stress and separate into syllables
def syllabify(word):
    # split first based on vowels
    syllables = []
    syl = Syllable()
    for letter in word:
        if letter in VUHINKAM_VOWELS:
            syl.append(letter)
            syllables.append(syl)
            syl = Syllable()
        else:
            syl.append(letter)
    # if syl is not nil, then final 'syl' must not have a vowel.
    # Add to the end of final syllable
    if (len(syl) > 0):
        syllables[-1] += syl
    
    # Assign stress to first and (in >2 syl words) penultimate
    syllables[0].stress = True
    if len(syllables) > 2:
        syllables[-2].stress = True
    # note that all syllables are currently (CCC)V
    for i in range(len(syllables)):
        s = syllables[i]
        # stress pulls when not final or preceding another stress
        if (s.stress and len(syllables) > i+1 and
            not syllables[i+1].stress and syllables[i+1][0] not in VUHINKAM_VOWELS):
            syllables[i].append(syllables[i+1].pop(0))
        # Any remaining CCC split as (V)C.CCV
        # note: if this isn't possible, then throw an error - illegal word!
        if len(s) > 3 and all([x not in VUHINKAM_VOWELS for x in s[:3]]):
            if i > 0 and syllables[i-1][-1] in VUHINKAM_VOWELS:
                syllables[i-1].append(syllables[i].pop(0))
            else:
                warnings.warn('Illegal consonant cluster: unresolvable CCC: ' +str(word))
        # Illegal CC clusters (where second C is not a liquid) split as (V)C.CV
        if (len(s) > 2 and s[0] not in VUHINKAM_VOWELS
            and s[1] not in VUHINKAM_VOWELS and s[1] not in VUHINKAM_LIQUIDS):
            if i > 0 and syllables[i-1][-1] in VUHINKAM_VOWELS:
                syllables[i-1].append(syllables[i].pop(0))
            else:
                warnings.warn('Illegal consonant cluster: unresolvable CC: ' +str(word))
        s.set_vowel()
    print('syllabified ' + str(syllables))
    return syllables

# goal: long vowels paired with voiced finals; short vowels paired with unvoiced
def agree_vowel_voicing(word):
    for i in range(len(word)):
        s = word[i]
        if is_vuh_long_vowel(s.vowel):
            # Do long vowel stuff
            # Remove nasal consonant as I/U
            if s.vowel in TO_NASALISE and s[-1] in VUHINKAM_NASALS:
                s.update_vowel(TO_NASALISE[s.vowel])
                s.remove_cons(-1)
            # Shorten vowel for unvoiced fric, but maintain 'long vowel' status
            # NOTE: This allows an unvoiced fric to 'stand alone after a stressed syllable'
            # as the consonant is also 'treated as a voiced consonant' in this case
            elif s[-1] in VUHINKAM_FRICS and s[-1] in VUHINKAM_UNVOICED:
                s.update_vowel(shorten_vuh_vowel(s.vowel))
            # Voice unvoiced consonant if not fric
            elif s[-1] in VUHINKAM_UNVOICED:
                s.swap_cons(-1, VUHINKAM_UNVOICED[s[-1]])
        else:
            # Do short vowel stuff
            # Lengthen vowel for unvoiced fric, but maintain 'short vowel' status
            if s[-1] in VUHINKAM_FRICS and s[-1] in VUHINKAM_VOICED:
                s.update_vowel(lengthen_vuh_vowel(s.vowel))
            # Devoice voiced consonant if not fric
            elif s[-1] in VUHINKAM_VOICED:
                s.swap_cons(-1, VUHINKAM_VOICED[s[-1]])
            # Nil final, only if not word-final
            elif s.vowel_position == len(s) - 1 and i+1 < len(word):
                if (is_hiatus(word, i)):
                    s.add_cons(len(s), 'ʔ')
                # not in hiatus, so there is a following consonant to geminate
                else:
                    gem = word[i+1][0]
                    # devoice and geminate if stressed; otherwise just geminate
                    if s.stress and gem in VUHINKAM_VOICED:
                        gem = VUHINKAM_VOICED[gem]
                        word[i+1].swap_cons(0, gem)
                    s.add_cons(len(s), IRREG_GEMINATE.get(gem, gem))
            # geminate if stressed to following if null initial, excluding glot
            # NOTE: This allows a voiced fricative to be devoiced, 'bypassing' the above rule
            # The above rule only applies to fricatives considered to be 'syllable final'
            # This also allows voiced fricatives to be geminated!
            if (s.stress and i+1 < len(word)
                    and word[i+1].vowel_position == 0
                    and s[-1] != 'ʔ'):
                word[i+1].add_cons(0, s[-1])
                s.swap_cons(-1, IRREG_GEMINATE.get(s[-1], s[-1]))
    print('agreed length-voicing ' + str(word))
    return word    

def shift_vowel_first(word):
    for i in range(len(word)):
        s = word[i]
        # Handle stressed initials
        if s.vowel_position == 0 and i == 0 and s.stress:
            # stressed initial 'long' E/O are exempt from closing
            if s.is_long_vowel and s.vowel[0] == 'e':
                s.add_cons(0, 'j')
                continue
            elif s.is_long_vowel and s.vowel[0] == 'o':
                s.add_cons(0, 'w')
                continue
            else:
                s.add_cons(0, 'ʔ')
        if s.is_long_vowel:
            if s.stress:
                # Nasalise stressed 'long' high vowels
                if s.vowel in TO_NASALISE:
                    s.update_vowel(TO_NASALISE[s.vowel])
                # Close 'long' mid vowels
                elif s.vowel in TO_CLOSE:
                    s.update_vowel(TO_CLOSE[s.vowel])
                # A stays as is
            else: # unstressed
                # I/U stay as is
                # Centralise mid vowels using True Length
                if s.vowel in TO_CENTRALISE:
                    s.update_vowel(TO_CENTRALISE[s.vowel])
                # Back unstressed 'long' A
                elif s.vowel in TO_BACK:
                    s.update_vowel(TO_BACK[s.vowel])
        else: # short vowel
            # 'short' A fronts regardless of stress
            if s.vowel in TO_FRONT:
                s.update_vowel(TO_FRONT[s.vowel])
            elif s.stress:
                # I/U stay as is
                # Open mid vowels
                if s.vowel in TO_OPEN:
                    s.update_vowel(TO_OPEN[s.vowel])
            else: # unstressed
                # I/U stay as is
                if s.vowel in TO_CENTRALISE:
                    s.update_vowel(TO_CENTRALISE[s.vowel])
    print('shifted vowel (1) ' + str(word))
    return word    

def assimilate_voicing(word):
    for i in range(len(word)):
        s = word[i]
        # Do onset cluster assimilation
        if s.vowel_position >= 2:
            if s[0] in ASSIMILATING_VOICED and s[1] in ASSIMILATING_UNVOICED:
                s.swap_cons(1, ASSIMILATING_UNVOICED[s[1]])
            if s[0] in ASSIMILATING_UNVOICED and s[1] in ASSIMILATING_VOICED:
                s.swap_cons(1, ASSIMILATING_VOICED[s[1]])
        # Do inter-syllable cluster assimilation
        if i + 1 >= len(word):
            continue # no following syllable to assimilate
        s1 = word[i+1]
        if s.is_vowel_final() or s1.is_vowel_initial():
            continue # no cluster to assimilate
        if s[-1] in ASSIMILATING_VOICED and s1[0] in ASSIMILATING_UNVOICED:
            s1.swap_cons(0, ASSIMILATING_UNVOICED[s1[0]])
        if s[-1] in ASSIMILATING_UNVOICED and s1[0] in ASSIMILATING_VOICED:
            s1.swap_cons(0, ASSIMILATING_VOICED[s1[0]])
    print('assimilated clusters ' + str(word))
    return word    

def shift_laryngeal_vowel(word):
    return word    

def shift_cons_first(word):
    return word    

def reduce_cluster_first(word):
    return word    

def vocalise_gh(word):
    return word        

def desyllabify(word):
    return word    

def first_shift(word):
    word = ipaify(word)
    word = syllabify(word)
    word = agree_vowel_voicing(word)
    word = shift_vowel_first(word)
    word = assimilate_voicing(word)
    word = shift_laryngeal_vowel(word)
    word = shift_cons_first(word)
    word = reduce_cluster_first(word)
    word = vocalise_gh(word)
    word = desyllabify(word)
    return word

# Evolution steps: First Shift
def second_shift(word):
    return word

# Evolve a word
def evolve_word(line):
    word, word_type, translation = line

    first_word = first_shift(word)
    second_word = second_shift(first_word)

    return [second_word, word_type, translation, word]


# the final function
def evolve(src=DEFAULT_SRC, dest=DEFAULT_DEST):
    print ('importing vocab from ' + src)
    old_vc = import_vocab(src)
    
    print ('evolving vocab...')
    new_vc = [evolve_word(line) for line in old_vc if line]
    
    print('exporting vocab to ' + dest)
    export_vocab(dest, new_vc)
    return new_vc

