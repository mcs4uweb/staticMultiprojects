# asr/whisper_server.py
from flask import Flask, request, jsonify
import whisper
import tempfile

app = Flask(__name__)
model = whisper.load_model("base")  # Use "tiny" for faster CPU

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio = request.files['audio']
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        audio.save(f.name)
        result = model.transcribe(f.name)
    return jsonify({"text": result["text"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)