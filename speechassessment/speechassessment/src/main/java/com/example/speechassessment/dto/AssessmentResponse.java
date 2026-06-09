package com.example.speechassessment.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AssessmentResponse {

    private String transcript;
    private String language;
    private double durationSeconds;
    private PronunciationMetrics metrics;
    private String translatedText;
    private String translatedAudioUrl;

	
    
    
}



