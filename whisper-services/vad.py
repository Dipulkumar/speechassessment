import webrtcvad
import numpy as np
import torchaudio
torchaudio.list_audio_backends = lambda: ["soundfile"]

class VADProcessor:
    def __init__(self, aggressiveness=2):
        self.vad = webrtcvad.Vad(aggressiveness)

    def load_audio(self, path):
        print("calling surch audio load")
        signal, fs = torchaudio.load(path)

        # Convert to mono
        if signal.shape[0] > 1:
            signal = signal.mean(dim=0, keepdim=True)

        print("call to load audio to end")
        return signal, fs

    def is_speech(self, signal, fs):
        print("call to is_speech start")
        audio_np = signal.squeeze().numpy()

        # Convert to 16-bit PCM
        pcm = (audio_np * 32768).astype(np.int16)
        is_speech_valid = self.vad.is_speech(pcm.tobytes(), fs)
        print("is_speech call end")
        return is_speech_valid

    def has_speech(self, audio_path):
        signal, fs = self.load_audio(audio_path)
        audio = signal.squeeze().numpy()

        pcm = (audio * 32768).astype(np.int16)

        frame_duration = 30  # ms
        frame_size = int(fs * frame_duration / 1000)

        for i in range(0, len(pcm), frame_size):
            frame = pcm[i:i+frame_size]
            if len(frame) < frame_size:
                continue
            if self.vad.is_speech(frame.tobytes(), fs):
                return True

        return False