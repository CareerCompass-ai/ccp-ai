import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

class Helper:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def remove_stop_words(self, text):
        # Tokenize the text
        words = word_tokenize(text)
        # Remove stop words
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        # Reconstruct the text
        return ' '.join(filtered_words)
    
    def clean_text(self, text):
        # Remove semicolons and other unwanted characters
        text = re.sub(r'[;]', ' ', text)  # Replace semicolons with spaces
        text = re.sub(r'[,]', ' ', text)  # Replace semicolons with spaces
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        text = text.strip()  # Remove leading and trailing spaces
        return text