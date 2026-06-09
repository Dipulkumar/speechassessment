import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

from speechbrain.inference import EncoderClassifier
import torch
import torchaudio
torchaudio.list_audio_backends = lambda: ["soundfile"]
import torch.nn.functional as F

device = "cpu"

classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="tmp_model",
    run_opts={"device": device},
    revision="main"
)


speaker_db = []
resamplers = {}

def update_speaker(id, speaker_data):
    for i, speaker in enumerate(speaker_db):
        if speaker.get("id") == id:
            if "name" in speaker_data and speaker_data["name"] is not None:
                speaker["name"] = speaker_data["name"]
            if "lang" in speaker_data and speaker_data["lang"] is not None:
                speaker["lang"] = speaker_data["lang"]
            if "emb" in speaker_data and speaker_data["emb"] is not None:
                speaker["emb"] = speaker_data["emb"]

def get_speaker(id):
    best_speaker = None
    for i, speaker in enumerate(speaker_db):
        if speaker.get("id") == id:
            best_speaker = speaker
    return  best_speaker

def get_resampler(orig_sr):
    if orig_sr not in resamplers:
        resamplers[orig_sr] = torchaudio.transforms.Resample(orig_sr, 16000)
    return resamplers[orig_sr]

def get_embedding(audio_path):
    signal, fs = torchaudio.load(audio_path)

    # Convert to mono
    if signal.shape[0] > 1:
        signal = signal.mean(dim=0, keepdim=True)

    if fs != 16000:
        signal = get_resampler(fs)(signal)

    signal = signal[:, :16000 * 3]

    with torch.inference_mode():
        emb = classifier.encode_batch(signal)

    # Normalize
    emb = F.normalize(emb, dim=2)

    return emb.squeeze()

def compare_embeddings(emb1, emb2):
    emb1 = F.normalize(emb1, dim=0)
    emb2 = F.normalize(emb2, dim=0)
    score = torch.dot(emb1, emb2).item()
    return score

def identify_speaker(audio_path, threshold=0.6):
    new_emb = get_embedding(audio_path)

    new_speaker = {
                "emb": new_emb,
                "name": "",
                "id": 0
            }
    if not speaker_db:
        new_speaker["id"] = 1
        speaker_db.append(new_speaker)
        return 1, ""

    best_score = -1
    best_speaker = None
    


    for i, speaker in enumerate(speaker_db):
        score = compare_embeddings(speaker.get("emb"), new_emb)

        if score > best_score:
            best_score = score
            best_speaker = speaker

    if best_score > threshold and best_speaker is not None:
        best_emb = (best_speaker.get("emb") + new_emb) / 2
        best_emb = F.normalize(best_emb, dim=0)
        best_speaker["emb"] = best_emb
        update_speaker(best_speaker.get("id"), best_speaker)

    elif len(speaker_db) < 2:
        new_speaker["id"] =  speaker_db[len(speaker_db) - 1].get("id") + 1
        speaker_db.append(new_speaker)
        best_speaker = new_speaker

    print("best_score:", best_score)
    
    return best_speaker.get("id"), best_speaker.get("name")

    