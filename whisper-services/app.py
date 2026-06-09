import os
os.environ["TORCHCODEC_DISABLE"] = "1"
os.environ["USE_TORCHCODEC"] = "0"

import torch
import torchaudio 
import soundfile as sf
from faster_whisper import WhisperModel
from transformers import VitsModel, AutoTokenizer, AutoModelForSeq2SeqLM
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import uuid 
from TTS.api import TTS
from vad import VADProcessor
from speaker import identify_speaker, update_speaker, get_speaker, speaker_db
import numpy as np
import subprocess
import mimetypes
import json
from extract_name import extract_name
from werkzeug.utils import secure_filename

torch.set_grad_enabled(False)
torch.set_num_threads(6)

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

vad = VADProcessor()
#STT model
whisper_model = WhisperModel("medium", device="cpu", compute_type="int8")

# Translation model
nllb_model_name = "facebook/nllb-200-distilled-600M"
trans_tokenizer = AutoTokenizer.from_pretrained(nllb_model_name)
trans_model = AutoModelForSeq2SeqLM.from_pretrained(nllb_model_name)
# trans_model = torch.compile(trans_model)

# TTS cache
tts_cache = {}

def get_tts(lang):
    lang =  NLLB_LANG_MAP.get(lang, "eng_Latn").split("_")[0]
    if lang not in tts_cache:
        tts_model_name = f"facebook/mms-tts-{lang}"
        tts_model = VitsModel.from_pretrained(tts_model_name)
        tts_tokenizer = AutoTokenizer.from_pretrained(tts_model_name)
        tts_model.eval()
        tts_cache[lang] = (tts_model, tts_tokenizer)

    return tts_cache[lang]

def get_audio_path(files):
    try:
        if "audio" not in files:
            raise ValueError("audio file missing.")
        audio = files["audio"]

        filename = secure_filename(audio.filename)
        input_path = os.path.join(UPLOAD_DIR, filename)
        audio.save(input_path)

        print("Uploaded file:", filename)
        print("MIME type:", audio.content_type)
        normalize_audio_path, file_name = normalize_audio(input_path)
        delete_file(input_path)

        return normalize_audio_path, file_name
    
    except Exception as e:
        print("get_audio_path error:", str(e))
        raise ValueError("error while processing audio speech file.")
    
def delete_file(file_path):
     if os.path.exists(file_path):
            os.remove(file_path)

def translate_text(text, source_lang, target_lang):
    try:
        src_lang =  NLLB_LANG_MAP.get(source_lang, "eng_Latn")
        tgt_lang =  NLLB_LANG_MAP.get(target_lang, "eng_Latn")

        trans_tokenizer.src_lang = src_lang

        inputs = trans_tokenizer(text, return_tensors="pt", padding=True)

        outputs = trans_model.generate(
            **inputs,
            forced_bos_token_id = trans_tokenizer.convert_tokens_to_ids(tgt_lang),
            max_length=512,
            num_beams=5
        )

        return trans_tokenizer.decode(outputs[0], skip_special_tokens=True)

    except Exception as e:
        print("Translation error:", str(e))

        return text

def transcribe_text(audio_path):
    segments, info = whisper_model.transcribe(
        audio_path,
        beam_size=5,
        best_of=5,
        temperature=0.0  
    )
    original_text = " ".join([seg.text for seg in segments])
    detected_lang = info.language
    print("Original:", original_text)
    print("Detected Language:", detected_lang)

    return original_text, detected_lang


def generate_audio(text, lang, file_name):
    model, tokenizer = get_tts(lang)
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        audio = model(**inputs)

    audio = audio.waveform.squeeze().cpu().numpy()

    # Normalize audio
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
        
    output_path = os.path.join(OUTPUT_DIR, file_name)
    sf.write(output_path, audio, 16000)

    return output_path

def normalize_audio(input_path):
    file_name = f"{uuid.uuid4()}.wav"
    output_path = os.path.join(UPLOAD_DIR, file_name)
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-sample_fmt", "s16",
        output_path
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            print(result.stderr.decode())
            raise ValueError("FFmpeg conversion failed")
        print("output_path:", output_path)
    except Exception as e:
        print("Ffmpeg error:", str(e))
        raise ValueError("failled to normalize ")

    
    return output_path, file_name

