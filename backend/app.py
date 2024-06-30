from flask import Flask, request, jsonify
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
from spellchecker import SpellChecker
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
    corrected_text = spell.correction(text)
    if corrected_text == None :
        corrected_text = text
    return corrected_text

# Define a route for making predictions
@app.route('/spell_correct', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    dataAfterSplit = data['sentence'].split(' ')
    # for singleWord in dataAfterSplit:
    #     if singleWord not in updated_words:
    #         data_updated = correct_spelling(singleWord)
    #         data['sentence'] = data['sentence'].replace(singleWord, data_updated)
    data_updated = ""
    for singleWord in dataAfterSplit:
        print(singleWord)
        singleWord = singleWord.replace("\n", "")
        singleWord = singleWord.replace(".", "")
        data_updated += correct_spelling(singleWord) + " "
    return jsonify({'correctedSentence': data_updated})

if __name__ == '__main__':
    app.run(debug=True)