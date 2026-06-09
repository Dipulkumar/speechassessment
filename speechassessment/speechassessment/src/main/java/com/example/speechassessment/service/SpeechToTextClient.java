package com.example.speechassessment.service;

import org.springframework.web.multipart.MultipartFile;

public interface SpeechToTextClient {

    String transcribe(MultipartFile file, String languageHint) throws Exception;

    default String detectLanguage(String transcript) {
        return "en";
    }
}
