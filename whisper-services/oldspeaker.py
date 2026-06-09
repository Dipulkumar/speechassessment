from speechbrain.inference import EncoderClassifier
import torch
import torchaudio
import torch.nn.functional as F

classifier = EncoderClassifier.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="tmp_model"
)

speaker_db = []
resampler = torchaudio.transforms.Resample(orig_freq=48000, new_freq=16000)

def get_embedding(audio_path):
    signal, fs = torchaudio.load(audio_path)

    # Convert to mono if needed
    if signal.shape[0] > 1:
        signal = torch.mean(signal, dim=0, keepdim=True)

    if fs != 16000:
        signal = resampler(signal)
    # Ensure correct shape
    signal = signal.unsqueeze(0)

    with torch.no_grad():
        embedding = classifier.encode_batch(signal)

    # Normalize (IMPORTANT)
    embedding = F.normalize(embedding, p=2, dim=2)

    return embedding.squeeze(0)

def compare_embeddings(emb1, emb2):
    score = F.cosine_similarity(emb1, emb2)
    return score.item()

def identify_speaker(audio_path, threshold=0.65):
    new_emb = get_embedding(audio_path)

    if len(speaker_db) == 0:
        speaker_db.append(new_emb)
        return 0

    best_score = -1
    best_id = -1

    for i, emb in enumerate(speaker_db):
        score = compare_embeddings(emb, new_emb)

        if score > best_score:
            best_score = score
            best_id = i

    # Check threshold
    if best_score > threshold:
        return best_id
    else:
        speaker_db.append(new_emb)
        return len(speaker_db) - 1