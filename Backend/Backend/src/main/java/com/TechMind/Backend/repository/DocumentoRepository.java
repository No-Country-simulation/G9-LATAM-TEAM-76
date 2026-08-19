package com.TechMind.Backend.repository;

import com.TechMind.Backend.model.DocumentoProcesado;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DocumentoRepository extends JpaRepository<DocumentoProcesado, String> {
    List<DocumentoProcesado> findByCategoriaIgnoreCase(String categoria);
}