from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
import dotenv
import json

dotenv.load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    keyword = data.get("keyword", "").strip()
    type_ = data.get("type", "words")  # "words" or "phrases"

    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    if type_ == "phrases":
        prompt = f"""You are an English language expert.
Given the keyword "{keyword}", generate 6 famous, trending, and unique English phrases or idioms related to this topic.

Return ONLY a valid JSON array. Each object must have:
- "phrase": the phrase
- "meaning": simple explanation in 2-3 sentences
- "example": one example sentence using the phrase
- "category": one of: idiom, slang, formal, business, everyday, literary
- "trending": true or false

No markdown, no explanation. Only the JSON array."""

    else:
        prompt = f"""You are an English language expert.
Given the keyword "{keyword}", generate 6 famous, trending, and unique English words related to this topic.

Return ONLY a valid JSON array. Each object must have:
- "word": the word
- "pronunciation": phonetic pronunciation like /wɜːrd/
- "part_of_speech": noun, verb, adjective, etc.
- "meaning": simple explanation in 2-3 sentences
- "example": one example sentence using the word
- "synonyms": list of 3 synonyms
- "difficulty": beginner, intermediate, or advanced

No markdown, no explanation. Only the JSON array."""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )

        raw = completion.choices[0].message.content
        # Remove markdown fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return jsonify({"data": result})

    except json.JSONDecodeError:
        return jsonify({"error": "AI returned invalid response. Please try again."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)