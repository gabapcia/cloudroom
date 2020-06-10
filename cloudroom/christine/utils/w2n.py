import re
from typing import Any, Dict, Tuple


# Adapted from https://stackoverflow.com/a/53400669
class Word2Number:
    ordinal_words = {
        'first': 1, 
        'second': 2, 
        'third': 3, 
        'fifth': 5, 
        'eighth': 8, 
        'ninth': 9, 
        'twelfth': 12
    }

    ordinal_endings = [
        ('ieth', 'y'), 
        ('th', '')
    ]
    
    scales = [
        'hundred', 
        'thousand', 
        'million', 
        'billion', 
        'trillion'
    ]

    units = [
        'zero', 
        'one',
        'two',
        'three',
        'four',
        'five',
        'six',
        'seven',
        'eight',
        'nine',
        'ten',
        'eleven',
        'twelve',
        'thirteen',
        'fourteen',
        'fifteen',
        'sixteen',
        'seventeen',
        'eighteen',
        'nineteen',
    ]

    tens = [
        '', 
        '', 
        'twenty', 
        'thirty', 
        'forty', 
        'fifty', 
        'sixty', 
        'seventy', 
        'eighty', 
        'ninety'
    ]


    def __init__(self):
        self.numwords = self.get_numwords()


    def get_numwords(self) -> Dict[str, Tuple[int, int]]:
        numwords = {
            'and': (1, 0)
        }

        for idx, word in enumerate(self.units): 
            numwords[word] = (1, idx)
        for idx, word in enumerate(self.tens): 
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(self.scales): 
            numwords[word] = (10 ** (idx * 3 or 2), 0)
        
        return numwords


    def __is_numword(self, x: Any) -> bool:
        if Word2Number.is_number(x):
            return True
        if x in self.numwords:
            return True
        return False


    def __from_numword(self, x: str) -> Tuple[int, int]:
        if Word2Number.is_number(x):
            scale = 0
            increment = int(x.replace(',', ''))
            return scale, increment
        return self.numwords[x]


    def parse(self, textnum: str) -> str:
        textnum = textnum.replace('-', ' ')

        current = result = 0
        curstring = ''
        onnumber = lastunit = lastscale = False

        for word in textnum.split():
            if word in self.ordinal_words:
                scale, increment = (1, self.ordinal_words[word])
                current = current * scale + increment
                if scale > 100:
                    result += current
                    current = 0
                onnumber = True
                lastunit = False
                lastscale = False
            else:
                word_before = word
                for ending, replacement in self.ordinal_endings:
                    if word.endswith(ending):
                        word = "%s%s" % (word[:-len(ending)], replacement)

                if (
                    not self.__is_numword(word) or 
                    (word == 'and' and not lastscale)
                ):
                    if onnumber:
                        curstring += repr(result + current) + " "
                    curstring += word_before + " "
                    result = current = 0
                    onnumber = False
                    lastunit = False
                    lastscale = False
                else:
                    scale, increment = self.__from_numword(word)
                    onnumber = True

                    if lastunit and (word not in self.scales):                                                                                                                                                                                                                
                        curstring += repr(result + current)                                                                                                                                                                                                                                       
                        result = current = 0                                                                                                                                                                                                                                                      

                    if scale > 1:                                                                                                                                                                                                                                                                 
                        current = max(1, current)                                                                                                                                                                                                                                                 

                    current = current * scale + increment                                                                                                                                                                                                                                         
                    if scale > 100:                                                                                                                                                                                                                                                               
                        result += current                                                                                                                                                                                                                                                         
                        current = 0                                                                                                                                                                                                                                                               

                    lastscale = False                                                                                                                                                                                                              
                    lastunit = False                                                                                                                                                
                    if word in self.scales:                                                                                                                                                                                                             
                        lastscale = True                                                                                                                                                                                                         
                    elif word in self.units:                                                                                                                                                                                                             
                        lastunit = True

        if onnumber:
            curstring += repr(result + current)

        return re.sub(r'(\d+) percent', r'\1%', curstring).strip()

    @staticmethod
    def is_number(x: Any) -> bool:
        if type(x) == str:
            x = x.replace(',', '')
        try:
            float(x)
        except:
            return False
        return True
