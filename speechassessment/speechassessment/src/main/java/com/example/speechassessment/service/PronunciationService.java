package com.example.speechassessment.service;

import org.springframework.stereotype.Service;

import com.example.speechassessment.dto.PronunciationMetrics;

@Service
public class PronunciationService {

    public PronunciationMetrics calculateMetrics(
            String expectedText,
            String recognizedText,
            double durationSeconds
    ) {
        if (recognizedText == null) {
            recognizedText = "";
        }
        String recognizedClean = recognizedText.trim().toLowerCase();
        String expectedClean = expectedText != null ? expectedText.trim().toLowerCase() : null;

        // speaking rate (WPM)
        double wpm = 0.0;
        Double fluencyScore = null;
        if (durationSeconds > 0 && !recognizedClean.isEmpty()) {
            int wordCount = recognizedClean.split("\\s+").length;
            wpm = (wordCount / durationSeconds) * 60.0;
            fluencyScore = calculateFluencyScore(wpm);
        }

        // word error rate
        Double wer = null;
        Double pronunciationScore = null;
        if (expectedClean != null && !expectedClean.isEmpty()) {
            wer = computeWordErrorRate(expectedClean, recognizedClean);
            pronunciationScore = (1.0 - Math.min(wer, 1.0)) * 100.0;
        }

        return PronunciationMetrics.builder()
                .wordErrorRate(wer)
                .pronunciationScore(pronunciationScore)
                .fluencyScore(fluencyScore)
                .speakingRateWpm(wpm)
                .build();
                
    }

    private Double computeWordErrorRate(String reference, String hypothesis) {
        String[] refWords = reference.split("\\s+");
        String[] hypWords = hypothesis.split("\\s+");

        int editDistance = levenshteinDistance(refWords, hypWords);
        return (double) editDistance / (double) refWords.length;
    }

    private int levenshteinDistance(String[] s1, String[] s2) {
        int n = s1.length;
        int m = s2.length;
        int[][] dp = new int[n + 1][m + 1];

        for (int i = 0; i <= n; i++) dp[i][0] = i;
        for (int j = 0; j <= m; j++) dp[0][j] = j;

        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= m; j++) {
                int cost = s1[i - 1].equals(s2[j - 1]) ? 0 : 1;
                dp[i][j] = min(
                        dp[i - 1][j] + 1,
                        dp[i][j - 1] + 1,
                        dp[i - 1][j - 1] + cost
                );
            }
        }
        return dp[n][m];
    }

    private int min(int a, int b, int c) {
        return Math.min(a, Math.min(b, c));
    }

    private double calculateFluencyScore(double wpm) {
        if (wpm < 60) return 40.0;
        if (wpm <= 90) return 70.0;
        if (wpm <= 160) return 95.0;
        if (wpm <= 200) return 80.0;
        return 60.0;
    }
}