# -----------------------------
# API: Translate Audio
# -----------------------------
@app.route("/translate", methods=["POST"])
def translate_audio():
    try:
        #conversation_count = int(request.form.get("conversation_count", "2"))
        normalize_audio_path, file_name = get_audio_path(request.files)
        translated_text = ""
        output_filename = ""

        print("normalize_audio_path:", normalize_audio_path)
        try:
            waveform, sr = torchaudio.load(normalize_audio_path)
            print("Audio OK:", waveform.shape, sr)
        except Exception as e:
            print("Audio broken:", e)
            return {"error": "Invalid audio file"}, 400
        if not vad.has_speech(normalize_audio_path):
            print("No speech detected")
            raise ValueError("No speech detected.")
        
        speaker_id, speaker_name = identify_speaker(normalize_audio_path)
        print("Speaker ID:", speaker_id)
        
        #transcribe audio speech
        original_text, detected_lang = transcribe_text(normalize_audio_path)
        #listner_lang = ""
        # if conversation_count < 2 :
            # ALWAYS update speaker
        name = extract_name(original_text)
        update_speaker(speaker_id, {
            "name": name,
            "lang": detected_lang
        })

        listner_lang = None
            # name = extract_name(original_text)
            # speaker = {
            #     "name" : name, 
            #     "lang" : detected_lang
            # }
            # update_speaker(speaker_id, speaker)


            # print("speaker:", speaker)

        #else:
        conversation_users = json.loads(request.form.get("conversation_users", "[1,2]"))

        listener_id = None
        for uid in conversation_users:
                if uid != speaker_id:
                    listener_id = uid
                    break

        listener = get_speaker(listener_id)

        if listener and listener.get("lang"):
                    listner_lang = listener.get("lang")
        elif len(speaker_db) > 1:
                for sp in reversed(speaker_db):
                    if sp.get("id") != speaker_id and sp.get("lang"):
                        listner_lang = sp.get("lang")
                        break

            # fallback
        if not listner_lang:
            listner_lang = detected_lang

        print("Speaker ID:", speaker_id)
        print("Speaker Lang:", detected_lang)
        print("Listener Lang:", listner_lang)
        print("Original Text:", original_text)
        

        if listner_lang and listner_lang != detected_lang:
                translated_text = translate_text(original_text, detected_lang, listner_lang)
                output_filename = generate_audio(translated_text, listner_lang, file_name)
                print("Translated Text:", translated_text)
        else:
                translated_text = ""
                output_filename = ""


            # conversation_users = json.loads(request.form.get("conversation_users", "[0,0]"))
            # listener_id = [uid for uid in conversation_users if uid != speaker_id][0]
            # listner = get_speaker(listener_id)
            # print("listener_id:", listener_id)

            # if listner is not None:
            #     listner_lang = listner.get("lang")
            # else:
            #     listner_lang = detected_lang
            # translate transcribe text
            # """ if detected_lang == listner_lang:
            #     translated_text = original_text
            # else: """
            # translated_text = translate_text(original_text, detected_lang, listner_lang)
            # print("Detected:", detected_lang)
            # print("Listener:", listner_lang)
            # print("Translated:", translated_text)

            # # convert translated text to audio speech
            # output_filename = generate_audio(translated_text, listner_lang, file_name)
            # print("Translated audio file:", output_filename)
       
        # delete original audio speech file
        # delete_file(normalize_audio_path)

        response = {
            "original_text": original_text,
            "translated_text": translated_text,
            "speaker": speaker_name,
            "speaker_id": speaker_id,
            "original_audio_url": f"http://localhost:5000/audio/{UPLOAD_DIR}/{os.path.basename(normalize_audio_path)}",
            "translated_audio_url": ""
        }
        if output_filename:
            response["translated_audio_url"] = f"http://localhost:5000/audio/{OUTPUT_DIR}/{os.path.basename(output_filename)}"

        return jsonify(response)

    except Exception as e:
         print("Translation error:", str(e))
         return jsonify({"error": str(e)}), 500


# -----------------------------
# API: Get Audio
# -----------------------------
@app.route("/audio/<path:filename>")
def get_audio(filename):
    print("original filename:", filename)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # ✅ Normalize path safely
    path = os.path.normpath(os.path.join(BASE_DIR, filename))

    print("final path:", path)

    # 🔐 Security check (VERY IMPORTANT)
    if not path.startswith(BASE_DIR):
        return jsonify({"error": "Invalid path"}), 400

    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404

    mime_type, _ = mimetypes.guess_type(path)

    return send_file(path, mimetype=mime_type or "audio/wav")
# -----------------------------
# API: Reset speaker cache
# -----------------------------
# @app.route("/conversation/reset")
# def reset_conversation():
#     #code to reset converstation
#     speaker = ""

@app.route("/conversation/reset")
def reset_conversation():
    speaker_db.clear()
    return {"message": "conversation reset"}


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)