from flask import Flask, render_template, request
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from heapq import nlargest
import json

app = Flask(__name__)



def summarize_text_for_paragraph(text, reduced_value):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Tokenize the text into words
    words = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.casefold() not in stop_words]
    
    # Stemming
    stemmer = PorterStemmer()
    stemmed_words = [stemmer.stem(word) for word in words]
    
    # Calculate word frequencies
    word_frequencies = {}
    for word in stemmed_words:
        if word not in word_frequencies:
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1
    
    # Calculate sentence scores based on word frequencies
    sentence_scores = {}      
    for sentence in sentences:
        for word in word_tokenize(sentence):
            stemmed_word = stemmer.stem(word)
            if stemmed_word in word_frequencies:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_frequencies[stemmed_word]
                else:
                    sentence_scores[sentence] += word_frequencies[stemmed_word]
    
    # Select the top N sentences with highest scores
    summary_sentences = nlargest(reduced_value, sentence_scores, key=sentence_scores.get)
    
    # Sort the summary sentences in their original order
    summary_sentences = sorted(summary_sentences,key=lambda x: sentences.index(x))
    summary_text=''
    # Combine the summary sentences into a summary text
    summary_text = ' '.join(summary_sentences)
    
    return summary_text

def eliminate_abusive_words(text):
    with open('abusive_words.json', 'r') as file:           
        data = json.load(file)
        abusive_words = data['abusive_words']

    words = text.split()
    cleaned_words = []
    for word in words:
        if word.lower() in abusive_words:
            cleaned_words.append("*" * len(word))  # Replace abusive word with asterisks
        else:
            cleaned_words.append(word)
    cleaned_text = " ".join(cleaned_words)
    return cleaned_text

@app.route('/', methods=['GET', 'POST'])
def index():
    text = ''
    summarized_text = ''
    percentage_25_selected = ''
    percentage_50_selected = ''
    num_of_words_in_original_text=''
    num_of_words_in_summarized_text=''
    limit=''
    cleaned_text=''
    if request.method == 'POST':
        text = request.form['text']

        words = word_tokenize(text)
        num_of_words_in_original_text = len(words)

        

        if 'percentage' in request.form:
            limit = int(request.form['percentage'])
       

        # Count the number of sentences
        sentences = sent_tokenize(text)
        num_of_sent = len(sentences)
        
        # Set the reduced_value based on the selected percentage
        if limit == 25:
            reduced_value = int(num_of_sent * 0.25)
            percentage_25_selected = 'checked'
        elif limit == 50:
            reduced_value = int(num_of_sent * 0.50)
            percentage_50_selected = 'checked'
        else:
            reduced_value = num_of_sent

        summarized_text = summarize_text_for_paragraph(text=text, reduced_value=reduced_value)
        cleaned_text = eliminate_abusive_words(summarized_text)

        words = word_tokenize(summarized_text)
        num_of_words_in_summarized_text = len(words)
    
    return render_template('index.html', text=text ,cleaned_text=cleaned_text,percentage_25_selected=percentage_25_selected, percentage_50_selected=percentage_50_selected,num_of_words_in_original_text=num_of_words_in_original_text,num_of_words_in_summarized_text=num_of_words_in_summarized_text)



if __name__ == '__main__':
    app.run(debug=True)
