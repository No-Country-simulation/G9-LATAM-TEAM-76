package com.TechMind.Backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class FastApiResponse {

    private String categoria;
    private Double probabilidad;

    @JsonProperty("palabras_clave")
    private List<String> palabrasClave;

    public FastApiResponse() {}

    public String getCategoria() { return categoria; }
    public void setCategoria(String categoria) { this.categoria = categoria; }

    public Double getProbabilidad() { return probabilidad; }
    public void setProbabilidad(Double probabilidad) { this.probabilidad = probabilidad; }

    public List<String> getPalabrasClave() { return palabrasClave; }
    public void setPalabrasClave(List<String> palabrasClave) { this.palabrasClave = palabrasClave; }
}