package com.TechMind.Backend.dto;

public class TextoAnalisisRequest {
    private String titulo;
    private String texto;

    public TextoAnalisisRequest() {}

    public TextoAnalisisRequest(String titulo, String texto) {
        this.titulo = titulo;
        this.texto = texto;
    }

    public String getTitulo() {
        return titulo;
    }

    public void setTitulo(String titulo) {
        this.titulo = titulo;
    }

    public String getTexto() {
        return texto;
    }

    public void setTexto(String texto) {
        this.texto = texto;
    }
}