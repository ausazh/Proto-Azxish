import warnings
from first_shift_constants import VUHINKAM_VOWELS, is_vuh_long_vowel

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
    def merge_cons(self, pos, new):
        # note: merges POS and POS+1
        # can only really be used on position 0 in CCV(C) syllables
        self.remove_cons(pos)
        self.remove_cons(pos)
        self.add_cons(pos, new)