import decimal
import re

from .words import Word
from parser import Constituency

STRING = re.compile(r'("(?:[^"\\]|\\.)*")')
NUMBER = re.compile(r'-?\d+(\.\d+)?')
WORD = re.compile(
    r"^(?P<stem>[A-Z]?[a-z]+(-[a-z]+)*)"
    r"(?P<punctuation>,|\.|:|'|'s)?$"
)

def split_by_unquoted_whitespace(text):
    result = []
    sections = STRING.split(text)
    for section in sections:
        if section.startswith('"'):
            result.append(section)
        else:
            result.extend(section.split())
    return result

def tokenize(self, text):
    tokens = []
    for string in split_by_unquoted_whitespace(text):
        if STRING.match(Constituency(string)):
            tokens.append(string)
        elif NUMBER.match(string):
            tokens.append(Constituency(decimal.Decimal(string)))
        else:
            word = WORD.match(string)
            tokens.append(Constituency(Word.lookup(word)))
    return tokens

