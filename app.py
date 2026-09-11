from flask import Flask, render_template, request, jsonify
import re
import time

app = Flask(__name__)

recent_checks = []   


CLICKBAIT_PHRASES = [
    "you won't believe", "shocking truth", "they don't want you to know",
    "mainstream media won't tell", "wake up", "share before deleted",
    "doctors hate", "one weird trick", "secret they", "the truth about",
    "exposed!", "the real truth", "100% proof", "must watch", "going viral",
    "breaking!!!", "urgent!!!", "act now", "limited time", "share this now",
    "banned video", "censored", "they're hiding", "deep state",
    "false flag", "crisis actor", "new world order", "plandemic",
    "mind control", "chemtrails", "illuminati", "hoax exposed",
    "fake pandemic", "government lies", "media blackout",
]

CREDIBILITY_SIGNALS = [
    "according to", "researchers found", "study shows", "experts say",
    "officials confirmed", "spokesperson said", "published in", "data shows",
    "survey revealed", "statistics show", "per the report", "cited sources",
    "peer-reviewed", "official statement", "press release",
    "government announced", "university research",
]


def analyze_article(text: str) -> dict:
    """
    Analyse a news article with a suite of heuristic rules.
    Returns a dict with individual rule scores and an overall verdict.
    """
    score = 0          # positive = more fake-leaning; negative = more credible
    flags = []         # human-readable explanation of triggered rules
    details = []       # detailed breakdown

    stripped = text.strip()
    words = stripped.split()
    total_words = len(words)
    lower_text = stripped.lower()

    if total_words < 40:
        score += 25
        flags.append(f"Article is very short ({total_words} words) — lacks depth")
        details.append({"rule": "Short Article", "impact": "+25", "detail": f"{total_words} words"})
    elif total_words < 100:
        score += 10
        flags.append(f"Article is short ({total_words} words)")
        details.append({"rule": "Short Article", "impact": "+10", "detail": f"{total_words} words"})
    else:
        score -= 5
        details.append({"rule": "Article Length", "impact": "-5", "detail": f"{total_words} words — good length"})

    if total_words > 0:
        caps_words = [w for w in words if w.isupper() and len(w) > 2]
        caps_ratio = len(caps_words) / total_words
        if caps_ratio > 0.25:
            score += 30
            flags.append(f"Excessive ALL-CAPS usage ({len(caps_words)} words, {caps_ratio:.0%})")
            details.append({"rule": "ALL-CAPS Abuse", "impact": "+30", "detail": f"{caps_ratio:.0%} of words are CAPS"})
        elif caps_ratio > 0.10:
            score += 15
            flags.append(f"High ALL-CAPS usage ({caps_ratio:.0%} of words)")
            details.append({"rule": "ALL-CAPS Usage", "impact": "+15", "detail": f"{caps_ratio:.0%} of words are CAPS"})
        else:
            details.append({"rule": "ALL-CAPS Check", "impact": "0", "detail": "Normal capitalisation"})

    excl_count = stripped.count("!")
    if excl_count >= 5:
        score += 25
        flags.append(f"Excessive exclamation marks ({excl_count})")
        details.append({"rule": "Exclamation Marks", "impact": "+25", "detail": f"{excl_count} found"})
    elif excl_count >= 3:
        score += 12
        flags.append(f"Multiple exclamation marks ({excl_count})")
        details.append({"rule": "Exclamation Marks", "impact": "+12", "detail": f"{excl_count} found"})
    else:
        details.append({"rule": "Exclamation Marks", "impact": "0", "detail": f"{excl_count} found — normal"})

    q_count = stripped.count("?")
    if q_count >= 4:
        score += 15
        flags.append(f"Many rhetorical questions ({q_count})")
        details.append({"rule": "Question Marks", "impact": "+15", "detail": f"{q_count} found"})
    else:
        details.append({"rule": "Question Marks", "impact": "0", "detail": f"{q_count} found — normal"})

    matched_phrases = []
    for phrase in CLICKBAIT_PHRASES:
        if phrase in lower_text:
            matched_phrases.append(phrase)

    if len(matched_phrases) >= 3:
        score += 40
        flags.append(f"Multiple clickbait/conspiracy phrases detected: {', '.join(matched_phrases[:5])}")
        details.append({"rule": "Clickbait Phrases", "impact": "+40", "detail": f"{len(matched_phrases)} phrases found"})
    elif len(matched_phrases) >= 1:
        score += 20 * len(matched_phrases)
        flags.append(f"Clickbait phrase(s) found: {', '.join(matched_phrases)}")
        details.append({"rule": "Clickbait Phrases", "impact": f"+{20 * len(matched_phrases)}", "detail": f"{len(matched_phrases)} phrase(s)"})
    else:
        score -= 10
        details.append({"rule": "Clickbait Phrases", "impact": "-10", "detail": "No clickbait phrases detected"})

    matched_credibility = [p for p in CREDIBILITY_SIGNALS if p in lower_text]
    if len(matched_credibility) >= 3:
        score -= 25
        details.append({"rule": "Credibility Signals", "impact": "-25", "detail": f"{len(matched_credibility)} signals found"})
    elif len(matched_credibility) >= 1:
        score -= 10 * len(matched_credibility)
        details.append({"rule": "Credibility Signals", "impact": f"-{10 * len(matched_credibility)}", "detail": f"{len(matched_credibility)} signal(s)"})
    else:
        score += 10
        flags.append("No credible sourcing language found")
        details.append({"rule": "Credibility Signals", "impact": "+10", "detail": "None detected"})

    if total_words > 0:
        word_freq = {}
        for w in [w.lower().strip(".,!?;:\"'") for w in words]:
            if len(w) > 3:
                word_freq[w] = word_freq.get(w, 0) + 1

        spam_words = {w: c for w, c in word_freq.items() if c >= 5 and c / total_words > 0.05}
        if spam_words:
            score += 20
            top = sorted(spam_words.items(), key=lambda x: -x[1])[:3]
            flags.append(f"Word spam detected: {', '.join(f'{w}×{c}' for w, c in top)}")
            details.append({"rule": "Word Repetition", "impact": "+20", "detail": str(dict(top))})
        else:
            details.append({"rule": "Word Repetition", "impact": "0", "detail": "No suspicious repetition"})

    ellipsis_count = lower_text.count("...") + lower_text.count("…")
    if ellipsis_count >= 4:
        score += 10
        flags.append(f"Excessive ellipsis usage ({ellipsis_count})")
        details.append({"rule": "Ellipsis Abuse", "impact": "+10", "detail": f"{ellipsis_count} instances"})
    else:
        details.append({"rule": "Ellipsis", "impact": "0", "detail": "Normal"})

    superlatives = ["worst ever", "best ever", "most amazing", "totally destroyed",
                    "completely exposed", "absolutely shocking", "unbelievable truth",
                    "never seen before", "historic scandal"]
    found_sup = [s for s in superlatives if s in lower_text]
    if found_sup:
        score += 15 * len(found_sup)
        flags.append(f"Emotional superlatives: {', '.join(found_sup)}")
        details.append({"rule": "Superlatives", "impact": f"+{15 * len(found_sup)}", "detail": str(found_sup)})
    else:
        details.append({"rule": "Superlatives", "impact": "0", "detail": "None detected"})

    sentences = re.split(r'[.!?]', stripped)
    mid_sentence_caps = 0
    for sentence in sentences:
        sub_words = sentence.strip().split()
        if len(sub_words) > 1:
            mid_sentence_caps += sum(1 for w in sub_words[1:] if w and w[0].isupper() and len(w) > 2)

    if total_words > 50 and mid_sentence_caps < 2:
        score += 10
        flags.append("Very few proper nouns — lacks specific sources or names")
        details.append({"rule": "Named Entities", "impact": "+10", "detail": f"Only {mid_sentence_caps} mid-sentence capitals"})
    else:
        details.append({"rule": "Named Entities", "impact": "0", "detail": f"{mid_sentence_caps} proper nouns found"})

    score = max(0, min(score, 100))   # clamp to [0, 100]

    if score >= 55:
        verdict = "Likely Fake News"
        verdict_class = "fake"
        summary = ("This article exhibits multiple strong indicators of fake or misleading news, "
                   "including sensationalist language, conspiracy phrases, and/or poor sourcing.")
    elif score >= 25:
        verdict = "Suspicious News"
        verdict_class = "suspicious"
        summary = ("This article shows some warning signs. It may be exaggerated, biased, or "
                   "poorly sourced. Cross-check with trusted sources before sharing.")
    else:
        verdict = "Likely Real News"
        verdict_class = "real"
        summary = ("This article does not exhibit significant fake-news indicators. "
                   "It appears to use credible language and proper sourcing conventions.")

    return {
        "verdict": verdict,
        "verdict_class": verdict_class,
        "score": score,
        "summary": summary,
        "flags": flags,
        "details": details,
        "word_count": total_words,
    }



@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/check", methods=["POST"])
def check_news():
    """
    POST endpoint that accepts JSON { "article": "<text>" }
    and returns a JSON analysis result.
    """
    data = request.get_json(force=True)
    article_text = data.get("article", "").strip()

    if not article_text:
        return jsonify({"error": "No article text provided."}), 400
    if len(article_text) < 10:
        return jsonify({"error": "Article is too short to analyse."}), 400

    result = analyze_article(article_text)

    recent_checks.append({
        "snippet": article_text[:80] + ("…" if len(article_text) > 80 else ""),
        "verdict": result["verdict"],
        "score": result["score"],
        "timestamp": time.strftime("%H:%M:%S"),
    })
    if len(recent_checks) > 50:
        recent_checks.pop(0)

    return jsonify(result)


@app.route("/history")
def history():
    """Return the last few checked articles (in-memory only)."""
    return jsonify({"history": recent_checks[-10:][::-1]})


if __name__ == "__main__":
    print("\n🟢  Fake News Detector is running!")
    print("    Open http://127.0.0.1:5000 in your browser.\n")
    app.run(debug=True)