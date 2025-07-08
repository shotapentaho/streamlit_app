from flask import Flask, request, jsonify
import openai
import requests
import toml
import os

# Load secrets from .streamlit/secrets.toml
secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
secrets = toml.load(secrets_path)

# OpenAI client instance (new SDK syntax)
openai_api_key = secrets["openai"]["api_key"]
openai_client = openai.OpenAI(api_key=openai_api_key)

gemini_api_key = secrets["gemini"]["api_key"]

app = Flask(__name__)

@app.route("/mcp", methods=["POST"])
def mcp():
    data = request.json
    prompt = data.get("prompt")
    provider = data.get("provider", "openai")  # Default to OpenAI
    model = data.get("model", "gpt-3.5-turbo")  # Default OpenAI model

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    try:
        if provider == "openai":
            response = openai_client.chat.completions.create(
                model = model,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content

        elif provider == "gemini":
            # Gemini API endpoint and payload
            #url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            resp = requests.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            answer = resp.json()["candidates"][0]["content"]["parts"][0]["text"]

        else:
            return jsonify({"error": "Invalid provider"}), 400

        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ MCP Flask server is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
