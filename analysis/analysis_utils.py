# analysis/utils.py
import re
import statistics
from datetime import datetime

# Simple lexicons for heuristic analysis
POSITIVE_WORDS = {"thanks", "thank", "great", "good", "happy", "awesome", "resolved", "ok", "okay"}
NEGATIVE_WORDS = {"not", "problem", "issue", "unhappy", "angry", "bad", "delay", "late", "wrong"}
EMPATHY_WORDS = {"sorry", "apologize", "understand", "feel", "sympath"}
FALLBACK_PHRASES = ["i don't know", "i'm not sure", "can't help", "cannot help", "sorry, i don't", "unable to"]

# ------------------ Utility helpers ------------------ #
def tokenize(text):
    return re.findall(r"\w+", text.lower())

def sentence_count(text):
    return max(1, len(re.split(r'[.!?]+', text.strip())))

def compute_clarity_score(text):
    tokens = tokenize(text)
    if not tokens:
        return 0.0
    avg_word_len = sum(len(t) for t in tokens) / len(tokens)
    avg_sentence_len = len(tokens) / sentence_count(text)
    sent_factor = max(0, 1 - (abs(avg_sentence_len - 12) / 20))
    word_factor = max(0, 1 - (abs(avg_word_len - 5) / 6))
    return round((sent_factor * 0.7 + word_factor * 0.3), 3)

def compute_relevance_score(ai_msg, user_msg):
    ai_tokens = set(tokenize(ai_msg))
    user_tokens = set(tokenize(user_msg))
    if not ai_tokens or not user_tokens:
        return 0.0
    overlap = ai_tokens.intersection(user_tokens)
    return round(len(overlap) / len(user_tokens), 3)

def compute_empathy_score(text):
    return round(min(1.0, sum(1 for w in EMPATHY_WORDS if w in text.lower()) * 0.5), 3)

def detect_fallbacks(text):
    return sum(1 for phrase in FALLBACK_PHRASES if phrase in text.lower())

def sentiment_of_user(user_msgs):
    pos = neg = 0
    for m in user_msgs:
        tokens = set(tokenize(m))
        pos += len(tokens & POSITIVE_WORDS)
        neg += len(tokens & NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return {"label": "neutral", "score": 0.5}
    score = (pos - neg) / total
    mapped = round((score + 1) / 2, 3)
    if mapped > 0.66:
        label = "positive"
    elif mapped < 0.34:
        label = "negative"
    else:
        label = "neutral"
    return {"label": label, "score": mapped}

def detect_resolution(messages):
    ai_texts = " ".join(m["message"].lower() for m in messages if m["sender"] == "ai")
    user_texts = " ".join(m["message"].lower() for m in messages if m["sender"] == "user")
    for p in ["shipped", "delivered", "resolved", "completed", "done", "cancelled"]:
        if p in ai_texts and not any(n in user_texts for n in NEGATIVE_WORDS):
            return True
    return False

def compute_accuracy_score(ai_msg):
    hedges = ["think", "maybe", "probably", "might", "could be", "not sure"]
    t = ai_msg.lower()
    if any(h in t for h in hedges):
        return 0.4
    return 0.6 if any(ch.isdigit() for ch in ai_msg) else 0.5

def average_response_times(mock_seconds_per_pair=20, user_to_ai_ratio=0.4):
    return {
        "avg_user_response_seconds": round(mock_seconds_per_pair * user_to_ai_ratio, 1),
        "avg_ai_response_seconds": round(mock_seconds_per_pair * (1 - user_to_ai_ratio), 1)
    }

# ------------------ Main Analyzer ------------------ #
def analyze_conversation(messages):
    user_msgs = [m["message"] for m in messages if m["sender"] == "user"]
    ai_msgs = [m["message"] for m in messages if m["sender"] == "ai"]

    # --- Compute clarity ---
    clarity = [compute_clarity_score(m) for m in ai_msgs]
    clarity = clarity or [0.0]

    # --- Compute relevance ---
    relevance = []
    for i, m in enumerate(messages):
        if m["sender"] == "ai":
            for j in range(i-1, -1, -1):
                if messages[j]["sender"] == "user":
                    relevance.append(compute_relevance_score(m["message"], messages[j]["message"]))
                    break
    relevance = relevance or [0.0]

    # --- Compute empathy ---
    empathy = [compute_empathy_score(m) for m in ai_msgs] or [0.0]

    # --- Fallbacks ---
    fallback_count = sum(detect_fallbacks(m) for m in ai_msgs)

    # --- Sentiment & resolution ---
    sentiment = sentiment_of_user(user_msgs) if user_msgs else {"label": "neutral", "score": 0.5}
    resolution = detect_resolution(messages)
    escalation_needed = not resolution and sentiment["label"] == "negative"

    # --- Accuracy ---
    accuracy = [compute_accuracy_score(m) for m in ai_msgs] or [0.0]

    # --- Completeness ---
    completeness = 0.0
    for m in ai_msgs:
        t = m.lower()
        if ("please" in t and "share" in t) or "can you" in t or "could you" in t:
            completeness += 0.6
        if any(word in t for word in ["shipped", "will arrive", "delivered", "tracking"]):
            completeness += 1.0
    completeness = round(min(1.0, completeness / max(1, len(ai_msgs))), 3)

    # --- Average response times ---
    times = average_response_times() if callable(average_response_times) else {"avg_user_response_seconds": 0.0, "avg_ai_response_seconds": 0.0}

    # --- Prepare final data dict ---
    data = {
        "clarity_score": round(statistics.mean(clarity), 3),
        "relevance_score": round(statistics.mean(relevance), 3),
        "accuracy_score": round(statistics.mean(accuracy), 3),
        "completeness_score": completeness,
        "empathy_score": round(statistics.mean(empathy), 3),
        "fallback_count": fallback_count,
        "sentiment": sentiment.get("label", "neutral"),
        "sentiment_score": sentiment.get("score", 0.5),
        "resolution": bool(resolution),
        "escalation_needed": bool(escalation_needed),
        "avg_user_response_seconds": times.get("avg_user_response_seconds", 0.0),
        "avg_ai_response_seconds": times.get("avg_ai_response_seconds", 0.0),
        "overall_score": 0.0,  # placeholder, will compute next
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    # --- Overall score (weighted sum) ---
    weights = {
        "clarity_score": 0.18,
        "relevance_score": 0.18,
        "accuracy_score": 0.14,
        "completeness_score": 0.16,
        "empathy_score": 0.12,
        "sentiment_score": 0.12,
        "resolution": 0.1,
    }
    overall = sum(data[k] * w for k, w in weights.items() if k in data)
    data["overall_score"] = round(overall, 3)

    return data