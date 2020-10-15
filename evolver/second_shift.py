import warnings
from second_shift_constants import *

# We can't inherited from <str> because we need this to be a mutable class
# ...we'll just
def warn_string(rep, new):
    if type(new) != str:
        print(type(new))
        raise TypeError('attempted to apply Sound ' + rep +
                        ' with non-string ' + str(new) +
                        ' of type ' + str(type(new)))

class Sound:
    def __init__(self, rep):
        self.rep = rep
        self.is_sound = rep not in MARKINGS
        self.to_add = []
        self.to_insert = []
        self.to_insert_syl = []
        self.in_hiatus = False # used only between Break-Hiatus and Great Vowel Shift
    def mutate(self, new):
        warn_string(self.rep, new)
        self.rep = new
    def append(self, new):
        warn_string(self.rep, new)
        self.rep += new
    def add(self, new):
        # similar to delete: prepares a sound for insertion after, but only performs on word.clear()
        warn_string(self.rep, new)
        self.to_add.append(new)
    def insert(self, new):
        # like add() but inserts *before* sound
        warn_string(self.rep, new)
        self.to_insert.append(new)
    def insert_syl(self, new):
        # inserts a sound which will create a new syllable
        self.to_insert_syl.append(new)
    def delete(self):
        # this prepares a sound for deletion; it doesn't actually delete it
        # to delete properly, call container word.clear()
        self.rep = ''
    def has_offglide(self):
        # either the final 'char' is an offglide marker, or final two 'chars' are offglide and nasal
        return (len(self.rep) > 2 and (self.rep[-1] == '̯' or self.rep[-2:] == '̯̃'))
    def __str__(self):
        return self.rep
    def __repr__(self):
        return self.rep
    def __eq__(self, other):
        return self.rep == other
    def __iter__(self):
        return iter(self.rep)
    def __next__(self):
        return next(self.rep)
    def __hash__(self):
        return hash(self.rep)
    def __contains__(self, x):
        return x in self.rep
    def __getitem__(self, key):
        return self.rep[key]

class Word:
    def __init__(self, word):
        self.elements = [Sound(s) for s in word]
    def __iter__(self):
        self.n = 0
        return self
    def __next__(self):
        if (self.n < len(self.elements)):
            sound = self.elements[self.n]
            self.n += 1
            return sound
        raise StopIteration
    def __len__(self):
        return len(self.elements)
    def __getitem__(self, key):
        return self.elements[key]
    def range(self):
        return [(i, self.elements[i]) for i in range(len(self.elements))]
    def sounds(self):
        return [s for s in self.elements if s.is_sound]
    def clear(self):
        l = []
        for s in self.elements:
            s.to_insert.reverse()
            # for x in s.to_insert_syl:
            #     raise 
            for x in s.to_insert:
                l.append(Sound(x))
            if s != '':
                l.append(s)
            for x in s.to_add:
                l.append(Sound(x))
            s.to_insert = []
            s.to_add = []
        self.elements = l
    def __str__(self):
        return ''.join([str(s) for s in self.elements])
    def get_prev(self, pos):
        i = pos - 1
        while i >= 0:
            s = self.elements[i]
            if s.is_sound and s != '':
                return self.elements[i]
            i -= 1
        return None
    def get_fol(self, pos):
        i = pos + 1
        while i < len(self.elements):
            s = self.elements[i]
            if s.is_sound and s != '':
                return self.elements[i]
            i += 1
        return None
    def get_adjacent(self, pos):
        return (self.get_prev(pos), self.get_fol(pos))
    def is_hiatus(self, pos):
        # returns if in hiatus with FOLLOWING
        fol = self.get_fol(pos)
        return fol and self[pos].rep in ALL_VOWELS and fol.rep in ALL_VOWELS

