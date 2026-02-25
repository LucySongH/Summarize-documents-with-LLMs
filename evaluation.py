import re

def check_starts_on_topic(summary: str) -> bool:
    """
    Pascal's feedback: summary must start by stating what the document is.
    Checks if the first sentence contains topic-identifying phrases.
    """
    if not summary:
        return False
    first_sentence = summary.strip().split(".")[0].lower()
    topic_phrases = [
        "this document",
        "this report",
        "this policy",
        "this guide",
        "this manual",
        "this letter",
        "this correspondence",
        "this financial",
        "this is a",
        "this is an",
    ]
    return any(phrase in first_sentence for phrase in topic_phrases)


def flesch_reading_ease(text: str) -> float:
    """
    Calculate Flesch Reading Ease score without external libraries.
    Score interpretation:
      90-100 : Very easy (5th grade)
      60-70  : Standard (8th-9th grade)
      30-50  : Difficult (college level)
      0-30   : Very difficult (professional)
    """
    if not text or not text.strip():
        return 0.0

    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = max(len(sentences), 1)

    # Count words
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    num_words = max(len(words), 1)

    # Count syllables (simplified)
    def count_syllables(word: str) -> int:
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        # Silent 'e' at end
        if word.endswith('e') and count > 1:
            count -= 1
        return max(count, 1)

    num_syllables = sum(count_syllables(w) for w in words)

    # Flesch formula
    score = (
        206.835 # Benchmark
        - 1.015 * (num_words / num_sentences) # Deduct points equal to the average sentence length.
        - 84.6 * (num_syllables / num_words) # Deduct points equal to the average number of syllables per word.
    )
    return round(max(0.0, min(100.0, score)), 1)


def evaluate_summary(summary: str, time_taken: float) -> dict:
    if not summary:
        return {
            "starts_on_topic": False,
            "word_count": 0,
            "time_taken": time_taken,
            "readability": 0.0,
            "readability_label": "N/A",
        }

    readability = flesch_reading_ease(summary)

    if readability >= 70:
        readability_label = "Easy"
    elif readability >= 50:
        readability_label = "Medium"
    elif readability >= 30:
        readability_label = "Difficult"
    else:
        readability_label = "Very Difficult"

    return {
        "starts_on_topic": check_starts_on_topic(summary),
        "word_count": len(summary.split()),
        "time_taken": round(time_taken, 2),
        "readability": readability,
        "readability_label": readability_label,
    }
