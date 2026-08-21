package com.TechMind.Backend.service;

import com.TechMind.Backend.dto.FastApiResponse;
import com.TechMind.Backend.dto.TextoAnalisisRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.net.URI;

@Service
public class FastApiService {

    private final RestClient restClient;

    @Value("${fastapi.url:${MODEL_API_URL:https://techmind-hackathon.duckdns.org/api/contenido}}")
    private String fastApiUrl;

    public FastApiService(RestClient restClient) {
        this.restClient = restClient;
    }

    public FastApiResponse clasificarTexto(TextoAnalisisRequest request) {
        return restClient.post()
                .uri(URI.create(fastApiUrl)) // <-- Se usa URI.create para forzar la URL absoluta
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(FastApiResponse.class);
    }
}