package com.example.speechassessment.service;

import java.util.Map;

import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

@Service
public class WhisperSpeechToTextClient implements SpeechToTextClient {

    private final RestTemplate restTemplate = new RestTemplate();

    @Override
    public String transcribe(MultipartFile file, String languageHint) throws Exception {

    	String url = "http://localhost:5000/translate";

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("audio", new ByteArrayResource(file.getBytes()) {
            @Override
            public String getFilename() {
                return file.getOriginalFilename();
            }
        });

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        HttpEntity<MultiValueMap<String, Object>> request =
                new HttpEntity<>(body, headers);

        ResponseEntity<Map> response =
                restTemplate.postForEntity(url, request, Map.class);

        return response.getBody().get("original_text").toString();
    }

    @Override
    public String detectLanguage(String transcript) {
        return "auto";
    }
}