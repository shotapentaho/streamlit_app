import sys
import json
from llama_cpp import Llama

llm = Llama(model_path="llama-2-7b-chat.Q4_K_M.gguf", n_ctx=2048)

def read_message():
    length_bytes = sys.stdin.buffer.read(4)
    if not length_bytes:
        return None
    length = int.from_bytes(length_bytes, byteorder="little")
    data = sys.stdin.buffer.read(length)
    return json.loads(data)

def write_message(message):
    encoded = json.dumps(message).encode("utf-8")
    sys.stdout.buffer.write(len(encoded).to_bytes(4, byteorder="little"))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()

while True:
    request = read_message()
    if request is None:
        break

    if request.get("type") == "request":
        prompt = request["body"]["text"]

        try:
            response = llm(prompt, max_tokens=256, stop=["</s>"])
            result = response["choices"][0]["text"].strip()

            write_message({
                "type": "response",
                "id": request["id"],
                "body": {"text": result}
            })

        except Exception as e:
            write_message({
                "type": "error",
                "id": request["id"],
                "body": {"error": str(e)}
            })