def shift_consonant(word):
    mark = Sound('')
    sign = None
    # print('shifting')
    # syl = []
    # stress = None
    for i, s in word.range():
        if not s.is_sound:
            # stress = s
            # syl = []
            continue
        # syl.append(s)
        prev, fol = word.get_adjacent(i)
        # print('analysing', s)

        # SIGNS
        if sign == 'unreleased':
            # print('signed unreleased', s, mark)
            if s.rep in STOP_CONS:
                mark.mutate(GEMINATE_STOP.get(s, s.rep))
                # print('stop geminated to',mark)
            elif s.rep in AFFRICATISE:
                mark.mutate(PREFRICATE[s])
                s.mutate(AFFRICATISE[s])
                # print('stop preffed to',mark)
            elif mark.rep[:-1] in STOPS_TO_NAS:
                # note that the keys of NASALISE_STOP don't have unreleased marks on them
                mark.mutate(NASALISE_STOP[mark[:-1]])
                # print('stop nased to',mark)
            else:
                mark.mutate('ʔ')
                # print('stop glotted to',mark)
            mark, sign = None, None
        elif sign == 'backelides':
            # print('signed backelides', s, mark)
            if s.rep in ELIDE_BACK_FRIC:
                # print('eliding', s, mark)
                mark.delete()
            elif mark.rep in APPROXIMISE_FRIC:
                # print('approximising', s, mark)
                mark.mutate(APPROXIMISE_FRIC[mark])
            mark, sign = None, None
        elif sign == 'frontelides':
            if s.rep in ELIDE_FRONT_FRIC:
                mark.delete()
            elif mark.rep in APPROXIMISE_FRIC:
                mark.mutate(APPROXIMISE_FRIC[mark])
            mark, sign = None, None
        elif sign == 'gemnas':
            if s == mark:
                c1, c2 = GEMINATE_NASAL[s]
                mark.mutate(c1)
                s.mutate(c2)
            mark, sign = None, None

        ## CONSONANTS
        ## Q > Q /ɢ/
        if s == 'q':
            s.mutate('ɢ')
        # slight labial shift of /ɸ/ > /f/.  parallel /w/ > /ʋ/ handled above
        elif s == 'ɸ':
            s.mutate('f')


        ## Initial glottal stop > G/Q
        elif i < 2 and s == 'ʔ':
            mark, sign = s, 'ʔ'
        elif sign == 'ʔ':
            if s in FRONT_VOWELS:
                mark.mutate('ɟ')
            else:
                mark.mutate('ɢ')
            mark, sign = None, None

        # Non-released stops
        elif '̚' in s:
            # print('found unreleased', s)
            mark, sign = s, 'unreleased'

        # Geminate nasal > nasal + stop
        elif s.rep in GEMINATE_NASAL:
            mark, sign = s, 'gemnas'

        # Looser fricatives
        elif (s.rep in VOCALISE_CCC_FRIC
                and not (prev and prev.rep in VOWELS)
                and not (fol and fol.rep in VOWELS)):
            s.mutate(VOCALISE_CCC_FRIC[s])
            # print('voc fric', s)
            if word[i+1].is_sound:
                s.add('.')
            else:
                s.insert('.')
        elif (s.rep in OFFGLIDE_VC_FRIC
                and prev and prev.rep in VOWELS
                and not prev.has_offglide()
                and prev.rep not in DISALLOW_OFFGLIDE[s]):
            prev.append(OFFGLIDE_VC_FRIC[s])
            s.delete()
        elif s.rep in BACK_ELIDES:
            # print('mark backelide', s)
            mark, sign = s, 'backelides'
        elif s.rep in FRONT_ELIDES:
            mark, sign = s, 'frontelides'
        elif s.rep in APPROXIMISE_FRIC:
            # print('approximating', s)
            s.mutate(APPROXIMISE_FRIC[s])

    # final mark-clearing
    if sign == 'unreleased':
        # print('final unreleased', mark)
        if mark.rep[:-1] in STOPS_TO_NAS:
            # print('nasalising', mark)
            # note that the keys of NASALISE_STOP don't have unreleased marks on them
            mark.mutate(NASALISE_STOP[mark[:-1]])
        else:
            # print('glotting', mark)
            mark.mutate('ʔ')
    elif sign == 'backelides':
        # print('final signed backelides', mark)
        if mark.rep in APPROXIMISE_FRIC:
            # print('approximising', s, mark)
            mark.mutate(APPROXIMISE_FRIC[mark])
    elif sign == 'frontelides':
        if mark.rep in APPROXIMISE_FRIC:
            mark.mutate(APPROXIMISE_FRIC[mark])

    word.clear()
    # print('shifted consonants', word)
    return word

