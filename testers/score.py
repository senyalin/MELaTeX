import os
import difflib
import Levenshtein
from nltk.translate.bleu_score import sentence_bleu
from pylatexenc.latexwalker import LatexWalker

def bleu(ans,res):
    ratio = sentence_bleu([res],ans,weights=(0.25, 0.25, 0.25, 0.25))
    return ratio