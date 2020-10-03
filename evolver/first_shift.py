
import warnings
from syllable import Syllable
from first_shift_constants import *

# is hiatus between i and i+1
def is_hiatus(word, i):
    if len(word) <= i+1:
        return False
    return (word[i].vowel_position == len(word[i]) - 1
                and word[i+1].vowel_position == 0)

# functions to retrieve adjacents, regardless of syllable structure
def get_preceding(word, i, pos):
    if pos > 0:
        return word[i][pos-1]
    if i > 0:
        return word[i-1][-1]
    #warnings.warn('Attempting to retrieve preceding of initial at ' + str(word))
    return None
def get_following(word, i, pos):
    if pos + 1 < len(word[i]):
        return word[i][pos+1]
    if i + 1 < len(word):
        return word[i+1][0]
    #warnings.warn('Attempting to retrieve following of final at ' + str(word))
    return None
    
def get_adjacent(word, i, pos):
    return (get_preceding(word, i, pos), get_following(word, i, pos))

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

# Apply regular grammatical affixes (verbs)
def grammatify(word, word_type, desc, root2):
    if 'VERB' not in word_type:
        return [(word, word_type, desc)]
    # Affixify verbs!
    words = []
    # Participle: first element, as is
    words.append([word, 'PART', desc + ' (Participle)'])

    # Negative Participle: first element + negative pre-/infix
    neg = list(word)
    if word[0] == 'a':
        neg = ['a', 'k', 'a'] + neg
    elif word[0] == 'aː':
        neg = ['aː', 'x', 'aː'] + neg
    elif word[0] == 'e':
        neg = ['e', 'ç', 'e'] + neg
    elif word[0] == 'eː':
        neg = ['eː', 'ç', 'eː'] + neg
    elif word[0] == 'i':
        neg = ['i', 't', 'i'] + neg
    elif word[0] == 'iː':
        neg = ['iː', 's', 'iː'] + neg
    elif word[0] == 'o':
        neg = ['o', 'ç', 'w', 'e'] + neg
    elif word[0] == 'oː':
        neg = ['oː', 'ç', 'w', 'eː'] + neg
    elif word[0] == 'u':
        neg = ['u', 't', 'w', 'i'] + neg
    elif word[0] == 'uː':
        neg = ['uː', 's', 'w', 'iː'] + neg
    elif word[0] in VUHINKAM_NASALS:
        neg = ['a'] + neg
    elif word[0] in VUHINKAM_STOPS_AFS:
        neg = ['eː'] + neg
    elif word[0] in VUHINKAM_FRICS:
        neg = ['iː'] + neg
    elif word[0] in VUHINKAM_APPXS_R:
        neg = ['q', 'i'] + neg
    else:
        raise KeyError('unsupported letter in verb ' + word)
    words.append([neg, 'PART', desc + ' (Negative Participle)'])

    verb_root = list(word)
    if word_type == 'VERB-IM':
        verb_root = list(root2)
    
    if verb_root[0] in VUHINKAM_VOWELS:
        verb_root = ['q', 'eː', 'j'] + verb_root
    else:
        verb_root = ['q', 'eː'] + verb_root

    # Perfective: PF: qê-, IM: qê-2-af, PT: N/A
    if word_type == 'VERB-PF':
        words.append([verb_root, 'VERB', desc + ' (Perfective)'])
    elif word_type == 'VERB-IM':
        new_root = list(verb_root)
        if len(new_root) > 2 and new_root[-3:] == ['k', 'a', 'n']:
            new_root = new_root[:-3] + ['k', 'n', 'e', 'f']
        else:
            new_root += ['e', 'f']
        words.append([new_root, 'VERB', desc + ' (Perfective)'])

    # Imperfective: PF: qê-ka, IM: qê-2, PT: N/A
    if word_type == 'VERB-PF':
        words.append([verb_root + ['k', 'e'], 'VERB', desc + ' (Imperfective)'])
    elif word_type == 'VERB-IM':
        words.append([verb_root, 'VERB', desc + ' (Imperfective)'])

    return words

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
        if (s.stress and len(syllables) > i+1
                     and not syllables[i+1].stress
                     and syllables[i+1][0] not in VUHINKAM_VOWELS):
            syllables[i].append(syllables[i+1].pop(0))
        # V-final syllable pulls when following is CC and first is equal or more stressed than second
        if (len(syllables) > i+1
                     and (s.stress or not syllables[i+1].stress)
                     and s[-1] in VUHINKAM_VOWELS
                     and len(syllables[i+1]) > 2
                     and syllables[i+1][0] not in VUHINKAM_VOWELS
                     and syllables[i+1][1] not in VUHINKAM_VOWELS):
            syllables[i].append(syllables[i+1].pop(0))        
        # Any remaining CCC split as (V)C.CCV
        # note: if this isn't possible, then throw an error - illegal word!
        if len(s) > 3 and all([x not in VUHINKAM_VOWELS for x in s[:3]]):
            if i > 0 and syllables[i-1][-1] in VUHINKAM_VOWELS:
                syllables[i-1].append(syllables[i].pop(0))
            else:
                warnings.warn('Illegal consonant cluster: unresolvable CCC: ' +str(word))
        # Illegal CC clusters (where second C is not a liquid) split as (V)C.CV
        # also includes CC clusters of homorganic stop + nasal
        if (len(s) > 2 and s[0] not in VUHINKAM_VOWELS
                and s[1] not in VUHINKAM_VOWELS
                and (s[1] not in VUHINKAM_LIQUIDS
                    or (s[0] in ILLEGAL_STOPNAS
                        and s[1] == ILLEGAL_STOPNAS[s[0]]
                    )
                )
            ):
            if i > 0 and syllables[i-1][-1] in VUHINKAM_VOWELS:
                syllables[i-1].append(syllables[i].pop(0))
            # CC homorganic clusters broken by deleting the nasal
            elif s[0] in ILLEGAL_STOPNAS and s[1] in ILLEGAL_STOPNAS[s[0]]:
                syllables[i].pop(1)
            else:
                warnings.warn('Illegal consonant cluster: unresolvable CC: ' +str(word))
        s.set_vowel()
    # print('syllabified ' + str(syllables))
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
    # print('agreed length-voicing ' + str(word))
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
    #print('shifted vowel (1) ' + str(word))
    return word    

