
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class TextModel(BaseModel):
    text:str
    lines:int



# Importing the summarization code
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from collections import Counter
from heapq import nlargest

def summarize_text(text,num_sentences):

    # Loading spaCy model
    nlp = spacy.load('en_core_web_sm')

    # Tokenization and removing stopwords
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc
              if not token.is_stop and not token.is_punct and token.text != '\n']

    # Calculating word frequency
    word_freq = Counter(tokens)
    if not word_freq:

        return "Error: No words found in the text."

    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = word_freq[word]/max_freq

    # Sentence tokenization
    sent_token = [sent.text for sent in doc.sents]

    sent_score = {}
    for sent in sent_token:
        for word in sent.split():
            if word.lower() in word_freq.keys():
                if sent not in sent_score.keys():
                    sent_score[sent] = word_freq[word]
                else:
                    sent_score[sent] += word_freq[word]

    # Select top-scoring sentences based on user input

    summarized_sentences = nlargest(num_sentences, sent_score, key=sent_score.get)

    return " ".join(summarized_sentences)




@app.get("/")
def home():
    return {"message": "Hello world"}


@app.post("/text-summary")
def text_summary(text_model: TextModel):
    content = text_model.text
    num_of_lines = text_model.lines

    if not content:
        return "Error: Content not provided."
    if num_of_lines <= 0:
        return "Error: Number of sentences not provided."
    
    returned_text = summarize_text(content, num_of_lines)

    return returned_text