def shift_place(word):
    marks = []
    sign = None
    s_to_mutate = None

    for i, s in word.range():
        if not s.is_sound or s == '':
            continue
        # print(s, marks, sign)
        # re-fix gh > j
        if s.rep[0] == 'e':
            prev = word.get_prev(i)
            print(s, prev)
            if prev and prev == 'ɣ':
                prev.mutate('j')
                print('now', s, prev)

        # SIGNS
        # see sign assignments below for details on the shift
        if sign == 'alv-pal':
            if s.rep in PALATAL_TRIGGERS:
                # print('trigger pal>vel!', marks, s)
                for m in marks:
                    m.mutate(PALATAL_PLACE_SHIFT[m]) 
                s_to_mutate = PALATAL_PLACE_SHIFT[s]
                marks, sign = [], None
            elif s.rep in PALATAL_BLOCKS:
                sign = 'alv'
                marks.append(s)
                continue
            elif s.rep in ALVEOLAR_PLACE_SHIFT:
                marks.append(s)
                continue
            else:
                if s.rep in ALVEOLAR_SHIFT_BLOCKS:
                    s_to_mutate = ALVEOLAR_SHIFT_BLOCKS[s]
                else:
                    for m in marks:
                        m.mutate(ALVEOLAR_PLACE_SHIFT[m]) 
                marks, sign = [], None
        elif sign == 'alv':
            if s.rep in ALVEOLAR_PLACE_SHIFT:
                marks.append(s)
                continue
            else:
                if s.rep in ALVEOLAR_SHIFT_BLOCKS:
                    s_to_mutate = ALVEOLAR_SHIFT_BLOCKS[s]
                else:
                    for m in marks:
                        m.mutate(ALVEOLAR_PLACE_SHIFT[m]) 
                marks, sign = [], None
        elif sign == 'x':
            if s.rep == 'xʷ':
                s_to_mutate = 'ħ'
                marks[0].mutate('ħ')
            else:
                prev = word.get_prev(i-1)
                if prev and prev.rep in RHOTS:
                    prev.delete()
                if s.rep in RHOTS:
                    s.delete()
                marks[0].mutate('ʀ̥')
            marks, sign = [], None

        # deal with sounds after (must elif through to prevent multiple shifts)
        # dental TTH > TF, DDH > DV
        if s_to_mutate:
            s.mutate(s_to_mutate)
            s_to_mutate = None
        elif s == 't͡θ':
            prev, fol = word.get_adjacent(i)
            if not fol or fol.rep not in TF_BLOCKS:
                s.mutate('t')
                s.add('f')
            elif not prev or prev.rep not in TF_BLOCKS:
                s.mutate('t')
                s.insert('f')
            else:
                s.mutate('f')
        elif s == 'd͡ð':
            prev, fol = word.get_adjacent(i)
            if not fol or fol.rep not in TF_BLOCKS:
                s.mutate('d')
                s.add('ʋ')
            elif not prev or prev.rep not in TF_BLOCKS:
                s.mutate('d')
                s.insert('ʋ')
            else:
                s.mutate('ʋ')

        # retroflex > alveolar
        # simple place shift.  affricates and geminates shift regularly
        elif s.rep in RETROFLEX_PLACE_SHIFT:
            s.mutate(RETROFLEX_PLACE_SHIFT[s])

        # alveolar > palatal
        # alveolar > alveolar with following V/F/U/TTH
        # alveolar > velar with following palatal, with some exceptions
        # note that both T-TTH and simple TTH evolve into simple TF
        elif s.rep in ALVEOLAR_PLACE_SHIFT:
            if s.rep in PALATAL_BLOCKS:
                marks, sign = [s], 'alv'
            else:
                marks, sign = [s], 'alv-pal'
        
        # palatal > velar
        # affricate geminates appear alveolar, and are handled there
        # note that PALATAL_PLACE_SHIFT contains alveolar consonants
        # ALV_P_S is checked first however, they will have no effect on flow
        # Note that JE > JE
        elif s.rep in PALATAL_PLACE_SHIFT:
            s.mutate(PALATAL_PLACE_SHIFT[s])
        
        # Simple velar changes
        elif s.rep in ['k', 'g']:
            s.delete()
        elif s.rep in VELAR_NASAL_SHIFT:
            s.mutate(VELAR_NASAL_SHIFT[s])
        
        # X, G > R̂H, R̂, fusing with any adjacent Rs also
        # BUT Xʷ and X-Xʷ > H
        elif s.rep == 'ɣ':
            prev, fol = word.get_adjacent(i)
            if prev and prev.rep in RHOTS:
                prev.delete()
            if fol and fol.rep in RHOTS:
                fol.delete()
            s.mutate('ʀ')
        elif s.rep == 'x':
            marks, sign = [s], 'x'
        elif s.rep == 'xʷ':
            s.mutate('ħ')

    # Final mark cleanup
    if sign == 'alv-pal' or sign == 'alv':
        for m in marks:
            m.mutate(ALVEOLAR_PLACE_SHIFT[m]) 
    elif sign == 'x':
        prev = word.get_prev(i)
        # print(word, prev, marks, s, i)
        if prev and prev.rep in RHOTS:
            prev.delete()
        marks[0].mutate('ʀ̥')

    word.clear()

    for _, s in word.range():
        if s.rep in PLACESHIFT_CLEANUP:
            s.mutate(PLACESHIFT_CLEANUP[s])

    # print('shifted place', word)
    return word

