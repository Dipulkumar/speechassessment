package com.example.speechassessment.controller;

import com.example.speechassessment.dto.AssessmentResponse;
import com.example.speechassessment.dto.PronunciationMetrics;
//import com.example.speechassessment.model.AssessmentResult;
//import com.example.speechassessment.repository.AssessmentResultRepository;
import com.example.speechassessment.service.PronunciationService;
import com.example.speechassessment.service.SpeechToTextClient;
import com.example.speechassessment.service.TranslationService;

import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/assessment")
//@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:8080")
public class AssessmentController {

    private final  SpeechToTextClient speechToTextClient;
    private final  PronunciationService pronunciationService;
    //private final  AssessmentResultRepository assessmentResultRepository;
    private final TranslationService translationService;


    @PostMapping(
            value = "/analyze",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public AssessmentResponse analyzeSpeech(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "expectedText", required = false) String expectedText,
            @RequestParam(value = "language", required = false) String language,
            @RequestParam(value = "targetLanguage", required = false) String targetLanguage,
            @RequestParam(value = "userId", required = false) String userId
    ) throws Exception {

        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Audio file is required");
        }

        // 1️⃣ Speech → Text
        String transcript = speechToTextClient.transcribe(file, language);

        // 2️⃣ Duration
        double durationSeconds = Math.max(file.getSize() / (16000.0 * 2), 1.0); // approx for PCM

        // 3️⃣ Pronunciation Metrics
        PronunciationMetrics metrics =
                pronunciationService.calculateMetrics(expectedText, transcript, durationSeconds);

        // 4️⃣ Detect Language
        String detectedLanguage = (language != null)
                ? language
                : speechToTextClient.detectLanguage(transcript);

        // 5️⃣ Translation
        String translatedText = null;
        String translatedAudioUrl = null;

        if (targetLanguage != null && !targetLanguage.equals(detectedLanguage)) {

            translatedText = translationService.translate(transcript, targetLanguage);

            translatedAudioUrl = translationService.generateSpeech(translatedText);

        }

		/*
		 * // 6️⃣ Save to DB AssessmentResult result = AssessmentResult.builder()
		 * .userId(userId != null ? userId : "anonymous") .language(detectedLanguage)
		 * .expectedText(expectedText) .recognizedText(transcript)
		 * .durationSeconds(durationSeconds) .wordErrorRate(metrics.getWordErrorRate())
		 * .pronunciationScore(metrics.getPronunciationScore())
		 * .fluencyScore(metrics.getFluencyScore())
		 * .speakingRateWpm(metrics.getSpeakingRateWpm())
		 * .createdAt(LocalDateTime.now()) .build();
		 * 
		 * assessmentResultRepository.save(result);
		 */

        // 7️⃣ Response
        return AssessmentResponse.builder()
                .transcript(transcript)
                .language(detectedLanguage)
                .durationSeconds(durationSeconds)
                .metrics(metrics)
                .translatedText(translatedText)
                .translatedAudioUrl(translatedAudioUrl)
                .build();
    }


	/*
	 * @GetMapping("/history/{userId}") public List<AssessmentResult>
	 * getHistory(@PathVariable String userId) { return
	 * assessmentResultRepository.findByUserIdOrderByCreatedAtDesc(userId); }
	 */
    
    
    
    // Manual Constructor
    public AssessmentController(
            SpeechToTextClient speechToTextClient,
            PronunciationService pronunciationService,
            TranslationService translationService
    ) {
        this.speechToTextClient = speechToTextClient;
        this.pronunciationService = pronunciationService;
        this.translationService = translationService;
    }
    
    
    
    
	    @PostMapping(
	            value = "/upload",
	            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
	    )
	    public ResponseEntity<String> uploadOnly(
	            @RequestParam("audio") MultipartFile audio,
	            @RequestParam(value = "language", required = false) String language
	    ) throws Exception {
	
	        if (audio == null || audio.isEmpty()) {
	            return ResponseEntity.badRequest().body("Audio file is required");
	        }
	
	        String transcript = speechToTextClient.transcribe(audio, language);
	        return ResponseEntity.ok(transcript);
	    }
    
    
    
}
