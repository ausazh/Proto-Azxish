
# --- FIRST SHIFT CONSTANTS --- #

IPA_VUHINKAM_DIGRAPHS = {'ts': 't͡s', 'ch': 't͡ʃ', 'sh': 'ç', 'gh': 'ʕ'}

IPA_VUHINKAM = {'m': 'm', 'n': 'n', 'ñ': 'ŋ',
                'p': 'p', 't': 't', 'k': 'k', 'q': 'q',
                'f': 'f', 's': 's', 'x': 'x', 'h': 'ħ',
                'v': 'v', 'z': 'z', 'g': 'ɣ',
                'w': 'w', 'l': 'l', 'j': 'j', 'r': 'r',
                'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'u',
                'â': 'aː', 'ê': 'eː', 'î': 'iː', 'ô': 'oː', 'û': 'uː'}

IRREG_GEMINATE = {'t͡s': 't', 't͡ʃ': 't', 'd͡z': 'd', 'd͡ʒ': 'd', 'xʷ': 'x'}

VUHINKAM_SHORT_VOWELS = ['a', 'e', 'i', 'o', 'u']
VUHINKAM_VOWELS = ['a', 'e', 'i', 'o', 'u', 'aː', 'eː', 'iː', 'oː', 'uː']
VUHINKAM_LIQUIDS = ['r', 'w', 'l', 'j', 'm', 'n', 'ŋ']
VUHINKAM_NASALS = ['m', 'n', 'ŋ']
VUHINKAM_FRICS = ['f', 's', 'x', 'ħ', 'v', 'z', 'ɣ', 'ç', 'ʕ']
VUHINKAM_STOPS_AFS = ['p', 't', 'k', 'q', 'ts', 'ch']
VUHINKAM_APPXS_R = ['w', 'l', 'j', 'r']
ILLEGAL_STOPNAS = {'p': 'm', 't': 'n', 'k': 'ŋ', 'q': 'ŋ'}

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
TO_VOICE_FRICS = {'f': 'v', 's': 'z', 'ç': 'ʝ', 'x': 'ɣ', 'ħ': 'ʕ'}
VOICING_FOLLOWS_EXCS = ['w', 'l', 'r', 'j']
VOICING_NASALS = ['ĩː', 'ũː', 'ĩ', 'ũ']

LARYNGEALS = ['q', 'ɢ', 'ħ', 'ʕ']
LARING_VOWELS = {'i': 'ɨ', 'ĩ': 'ɨ̃', 'ɛ': 'ɜ',
                 'iː': 'ɨː', 'ĩː': 'ɨ̃ː', 'ɛː': 'ɜː'}
FIRST_PALATALS = ['t͡ʃ', 'd͡ʒ', 'ç', 'ʝ', 'j']
FIRST_I_VARS = ['i', 'iː', 'ĩ', 'ĩː']
RETRING_ALVS = {'t': 'ʈ', 'd': 'ɖ', 'n': 'ɳ', 'n̥': 'ɳ̊',
                's': 'ʂ', 'z': 'ʐ', 'l': 'ɭ', 'ɬ': 'ɭ̥'}
GH_FIRST = {'ɨː': 'ɐː', 'ɨ': 'ɐɪ̯', 'ɨ̃ː': 'ɐ̃ː', 'ɨ̃': 'ɐ̃ː',
            'ɜː': 'a:', 'ɜ': 'ɑɛ̯', 
            'uː': 'ɐʊ̯', 'u': 'ɐʊ̯', 'ũː': 'ɐʊ̯̃', 'ũ': 'ɐʊ̯̃',
            'ɔː': 'ɑː', 'ɔ': 'ɐɔ̯', 
            'ɘː': 'ɘː', 'ɐ': 'ɐː', 'ɑː': 'ɑː', 'ɑ': 'ɑː',
            'aː': 'aː', 'a': 'aː', 'æː': 'ɑɛ̯', 'æ': 'ɑɛ̯'}
# Note: this should be an exhaustive list of all vowel phonemes at this point
GH_SECOND = {'iː': 'iɐ̯', 'i': 'jɐ', 'ĩː': 'iɐ̯̃', 'ĩ': 'jɐ̃',
             'ɨː': 'ɐː', 'ɨ': 'ɐː', 'ɨ̃ː': 'ɐ̃ː', 'ɨ̃': 'ɐ̃ː',
             'ɛː': 'æː', 'ɛ': 'ɛɐ̯', 'ɜː': 'aː', 'ɜ': 'ɑː', 
             'eː': 'iɐ̯', 'e': 'ɛɐ̯',
             'uː': 'uɐ̯', 'u': 'wa', 'ũː': 'uɐ̯̃', 'ũ': 'wɐ̃',
             'ɔː': 'ɑː', 'ɔ': 'ɔɐ̯', 'oː': 'uɐ̯', 'o': 'ɔɐ̯',
             'ɘː': 'ɘː', 'ɐ': 'ɐː', 'ɑː': 'ɑː', 'ɑ': 'ɑː',
             'aː': 'aː', 'a': 'aː', 'æː': 'aː', 'æ': 'ɛɐ̯'}
GH_TO_REJIG = {'jɐ': ('j', 'ɐ'),
               'jɐ̃': ('j', 'ɐ̃'),
               'wɐ': ('w', 'ɐ'),
               'wɐ̃': ('w', 'ɐ̃')}
STOPS_TO_DERELEASE = ['p', 'b', 't', 'd', 'ʈ', 'ɖ', 'k', 'g', 'q', 'ɢ']

def is_vuh_long_vowel(v):
    return v in VUHINKAM_VOWELS and len(v) > 1
def lengthen_vuh_vowel(v):
    if is_vuh_long_vowel(v):
        return v
    return v + 'ː'
def shorten_vuh_vowel(v):
    return v[:-1]

# --- SECOND SHIFT CONSTANTS --- #