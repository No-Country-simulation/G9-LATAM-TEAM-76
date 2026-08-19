package com.javafx.techmindinterface;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.FlowPane;
import javafx.stage.Stage;

import java.io.IOException;
import java.util.List;

public class ResultadoController {

    @FXML private Label lblCategoria;
    @FXML private Label lblConfianza;
    @FXML private Label lblIdioma;
    @FXML private FlowPane containerPalabrasClave;
    @FXML private Button btnVolver;

    public void setDatosResultado(String categoria, double confianza, String idioma, List<String> palabrasClave) {
        lblCategoria.setText(categoria);
        lblConfianza.setText(String.format("%.2f%%", confianza));

        String idiomaTexto = switch (idioma.toLowerCase()) {
            case "es" -> "Español (ES)";
            case "en" -> "Inglés (EN)";
            case "pt" -> "Portugués (PT)";
            default -> idioma.toUpperCase();
        };
        lblIdioma.setText(idiomaTexto);

        containerPalabrasClave.getChildren().clear();
        if (palabrasClave == null || palabrasClave.isEmpty()) {
            Label noTags = new Label("No se encontraron palabras clave");
            noTags.setStyle("-fx-text-fill: #64748B; -fx-font-size: 13px;");
            containerPalabrasClave.getChildren().add(noTags);
        } else {
            for (String palabra : palabrasClave) {
                Label tag = new Label(palabra);
                tag.setStyle(
                        "-fx-background-color: #334155; " +
                                "-fx-text-fill: #38BDF8; " +
                                "-fx-padding: 6 12; " +
                                "-fx-background-radius: 16; " +
                                "-fx-font-size: 12px; " +
                                "-fx-font-weight: bold;"
                );
                containerPalabrasClave.getChildren().add(tag);
            }
        }
    }

    @FXML
    private void handleVolverAction(ActionEvent event) {
        try {
            // Regresa al Formulario
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/com/javafx/techmindinterface/Interfaces/FormularioAnalisisView.fxml"));
            Parent root = loader.load();

            Stage stage = (Stage) ((Node) event.getSource()).getScene().getWindow();
            stage.getScene().setRoot(root);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}