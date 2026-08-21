package com.TechMind.Backend.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.TechMind.Backend.dto.*;
import com.TechMind.Backend.model.DocumentoProcesado;
import com.TechMind.Backend.repository.DocumentoRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DocumentoService {

    private final FastApiService fastApiService;
    private final DocumentoRepository repository;
    private final ObjectMapper objectMapper;

    public DocumentoService(FastApiService fastApiService, DocumentoRepository repository, ObjectMapper objectMapper) {
        this.fastApiService = fastApiService;
        this.repository = repository;
        this.objectMapper = objectMapper;
    }

    public DocumentoResponse procesarYGuardar(TextoAnalisisRequest request) {
        FastApiResponse iaResponse = fastApiService.clasificarTexto(request);

        String jsonResultado;
        try {
            jsonResultado = objectMapper.writeValueAsString(iaResponse);
        } catch (Exception e) {
            jsonResultado = "{}";
        }

        DocumentoProcesado doc = new DocumentoProcesado();
        doc.setTitulo(request.getTitulo());
        doc.setTextoOriginal(request.getTexto());

        String categoria = iaResponse.getCategoria();
        if (categoria == null || categoria.isEmpty()) {
            categoria = "Sin Clasificar";
        }
        doc.setCategoria(categoria);

        // Propagar la probabilidad devuelta por el modelo, si existe
        doc.setProbabilidad(iaResponse.getProbabilidad());

        doc.setDatosJson(jsonResultado);

        DocumentoProcesado guardado = repository.save(doc);

        return mapearARespuesta(guardado);
    }


    public List<DocumentoResponse> obtenerTodos() {
        return repository.findAll().stream()
                .map(this::mapearARespuesta)
                .toList();
    }

    public List<DocumentoResponse> obtenerPorCategoria(String categoria) {
        return repository.findByCategoriaIgnoreCase(categoria).stream()
                .map(this::mapearARespuesta)
                .toList();
    }

    private DocumentoResponse mapearARespuesta(DocumentoProcesado doc) {
        return new DocumentoResponse(
                doc.getId(),
                doc.getTitulo(), // <-- Mapeo hacia el DTO de respuesta
                doc.getTextoOriginal(),
                doc.getCategoria(),
                doc.getProbabilidad(),
                doc.getDatosJson(),
                doc.getFechaCreacion()
        );
    }
}