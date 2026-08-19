package com.TechMind.Backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class FastApiResponse {

    private String idioma;

    @JsonProperty("palabras_clave")
    private List<String> palabrasClave;

    @JsonProperty("embedding_generado")
    private Boolean embeddingGenerado;

    public FastApiResponse() {}

    public String getIdioma() { return idioma; }
    public void setIdioma(String idioma) { this.idioma = idioma; }

    public List<String> getPalabrasClave() { return palabrasClave; }
    public void setPalabrasClave(List<String> palabrasClave) { this.palabrasClave = palabrasClave; }

    public Boolean getEmbeddingGenerado() { return embeddingGenerado; }
    public void setEmbeddingGenerado(Boolean embeddingGenerado) { this.embeddingGenerado = embeddingGenerado; }
}