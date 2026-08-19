package com.javafx.techmindinterface;

public class DocumentoModel {
    private String id;
    private String titulo;
    private String categoria;
    private String fechaCreacion;
    private String textoOriginal;
    private String datosJson;

    public DocumentoModel(String id, String titulo, String categoria, String fechaCreacion, String textoOriginal, String datosJson) {
        this.id = id;
        this.titulo = titulo;
        this.categoria = categoria;
        this.fechaCreacion = fechaCreacion;
        this.textoOriginal = textoOriginal;
        this.datosJson = datosJson;
    }

    public String getId() { return id; }
    public String getTitulo() { return titulo; }
    public String getCategoria() { return categoria; }
    public String getFechaCreacion() { return fechaCreacion; }
    public String getTextoOriginal() { return textoOriginal; }
    public String getDatosJson() { return datosJson; }
}