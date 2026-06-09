package com.example.speechassessment.service;

import com.sun.speech.freetts.Voice;
import com.sun.speech.freetts.VoiceManager;
import com.sun.speech.freetts.audio.SingleFileAudioPlayer;

import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

import javax.sound.sampled.AudioFileFormat;

@Service
public class TranslationService {

    private static final String TRANSLATE_URL = "https://libretranslate.de/translate";

    private final RestTemplate restTemplate = new RestTemplate();

    // 🌍 Translation
    public String translate(String text, String targetLang) {

        if (text == null || text.isBlank() || targetLang == null || "en".equals(targetLang)) {
            return text;
        }

        try {

            Map<String, Object> body = new HashMap<>();
            body.put("q", text);
            body.put("source", "auto");
            body.put("target", targetLang);
            body.put("format", "text");

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> entity =
                    new HttpEntity<>(body, headers);

            ResponseEntity<Map> response =
                    restTemplate.exchange(
                            TRANSLATE_URL,
                            HttpMethod.POST,
                            entity,
                            Map.class
                    );

            if (response.getBody() == null ||
                response.getBody().get("translatedText") == null) {
                return text;
            }

            return response.getBody().get("translatedText").toString();

        } catch (Exception e) {

            System.out.println("Translation error: " + e.getMessage());

            return text;

        }
    }

    // 🔊 Text → Speech
    public String generateSpeech(String text) {

        if (text == null || text.isBlank()) {
            return null;
        }

        try {

            // ✅ Register FreeTTS voice
            System.setProperty(
                    "freetts.voices",
                    "com.sun.speech.freetts.en.us.cmu_us_kal.KevinVoiceDirectory"
            );

            String folder = "src/main/resources/static/audio/";

            File dir = new File(folder);

            if (!dir.exists()) {
                dir.mkdirs();
            }

            String fileName = "tts_" + System.currentTimeMillis();

            String filePath = folder + fileName;

            VoiceManager vm = VoiceManager.getInstance();

            Voice voice = vm.getVoice("kevin16");

            if (voice == null) {
                System.out.println("Available voices:");

                for (Voice v : vm.getVoices()) {
                    System.out.println(v.getName());
                }

                throw new IllegalStateException("Voice not found");
            }

            SingleFileAudioPlayer audioPlayer =
                    new SingleFileAudioPlayer(
                            filePath,
                            AudioFileFormat.Type.WAVE
                    );

            voice.setAudioPlayer(audioPlayer);

            voice.allocate();

            voice.speak(text);

            voice.deallocate();

            audioPlayer.close();

            return "/audio/" + fileName + ".wav";

        } catch (Exception e) {

            System.out.println("TTS error: " + e.getMessage());

            return null;
        }
    }
}