def shift_cluster(word):
    sign = None
    for i, s in word.range():
        if not s.is_sound or s == '':
            continue
        prev, fol = word.get_adjacent(i)

        # Stop + unvoiced R > delete stop'
        # Note that geminate stop + R only removes one layer of stop
        if fol == 'r̥' and s.rep in STOPS_TO_DELETE:
            s.mutate(STOPS_TO_DELETE[s])
            sign = 'no-comp'

        # Stop + Ś > c͡ɕ
        if fol == 'ɕ' and s.rep in STOPS_TO_AFFRICATISE:
            fol.mutate('c͡ɕ')
            s.delete()

        # Separate palatal-V/U/L or V/U/L-palatal clusters with /ɐ/
        # but allow sibilants/affricates/J
        if (fol and (
            (fol.rep in PALS_TO_DECLUSTER and
                s.rep in VULS_TO_DECLUSTER) or 
            (s.rep in PALS_TO_DECLUSTER and
                fol.rep in VULS_TO_DECLUSTER))):
            if word[i+1].is_sound:
                s.add('ɐ')
                s.add('.')
            else:
                s.add('.')
                s.add('ɐ')

        # Initial trill compensation
        if not prev and sign != 'no-comp' and s.rep in TRILLS_TO_COMPENSATE:
            word[0].insert(s.rep)
            word[0].insert('ɐ')

    word.clear()
    print('rejigged clusters', word)
    return word

def break_hiatus(word):
    for i, s in word.range():
        if not s.is_sound or s == '':
            continue
        if not word.is_hiatus(i):
            continue
        fol = word.get_fol(i)

        
        # Nasal breaking: descend a nasal cons from a nasal vowel
        if s.rep in NASAL_VOWELS:
            if s.rep in M_NASALS:
                s.mutate(M_NASALS[s])
                fol.insert('m')
            elif s.rep in N_NASALS:
                s.mutate(N_NASALS[s])
                fol.insert('n')
            elif s.rep in NJ_NASALS:
                s.mutate(NJ_NASALS[s])
                fol.insert('ɲ')
            elif s.rep in NG_NASALS:
                s.mutate(NG_NASALS[s])
                fol.insert('ɴ')
        else:
            s.in_hiatus = True

    # print('broken hiatuses', word)
    return word

