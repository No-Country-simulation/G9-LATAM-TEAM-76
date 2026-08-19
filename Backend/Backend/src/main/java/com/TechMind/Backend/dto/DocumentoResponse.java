package com.TechMind.Backend.dto;

import java.time.LocalDateTime;

public class DocumentoResponse {
    private String id;
    private String titulo;
    private String textoOriginal;
    private String categoria;
    private String datosJson;
    private LocalDateTime fechaCreacion;

    public DocumentoResponse() {}

    public DocumentoResponse(String id, String titulo, String textoOriginal, String categoria, String datosJson, LocalDateTime fechaCreacion) {
        this.id = id;
        this.titulo = titulo;
        this.textoOriginal = textoOriginal;
        this.categoria = categoria;
        this.datosJson = datosJson;
        this.fechaCreacion = fechaCreacion;
    }

    public String getTitulo() {
        return titulo;
    }

    public void setTitulo(String titulo) {
        this.titulo = titulo;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTextoOriginal() {
        return textoOriginal;
    }

    public void setTextoOriginal(String textoOriginal) {
        this.textoOriginal = textoOriginal;
    }

    public String getCategoria() {
        return categoria;
    }

    public void setCategoria(String categoria) {
        this.categoria = categoria;
    }

    public String getDatosJson() {
        return datosJson;
    }

    public void setDatosJson(String datosJson) {
        this.datosJson = datosJson;
    }

    public LocalDateTime getFechaCreacion() {
        return fechaCreacion;
    }

    public void setFechaCreacion(LocalDateTime fechaCreacion) {
        this.fechaCreacion = fechaCreacion;
    }
}