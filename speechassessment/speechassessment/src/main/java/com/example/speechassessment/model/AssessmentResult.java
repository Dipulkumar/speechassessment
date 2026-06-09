package com.example.speechassessment.model;

import lombok.*;
import lombok.experimental.SuperBuilder;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@SuperBuilder
public class AssessmentResult {

    private Long id;

    private String userId;
    private String language;
    private String expectedText;

    private String recognizedText;

    private double durationSeconds;

    private Double wordErrorRate;
    private Double pronunciationScore;
    private Double fluencyScore;
    private Double speakingRateWpm;

    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}