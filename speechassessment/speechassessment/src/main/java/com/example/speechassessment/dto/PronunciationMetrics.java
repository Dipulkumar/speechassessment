package com.example.speechassessment.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder


public class PronunciationMetrics {
    private Double wordErrorRate;
    private Double pronunciationScore;
    private Double fluencyScore;
    private Double speakingRateWpm;
	
    

}