def assimilate_voicing(word):
    for i in range(len(word)):
        s = word[i]
        # Fricative-Consonant UV-V clusters assimilate to V, excluding apx and R
        # Do onset cluster assimilation
        if s.vowel_position >= 2:
            if (s[0] in TO_VOICE_FRICS
                    and s[1] in ASSIMILATING_VOICED
                    and s[1] not in VOICING_FOLLOWS_EXCS):
                s.swap_cons(0, ASSIMILATING_UNVOICED[s[0]])
                # UV-UV(F)-V assimilates to V-V-V
                prec = get_preceding(word, i, 0)
                if prec in ASSIMILATING_UNVOICED:
                    word[i-1].swap_cons(-1, ASSIMILATING_UNVOICED[prec])
            elif s[0] in ASSIMILATING_VOICED and s[1] in ASSIMILATING_UNVOICED:
                s.swap_cons(1, ASSIMILATING_UNVOICED[s[1]])
            elif s[0] in ASSIMILATING_UNVOICED and s[1] in ASSIMILATING_VOICED:
                s.swap_cons(1, ASSIMILATING_VOICED[s[1]])

        # Nasal vowels force following cluster to be voiced
        if s.vowel in VOICING_NASALS:
            if s.is_vowel_final():
                fol = get_following(word, i, s.vowel_position)
                if fol in ASSIMILATING_UNVOICED:
                    word[i+1].swap_cons(0, ASSIMILATING_UNVOICED[fol])
            elif s[-1] in ASSIMILATING_UNVOICED:
               s.swap_cons(-1, ASSIMILATING_UNVOICED[s[-1]])

        # Do inter-syllable cluster assimilation
        if i + 1 >= len(word):
            continue # no following syllable to assimilate
        s1 = word[i+1]
        if s.is_vowel_final() or s1.is_vowel_initial():
            continue # no cluster to assimilate
        if (s[-1] in TO_VOICE_FRICS
            and s1[0] in ASSIMILATING_VOICED
            and s1[0] not in VOICING_FOLLOWS_EXCS):
            s.swap_cons(-1, ASSIMILATING_UNVOICED[s[-1]])
        elif s[-1] in ASSIMILATING_VOICED and s1[0] in ASSIMILATING_UNVOICED:
            s1.swap_cons(0, ASSIMILATING_UNVOICED[s1[0]])
        elif s[-1] in ASSIMILATING_UNVOICED and s1[0] in ASSIMILATING_VOICED:
            s1.swap_cons(0, ASSIMILATING_VOICED[s1[0]])
    #print('assimilated clusters ' + str(word))
    return word    

def shift_laryngeal_vowel(word):
    for i in range(len(word)):
        s = word[i]
        prec = get_preceding(word, i, s.vowel_position)
        if (prec in LARYNGEALS and s.vowel in LARING_VOWELS):
            s.update_vowel(LARING_VOWELS[s.vowel])
    return word    

