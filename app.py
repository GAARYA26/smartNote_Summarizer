
from flask import Flask, render_template, request, send_file
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import os
from werkzeug.utils import secure_filename
import PyPDF2
import io
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------- PDF TEXT EXTRACTION --------
def extract_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

# -------- HIGHLIGHT FUNCTION --------
def highlight_text(text, keywords):
    for word in keywords:
        pattern = re.compile(rf'\b({word})\b', re.IGNORECASE)
        text = pattern.sub(r'<mark>\1</mark>', text)
    return text

# -------- KEYWORD EXTRACTION --------
def extract_keywords(text):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=8)
    X = vectorizer.fit_transform([text])
    return list(vectorizer.get_feature_names_out())

# -------- NEW CORRECT SUMMARIZATION --------
def summarize_text(text, num_sentences=3, query=None):
    sentences = re.split(r'(?<=[.!?]) +', text)

    if len(sentences) <= num_sentences:
        return [], sentences, sentences

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)

    # 👉 NEW: sentence score = sum of TF-IDF weights
    scores = np.sum(tfidf_matrix.toarray(), axis=1)

    sentence_scores = [(sentences[i], float(scores[i])) for i in range(len(sentences))]

    ranked = sorted(sentence_scores, key=lambda x: x[1], reverse=True)

    selected = [sent for sent, score in ranked[:num_sentences]]

    return ranked, selected, sentences

# -------- DOWNLOAD ROUTE --------
@app.route("/download")
def download():
    summary_text = request.args.get("text", "")
    buffer = io.BytesIO()
    buffer.write(summary_text.encode())
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="summary.txt",
        mimetype="text/plain"
    )

# -------- MAIN ROUTE --------
@app.route("/", methods=["GET", "POST"])
def index():
    summary = []
    ranked = []
    original = ""
    keywords = []
    all_sentences = []
    highlighted_text = ""

    if request.method == "POST":

        original = request.form.get("text", "")
        file = request.files.get("file")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            if filename.endswith(".pdf"):
                original = extract_pdf(path)
            else:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    original = f.read()

        if original.strip():
            num = int(request.form.get("length", 3))
            ranked, summary, all_sentences = summarize_text(original, num)
            keywords = extract_keywords(original)
            highlighted_text = highlight_text(original, keywords)

    return render_template(
        "index.html",
        summary=summary,
        ranked=ranked,
        original=original,
        keywords=keywords,
        all_sentences=all_sentences,
        highlighted_text=highlighted_text
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
from flask import Flask, render_template, request, send_file
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import os
from werkzeug.utils import secure_filename
import PyPDF2
import io
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------- PDF TEXT EXTRACTION --------
def extract_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

# -------- HIGHLIGHT FUNCTION --------
def highlight_text(text, keywords):
    for word in keywords:
        pattern = re.compile(rf'\b({word})\b', re.IGNORECASE)
        text = pattern.sub(r'<mark>\1</mark>', text)
    return text

# -------- KEYWORD EXTRACTION --------
def extract_keywords(text):
    vectorizer = TfidfVectorizer(stop_words='english', max_features=8)
    X = vectorizer.fit_transform([text])
    return list(vectorizer.get_feature_names_out())

# -------- NEW CORRECT SUMMARIZATION --------
def summarize_text(text, num_sentences=3, query=None):
    sentences = re.split(r'(?<=[.!?]) +', text)

    if len(sentences) <= num_sentences:
        return [], sentences, sentences

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)

    # 👉 NEW: sentence score = sum of TF-IDF weights
    scores = np.sum(tfidf_matrix.toarray(), axis=1)

    sentence_scores = [(sentences[i], float(scores[i])) for i in range(len(sentences))]

    ranked = sorted(sentence_scores, key=lambda x: x[1], reverse=True)

    selected = [sent for sent, score in ranked[:num_sentences]]

    return ranked, selected, sentences

# -------- DOWNLOAD ROUTE --------
@app.route("/download")
def download():
    summary_text = request.args.get("text", "")
    buffer = io.BytesIO()
    buffer.write(summary_text.encode())
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="summary.txt",
        mimetype="text/plain"
    )

# -------- MAIN ROUTE --------
@app.route("/", methods=["GET", "POST"])
def index():
    summary = []
    ranked = []
    original = ""
    keywords = []
    all_sentences = []
    highlighted_text = ""

    if request.method == "POST":

        original = request.form.get("text", "")
        file = request.files.get("file")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)

            if filename.endswith(".pdf"):
                original = extract_pdf(path)
            else:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    original = f.read()

        if original.strip():
            num = int(request.form.get("length", 3))
            ranked, summary, all_sentences = summarize_text(original, num)
            keywords = extract_keywords(original)
            highlighted_text = highlight_text(original, keywords)

    return render_template(
        "index.html",
        summary=summary,
        ranked=ranked,
        original=original,
        keywords=keywords,
        all_sentences=all_sentences,
        highlighted_text=highlighted_text
    )

if __name__ == "__main__":
    app.run(debug=True)