class Vowel:
    def __init__(self, s, sound, p_stress, s_stress):
        self.s = s
        self.sound = sound
        self.stress = 0
        if p_stress:
            self.stress = 1
        elif s_stress:
            self.stress = 2
        self.inf = None
        self.in_hiatus = sound.in_hiatus
    def is_front(self):
        return self.s in FRONT_VOWELS
    def is_mid(self):
        return self.s in CENTRAL_VOWELS
    def is_back(self):
        return self.s in BACK_VOWELS
    def mutate(self, new):
        self.s = new
        self.sound.mutate(new)

# Front is True or False; determine frontness elsewhere!
def do_shift_vowel(v, front):
    inf_i = 0
    if not front:
        inf_i = 1
    # print('shifting s', v.s)

    if v.in_hiatus and v.s in NO_SHIFT_BEFORE_HIATUS:
        pass
    elif v.s in BOTH_INF_SHIFT:
        v.mutate(BOTH_INF_SHIFT[v.s][inf_i])
    elif v.s in BOTH_UNINF_SHIFT:
        v.mutate(BOTH_UNINF_SHIFT[v.s])
    elif v.s in NO_SHIFT:
        pass
    elif v.stress > 0:  
        if v.s in STR_INF_SHIFT:
            v.mutate(STR_INF_SHIFT[v.s][inf_i])
        elif v.s in STR_UNINF_SHIFT:
            v.mutate(STR_UNINF_SHIFT[v.s])
        elif v.s in STR_NO_SHIFT:
            pass
        else:
            raise KeyError('Unhandled stressed vowel ' + v.s)
    else:  
        if v.s in UNS_INF_SHIFT:
            v.mutate(UNS_INF_SHIFT[v.s][inf_i])
        elif v.s in UNS_UNINF_SHIFT:
            v.mutate(UNS_UNINF_SHIFT[v.s])
        elif v.s in UNS_NO_SHIFT:
            pass
        else:
            raise KeyError('Unhandled unstressed vowel ' + v.s)
    # print('shifted vowel', v.s)

def shift_vowel(word):
    vowels = [] 
    p_stress_v = None
    s_stress_v = None

    # identify vowels and stress
    p_stress = False
    s_stress = False
    influence = None
    # print(word)
    for _, s in word.range():
        if s == 'ˈ':
            p_stress = True
            s_stress = False
        elif s == 'ˌ':
            s_stress = True
            p_stress = False
        elif s == '.':
            p_stress = False
            s_stress = False
        
        elif s.rep in ABS_ALL_VOWELS:
            v = Vowel(s.rep, s, p_stress, s_stress)
            if p_stress:
                influence = v
                p_stress_v = v
            elif s_stress:
                s_stress_v = v
            vowels.append(v)
            print(s.rep, p_stress, s_stress)

    # Update influence of vowels
    for v in vowels:
        if v.stress == 1:
            influence = v
        elif v.stress == 2:
            influence = v
        v.inf = influence

    # let the shifting begin!
    # Shift the Stressed Vowels first
    # If a stressed vowel is Central, then shift it:
    # First to other stress; otherwise to next following
    # Otherwise default to Back
    # Note that there can be exceptions to this
    # TODO -- output one front and one back word in these cases
    front = False
    if p_stress_v.is_mid():
        if s_stress_v and not s_stress_v.is_mid():
            front = s_stress_v.is_front()
        else:
            for v in vowels:
                if not v.is_mid():
                    front = v.is_front()
                    break
    else:
        front = p_stress_v.is_front()
    # print('is front', p_stress_v.rep, front)
    do_shift_vowel(p_stress_v, front)
    # Note that all post-shift vowels are either front or back
    # So we always have primary stress as a backup influence from now
    if s_stress_v:
        if s_stress_v.is_mid():
            front = p_stress_v.is_front()
        else:
            front = s_stress_v.is_front()
        do_shift_vowel(s_stress_v, front)

    # Then shift all the rest of the vowels
    for v in vowels:
        if v.stress > 0:
            continue # already done stressed vowels
        do_shift_vowel(v, v.inf.is_front())

    # print('vowels shifted', word)
    return word

