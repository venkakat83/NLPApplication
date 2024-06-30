from flask import Flask, request, jsonify
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
from spellchecker import SpellChecker
import re
from collections import Counter
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

spell = SpellChecker()
 # List the default words
word_frequency = spell.word_frequency
default_words = list(word_frequency.keys())

print(len(default_words))


spell.word_frequency.load_text_file('./backend/corpus.txt')

updated_words = list(word_frequency.keys())

print(len(updated_words))
################################################################################
#counter stores the frequency of each word in the corpus (big.txt).
# words function is used to tokenize the content of 'big.txt', and the Counter is created to count the occurrences of each word.

def words(text):
    return re.findall(r'\b\w+\b', text.lower())

def read_file(file_path):
    encodings = ['utf-8', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            print(f"{encoding} encoding failed. Trying next encoding.")
    # Fallback to reading with replacement characters if all encodings fail
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        return file.read()

text = read_file('./backend/corpus.txt')
WORDS = Counter(words(text))
#print(len(WORDS))
#print(WORDS.most_common(10))

#function to calculate the probability of a word occurring in the corpus.
#probability is calculated as the count of the word divided by the total count of words.
def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    print(f'the word {word} probability is {WORDS[word] / N})')
    #print(N)
    #print(WORDS[word] / N)
    return WORDS[word] / N

#filter a set of words and returns the subset that appears in the dictionary of known words (WORDS).
def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

# checks for known words among the edits that are one, two, or zero edits away from the given word.
def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or  [word])

#function takes a word and returns the most probable spelling correction for that word, 
#find the candidate word from a list of candidates (candidates(word)) that maximizes a scoring function P.
def correction(word): 
    "Most probable spelling correction for word."
    print(max(candidates(word), key=P))
    return max(candidates(word), key=P)

#function generates all edits that are one edit away from the given word.
def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    # splits(apple) generates: [('', 'apple'),('a', 'pple'),('ap', 'ple'),('app', 'le'),('appl', 'e'),('apple', '')]
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    #For each (L, R) in splits where R is not empty:('', 'apple') → 'pple'('a', 'pple') → 'aple'('ap', 'ple') → 'ale'('app', 'le') → 'ape'('appl', 'e') → 'appl'('apple', '') → 'apple'
    deletes    = [L + R[1:]               for L, R in splits if R]
    #swap the positions of the first two characters in the original word word for each tuple (L, R) where len(R) > 1.
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)
################################################################################
# print(spell.word_frequency.words())
# spell.known(['hello', 'world', 'this', 'is', 'a', 'test'])

# word_frequency = spell.word_frequency

# # List the default words
# default_words = list(word_frequency.keys())

# print(len(default_words))


# word_frequency = spell.word_frequency

# # Specify the word for which you want to check the probability
# word_to_check = "Helo"

# # Check the probability of the word
# word_probability = spell.word_usage_frequency(word_to_check)

# # Print the probability of the word
# print("Probability of", word_to_check, ":", word_probability)

def correct_spelling(text):
    contains_dot = False
    if "." in text:
        contains_dot = True
    corrected_text = spell.correction(text)
    if corrected_text == None :
        corrected_text = text
    elif contains_dot:
        corrected_text = corrected_text + "."
    return corrected_text

# Define a route for making predictions
@app.route('/spell_correct', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    #data_udpated = correct_spelling(data['sentence'])
    data['sentence'] = data['sentence'].replace("\n", " ")
    dataAfterSplit = data['sentence'].split(" ")
    data_udpated = ""
    for singleWord in dataAfterSplit: 
        data_udpated = data_udpated + " " + correct_spelling(singleWord)
        print('Highest probability word selected for wrong word "' + singleWord + '" is : ' +correction(singleWord))
    return jsonify({'correctedSentence': data_udpated})

if __name__ == '__main__':
    app.run(debug=True)