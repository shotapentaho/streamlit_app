from flask import Flask, request, jsonify
import openai
import toml

# Load OpenAI API key from .streamlit/secrets.toml
secrets = toml.load(".streamlit/secrets.toml")

# Create OpenAI client instance (new SDK syntax)
client = openai.OpenAI(api_key=secrets["openai"]["api_key"])

app = Flask(__name__)

@app.route("/mcp", methods=["POST"])
def mcp():
    data = request.json
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ MCP Flask server is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

