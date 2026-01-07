# tts/coqui_server.py
from flask import Flask, request, send_file
from TTS.api import TTS
import tempfile
import os

app = Flask(__name__)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.json['text']
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tts.tts_to_file(text=text, file_path=f.name)
        return send_file(f.name, mimetype="audio/wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)