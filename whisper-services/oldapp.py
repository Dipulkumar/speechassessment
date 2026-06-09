from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
#import whisper
from faster_whisper import WhisperModel
import os
import uuid

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from TTS.api import TTS
import torch
from vad import VADProcessor
from speaker import identify_speaker

torch.set_num_threads(4) 

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Load Models
# -----------------------------
print("Loading Whisper model...")
#whisper_model = whisper.load_model("base")
vad = VADProcessor()
whisper_model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)
nllb_model_name = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(nllb_model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(nllb_model_name)
# model = torch.quantization.quantize_dynamic(
#     model, {torch.nn.Linear}, dtype=torch.qint8
# )
model = torch.compile(model)
# Optional GPU
# model = model.to("cuda")

print("Loading Multilingual TTS model...")
#tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/vits", gpu=False)

print("Server Ready!")

# -----------------------------
# Language Mapping (NLLB)
# -----------------------------
NLLB_LANG_MAP = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "bn": "ben_Beng",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "ml": "mal_Mlym",
    "kn": "kan_Knda",
    "mr": "mar_Deva",
    "gu": "guj_Gujr",
    "pa": "pan_Guru",
    "ur": "urd_Arab"
}

def get_nllb_lang(code):
    return NLLB_LANG_MAP.get(code, "eng_Latn")

# -----------------------------
# Translation Function
# -----------------------------
def translate_text(text, source_lang, target_lang):
    try:
        src_lang = get_nllb_lang(source_lang)
        tgt_lang = get_nllb_lang(target_lang)

        tokenizer.src_lang = src_lang

        inputs = tokenizer(text, return_tensors="pt", padding=True)

        outputs = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang),
            max_length=512,
            num_beams=3
        )
        
        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    except Exception as e:
        print("Translation error:", str(e))
        return text


# -----------------------------
# API: Translate Audio
# -----------------------------
@app.route("/translate", methods=["POST"])
def translate_audio():

    try:
        if "audio" not in request.files:
            return jsonify({"error": "Audio file missing"}), 400

        audio = request.files["audio"]
        target_lang = request.form.get("target_lang", "hi")

        file_id = str(uuid.uuid4())

        input_path = os.path.join(UPLOAD_DIR, file_id + ".wav")
        output_filename = file_id + ".wav"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        audio.save(input_path)

        # -----------------------------
        # Speech to Text (Whisper)
        # -----------------------------
        #result = whisper_model.transcribe(input_path)

        #original_text = result["text"]
        #detected_lang = result.get("language", "en")
        if not vad.has_speech(input_path):
            print("No speech detected")
            return

        segments, info = whisper_model.transcribe(input_path,  beam_size=3)

        original_text = " ".join([seg.text for seg in segments])
        detected_lang = info.language
        for segment in segments:
            print("segment: ", segment.text)
        print("Original:", original_text)
        print("Detected Language:", detected_lang)

        # -----------------------------
        # Translate
        # -----------------------------
        if detected_lang == target_lang:
            translated_text = original_text
        else:
            translated_text = translate_text(original_text, detected_lang, target_lang)

        print("Translated:", translated_text)

        # -----------------------------
        # Text to Speech (XTTS)
        # -----------------------------
        tts.tts_to_file(
            text=translated_text,
            file_path=output_path,
            language=target_lang
        )


        # -----------------------------
        # Cleanup input file
        # -----------------------------
        if os.path.exists(input_path):
            os.remove(input_path)

        # -----------------------------
        # Response
        # -----------------------------
        return jsonify({
            "original_text": original_text,
            "detected_language": detected_lang,
            "translated_text": translated_text,
            "target_language": target_lang,
            "audio_url": f"http://localhost:5000/audio/{output_filename}"
        })

    except Exception as e:
         print("Translation error:", str(e))
         return jsonify({"error": str(e)}), 500


# -----------------------------
# API: Get Audio
# -----------------------------
@app.route("/audio/<filename>")
def get_audio(filename):
    path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404

    return send_file(path, mimetype="audio/wav")


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)