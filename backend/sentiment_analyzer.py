import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Load model once at module level (for speed)
tokenizer = AutoTokenizer.from_pretrained("MarieAngeA13/Sentiment-Analysis-BERT")
model = AutoModelForSequenceClassification.from_pretrained("MarieAngeA13/Sentiment-Analysis-BERT")

# Map your labels to emotional tones for Ren
tone_map = {
    "positive": "warm",
    "neutral": "calm",
    "negative": "serious",
    "anger": "firm",
    "joy": "light",
    "sadness": "low",
    "surprise": "sharp",
    "fear": "tense"
}

def analyze_tone(text: str) -> dict:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.softmax(outputs.logits, dim=1)
    confidence, predicted_class = torch.max(probs, dim=1)

    raw_label = model.config.id2label[predicted_class.item()].lower()
    tone = tone_map.get(raw_label, "neutral")

    return {
        "raw_label": raw_label,
        "tone": tone,
        "confidence": round(confidence.item(), 3)
    }