def open_guttural(word):
    for i, s in word.range():
        if not s.is_sound or s == '':
            continue
        prev, fol = word.get_adjacent(i)
        if (s.rep in AFTER_SHIFT_VOWELS and (
                (prev and prev.rep in ['ʀ̥', 'ʀ']) or
                (fol and fol.rep in ['ʀ̥', 'ʀ']) )):
            s.mutate(OPEN_ADJ_GUTR[s])
            # open *again* if specifically before guttural
            # this occurs for long front vowels, which gain a central glide
            if s.rep in OPEN_BEF_GUTR and fol and fol.rep in ['ʀ̥', 'ʀ']:
                s.mutate(OPEN_BEF_GUTR[s])

    # print('gut-vowels opened', word)
    return word

def denasalise(word):
    for i, s in word.range():
        if not s.is_sound or s == '':
            continue
        prev, fol = word.get_adjacent(i)
        if '̃' in s.rep:
            s.mutate(s.rep.replace('̃', ''))
            nasal = ''
            if s.rep in BACK_VOWELS:
                nasal = 'm'
            elif s.rep in CENTRAL_VOWELS:
                nasal = 'ɴ'
            elif s.rep in FRONT_VOWELS:
                nasal = 'n'
            
            if fol and fol.rep in TO_PRENASALISE:
                s.add(TO_PRENASALISE[fol.rep])
            elif not fol or fol.rep in AFTER_GUT_VOWELS:
                s.add(nasal)
            elif not prev or prev.rep in AFTER_GUT_VOWELS:
                s.insert(nasal)
    word.clear()
    # print('nasals deleted', word)
    return word
    
def delengthen(word):
    for _, s in word.range():
        if not s.is_sound or s == '':
            continue
        s.mutate(s.rep.replace('ː', ''))

    # print('length deleted', word)
    return word    
    
def merge_trill(word):
    for _, s in word.range():
        if not s.is_sound or s == '':
            continue
        s.mutate(s.rep.replace('ʀ̥', 'r̥'))
        s.mutate(s.rep.replace('ʀ', 'r'))

    # print('trills merged', word)
    return word    

def rare_sounds_shift(word):
    for _, s in word.range():
        if not s.is_sound or s == '':
            continue
        if s.rep in SHIFT_RARE_SOUND:
            s.mutate(SHIFT_RARE_SOUND[s])

    # print('rare sounds merged', word)
    return word    

def scriptify(sounds):
    stress = False
    ipa = ''
    word = ''
    # print(sounds)
    for i, s in sounds.range():
        fol = sounds.get_fol(i)
        if s == 'ˈ' or s == 'ˌ':
            ipa += s.rep
            stress = True
        elif s == '.':
            stress = False
        elif s.rep in FINAL_VOWELS:
            ipa += s.rep
            index = 0
            if stress: index = 1
            word += FINAL_VOWELS[s][index]
        elif i + 1 == len(sounds) and s.rep in FINAL_ALT_FINAL:
            ipa += s.rep
            word += FINAL_ALT_FINAL[s]
        elif fol and (s.rep, fol.rep) in FINAL_ALT_GEMS:
            ipa += s.rep
            word += FINAL_ALT_GEMS[(s.rep, fol.rep)] 
        elif s.rep in FINAL_CONS:
            ipa += s.rep
            word += FINAL_CONS[s] 
        else:
            ipa += s.rep
            raise KeyError("couldn't find letter for " + s.rep + ' in ' + str(word))

    return word, ipa

# Evolution steps: Second Shift
def second_shift(word):
    word = Word(word)
    word = shift_consonant(word)
    word = shift_place(word)
    word = shift_cluster(word)
    word = break_hiatus(word)
    word = shift_vowel(word)
    word = open_guttural(word)
    # print('>>>shift 2: ' + str(word) + ' <<<')
    # final steps
    word = denasalise(word)
    word = delengthen(word)
    word = merge_trill(word)
    word = rare_sounds_shift(word)
    word, ipa = scriptify(word)
    print('>>>final:', word, '/' + ipa + '/', '<<<')
    print()
    return word, ipa
