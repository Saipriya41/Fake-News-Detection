# 📰 Fake News Detector (Rule-Based)

A rule-based fake news detection system built with Flask that analyzes news articles using predefined heuristics to provide transparent and explainable credibility assessments. Every prediction is generated from explicit rules, making the decision process easy to understand and verify.

---

## 📌 Overview

Fake News Detector is a lightweight web application that evaluates the credibility of a news article without using machine learning models. Instead, it analyzes the text using predefined rules such as clickbait phrases, excessive punctuation, ALL-CAPS usage, credibility indicators, and other linguistic patterns.

Based on these rules, the application classifies the article as **Likely Real**, **Suspicious**, or **Likely Fake**, while also showing the factors that contributed to the final decision.

---

## ✨ Features

- Rule-based fake news detection
- Credibility score with verdict
- Explanation of triggered rules
- Recent checks history (in-memory)
- Responsive web interface
- Live word counter and input validation

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Detection Engine:** Rule-Based Heuristics
- **Storage:** In-Memory Session History

---

## 📁 Project Structure

```text
fake_news_detector/
│
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   └── js/
└── README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/keerthiprathapagiri/fake_news_detector_rulebased.git
cd fake_news_detector_rulebased
```

Create a virtual environment (optional):

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

Install Flask:

```bash
pip install flask
```

Run the application:

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 🚀 Usage

1. Enter or paste a news article.
2. Click **Check News**.
3. View the credibility verdict and score.
4. Review the explanation for the detected rules.
5. See recently analyzed articles in the history section.

---

## 🔍 How It Works

```
User Input
     ↓
Flask Backend
     ↓
Rule-Based Analysis
     ↓
Score Calculation
     ↓
Credibility Verdict
     ↓
Result & Explanation
---

## 🚀 Future Improvements

- Store history in a database
- Expand the rule library
- Support multiple languages
- URL-based news analysis
- Optional machine learning mode

---

## 🤝 Contributing

Contributions are welcome. Feel free to fork the repository, make improvements, and submit a pull request.
