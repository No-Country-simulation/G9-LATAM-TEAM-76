package com.TechMind.Backend.controller;

import com.TechMind.Backend.dto.DocumentoResponse;
import com.TechMind.Backend.dto.TextoAnalisisRequest;
import com.TechMind.Backend.service.DocumentoService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/documentos")
public class DocumentoController {

    private final DocumentoService documentoService;

    public DocumentoController(DocumentoService documentoService) {
        this.documentoService = documentoService;
    }

    // Endpoint principal: Recibe texto del frontend, clasifica con FastAPI y guarda en DB
    @PostMapping("/clasificar")
    public ResponseEntity<DocumentoResponse> clasificarYGuardar(@RequestBody TextoAnalisisRequest request) {
        DocumentoResponse response = documentoService.procesarYGuardar(request);
        return ResponseEntity.ok(response);
    }

    // Endpoint para Dashboard: Obtener todos los registros guardados
    @GetMapping
    public ResponseEntity<List<DocumentoResponse>> obtenerTodos() {
        return ResponseEntity.ok(documentoService.obtenerTodos());
    }

    // Endpoint para Dashboard: Filtrar por categoría
    @GetMapping("/categoria/{categoria}")
    public ResponseEntity<List<DocumentoResponse>> obtenerPorCategoria(@PathVariable String categoria) {
        return ResponseEntity.ok(documentoService.obtenerPorCategoria(categoria));
    }
}