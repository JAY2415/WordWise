from flask import Flask, render_template, request, jsonify
import os
import json

try:
    from groq import Groq
except ImportError:
    Groq = None

app = Flask(__name__)


def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY is not set in environment variables")
    if Groq is None:
        raise Exception("groq package failed to import")
    return Groq(api_key=api_key, base_url="https://api.groq.com/openai/v1")


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
        client = get_client()
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
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
