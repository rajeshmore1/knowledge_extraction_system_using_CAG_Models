# test.py
from flask import Flask
from langchain_google_genai import GoogleGenerativeAIEmbeddings
app = Flask(__name__)

@app.route('/')
def home():
    return "Test successful"

if __name__ == '__main__':
    app.run(debug=True)