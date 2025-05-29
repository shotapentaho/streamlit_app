from flask import Flask, request, jsonify
import openai
import os
import streamlit as st


openai.api_key = st.secrets["openai"]["api_key"]

app = Flask(__name__)

@app.route("/mcp", methods=["POST"])
def mcp():
    data = request.json
    prompt = data.get("prompt")
    print("Received prompt:", prompt)

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["choices"][0]["message"]["content"]
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
