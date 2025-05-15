# 📰 News Summarization Project

This project focuses on cleaning raw news datasets and summarizing articles using both extractive and abstractive NLP and generative AI concepts.

---

## 📁 Project Structure

- `data_cleaning.ipynb`: Cleans raw news article datasets by removing noise, standardizing text, and preparing a structured format.
- `news_summariztaion.ipynb`: Performs news summarization using:
  - Extractive methods (e.g., TextRank)
  - Abstractive methods (e.g., Transformer models like BART, T5)

---

## 🔧 Setup Instructions

1. Clone this repo:
   ```bash
   git clone https://github.com/your-username/news-summarization.git
   cd news-summarization
    ```
2. Create a virtual environment:
    ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows

    ```
4. Install dependencies:
    ```bash
   pip install -r requirements.txt

    ```
   
## 📊 Features
Data Cleaning:

Removes nulls, duplicates, stopwords, URLs, and unwanted characters.

Tokenizes and lowercases all text.

Summarization Models:

Extractive: TextRank

Abstractive: BART / T5 via Hugging Face Transformers

Evaluation:

ROUGE metric for summary quality

Comparison with original headlines

### 📌 Requirements
See requirements.txt for full package list.

###  Integrated Streamlit UI 

🧾 File: streamlit_app_v2.py
Tabs:

🔍 Enter an article → Get summary

👤 Enter a user ID → Get top-K recommended articles (with summaries)

❤️ User feedback (like/dislike) → Saved in local file

Backend:

Loads summarized_articles_t5.csv

Loads FAISS index + BERT model

Displays summarized recommendations

### 🚧 Note
Data files used in the notebooks are not included due to size/privacy constraints.

To replicate:

Use your own news article dataset (CSV/JSON).

Ensure it has columns like article and headline.


---

### 📦 `requirements.txt`

```txt
numpy
pandas
nltk
scikit-learn
matplotlib
seaborn
beautifulsoup4
spacy
sumy
transformers
torch
tqdm
rouge-score
gensim
sentencepiece