def shift_cons_first(word):
    for i in range(len(word)):
        s = word[i]
        # TS > TTH, DZ > DDH
        if 't͡s' in s:
            s.swap_cons(s.index('t͡s'), 't͡θ')
        if 'd͡z' in s:
            s.swap_cons(s.index('d͡z'), 'd͡ð')
        # W > Ẅ after palatal cons or before I
        if 'w' in s:
            pos = s.index('w')
            prec, fol = get_adjacent(word, i, pos)
            if prec in FIRST_PALATALS or fol in FIRST_I_VARS:
                s.swap_cons(pos, 'ɥ')
        # Alv + R > Retroflex
        pos = -1
        if 'r' in s: pos = s.index('r')
        if 'r̥' in s: pos = s.index('r̥')
        if pos >= 0:            
            prec, fol = get_adjacent(word, i, pos)
            merged = False
            if prec in RETRING_ALVS:
                merged = True
                if pos == 0:
                    word[i-1].swap_cons(-1, RETRING_ALVS[prec])
                else:
                    s.swap_cons(pos-1, RETRING_ALVS[prec])
            if fol in RETRING_ALVS:
                merged = True
                if pos + 1 == len(s):
                    word[i+1].swap_cons(0, RETRING_ALVS[fol])
                else:
                    s.swap_cons(pos+1, RETRING_ALVS[fol])
            if merged:
                s.remove_cons(pos)
    #print("lar'd I/E and shifted cons " + str(word))
    return word    

def vocalise_gh(word):
    for i in range(len(word)):
        s = word[i]
        if 'ʕ' not in s:
            continue
        pos = s.index('ʕ')
        # GH-V-(C) or C-GH-V-(C) > rising dipthong
        if (pos == s.vowel_position - 1):
            s.remove_cons(pos)
            s.update_vowel(GH_FIRST[s.vowel])
        # (CL)-V-GH > falling dipthong
        elif (pos == s.vowel_position + 1):
            s.remove_cons(pos)
            vowel = GH_SECOND[s.vowel]
            if vowel in GH_TO_REJIG:
                glide, vowel = GH_TO_REJIG[vowel]
                s.add_cons(s.vowel_position, glide)
            s.update_vowel(vowel)
        # GH-L-V-(C) >
        elif (pos == s.vowel_position - 2):
            # V|GH-L-V > falling dipthong in previous
            if i > 0 and word[i-1].is_vowel_final:
                s.remove_cons(pos)
                vowel = GH_SECOND[s.vowel]
                if vowel in GH_TO_REJIG:
                    glide, vowel = GH_TO_REJIG[vowel]
                    word[i-1].add_cons(s.vowel_position, glide)
                    word[i-1].update_vowel(vowel)
            else: # C|GH-L-V > new vowel 'A'
                s.remove_cons(pos)
                s.add_cons(pos, 'ɐ')
        else:
            warnings.warn("uhh there's an error in GH voxing for " + str(word))
    #print('vocalised gh ', str(word))
    return word        

def derelease_stops(word):
    for s in word:
        if s[-1] in STOPS_TO_DERELEASE:
            s.swap_cons(-1, s[-1] + '̚') 
    return word

def desyllabify(word):
    desyl = ''
    phones = []
    stressed = False
    for s in word:
        if s.stress:
            if not stressed:
                desyl += 'ˈ'
                if len(phones)>0 and phones[-1] == '.':
                    phones = phones[:-1]
                phones += ['ˈ']
                stressed = True
            else:
                desyl += 'ˌ'
                if phones[-1] == '.':
                    phones = phones[:-1]
                phones += ['ˌ']
        for l in s:
            desyl += l
        phones += s + ['.']
    if phones[-1] == '.':
        phones = phones[:-1]
    return desyl, phones

def first_shift(word, word_type, desc, root2):
    print('---old word: ' + str(word) + ' ---')
    word = ipaify(word)
    if root2:
        root2 = ipaify(root2)
    words = grammatify(word, word_type, desc, root2)
    new_words = []
    for word, new_type, new_desc in words:
        word = syllabify(word)
        word = agree_vowel_voicing(word)
        word = shift_vowel_first(word)
        word = assimilate_voicing(word)
        word = shift_laryngeal_vowel(word)
        word = shift_cons_first(word)
        word = vocalise_gh(word)
        word = derelease_stops(word)
        word, phones = desyllabify(word)
        print('>>>shift 1: ' + str(word) + ' <<<')
        new_words.append((word, phones, new_type, new_desc))
    return new_words