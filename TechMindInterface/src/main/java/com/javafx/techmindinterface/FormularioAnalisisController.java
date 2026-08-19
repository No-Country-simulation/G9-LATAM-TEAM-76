package com.javafx.techmindinterface;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.layout.StackPane;
import javafx.stage.Stage;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;

public class FormularioAnalisisController {

    @FXML private StackPane mainContainer;
    @FXML private TextField txtTitulo;
    @FXML private TextArea txtTexto;
    @FXML private Button btnAnalizar;

    private Node loadingOverlay;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @FXML
    public void handleAnalizarAction(ActionEvent event) {
        String titulo = txtTitulo.getText().trim();
        String texto = txtTexto.getText().trim();

        if (titulo.isEmpty() || texto.isEmpty()) {
            mostrarAlerta(
                    Alert.AlertType.WARNING,
                    "Campos Incompletos",
                    "Por favor llena tanto el título como el texto antes de clasificar."
            );
            return;
        }

        mostrarPantallaCarga();

        String jsonPayload = String.format("{\"titulo\": \"%s\", \"texto\": \"%s\"}",
                escapeJson(titulo),
                escapeJson(texto));

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:8081/api/documentos/clasificar"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenAccept(response -> Platform.runLater(() -> {
                    ocultarPantallaCarga();

                    if (response.statusCode() == 200 || response.statusCode() == 201) {
                        try {
                            JsonNode rootJson = objectMapper.readTree(response.body());

                            String categoria = rootJson.path("categoria").asText("Sin Categoría");

                            double confianza = 0.0;
                            if (rootJson.has("confianza")) {
                                confianza = rootJson.get("confianza").asDouble();
                            } else if (rootJson.has("score")) {
                                confianza = rootJson.get("score").asDouble();
                            } else {
                                confianza = 95.0;
                            }

                            if (confianza > 0.0 && confianza <= 1.0) {
                                confianza = confianza * 100.0;
                            }

                            String idioma = "es";
                            List<String> palabrasClave = new ArrayList<>();

                            if (rootJson.has("datosJson") && !rootJson.get("datosJson").isNull()) {
                                String datosJsonStr = rootJson.get("datosJson").asText();
                                JsonNode datosInner = objectMapper.readTree(datosJsonStr);

                                if (datosInner.has("idioma")) {
                                    idioma = datosInner.get("idioma").asText();
                                }

                                if (datosInner.has("palabras_clave") && datosInner.get("palabras_clave").isArray()) {
                                    for (JsonNode tag : datosInner.get("palabras_clave")) {
                                        palabrasClave.add(tag.asText());
                                    }
                                }
                            }

                            mostrarVistaResultado(categoria, confianza, idioma, palabrasClave);

                        } catch (Exception e) {
                            e.printStackTrace();
                            mostrarAlerta(Alert.AlertType.ERROR, "Error de Procesamiento", "No se pudo procesar la respuesta.");
                        }
                    } else {
                        mostrarAlerta(Alert.AlertType.ERROR, "Error del Servidor", "Código: " + response.statusCode());
                    }
                }))
                .exceptionally(ex -> {
                    Platform.runLater(() -> {
                        ocultarPantallaCarga();
                        mostrarAlerta(Alert.AlertType.ERROR, "Error de Conexión", "No se pudo conectar con el servicio backend.");
                    });
                    ex.printStackTrace();
                    return null;
                });
    }

    private void mostrarVistaResultado(String categoria, double confianza, String idioma, List<String> palabrasClave) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/com/javafx/techmindinterface/Interfaces/ResultadoView.fxml"));
            Parent root = loader.load();

            ResultadoController controller = loader.getController();
            controller.setDatosResultado(categoria, confianza, idioma, palabrasClave);

            Stage stage = (Stage) mainContainer.getScene().getWindow();
            stage.getScene().setRoot(root);

        } catch (IOException e) {
            e.printStackTrace();
            mostrarAlerta(Alert.AlertType.ERROR, "Error de Interfaz", "No se pudo cargar la vista de resultados.");
        }
    }

    private void mostrarPantallaCarga() {
        btnAnalizar.setDisable(true);
        try {
            if (loadingOverlay == null) {
                loadingOverlay = FXMLLoader.load(getClass().getResource("/com/javafx/techmindinterface/Interfaces/LoadingView.fxml"));
            }

            if (mainContainer != null && !mainContainer.getChildren().contains(loadingOverlay)) {
                mainContainer.getChildren().add(loadingOverlay);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void ocultarPantallaCarga() {
        btnAnalizar.setDisable(false);
        if (mainContainer != null && loadingOverlay != null) {
            mainContainer.getChildren().remove(loadingOverlay);
        }
    }

    private String escapeJson(String input) {
        return input.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r");
    }

    private void mostrarAlerta(Alert.AlertType tipo, String titulo, String mensaje) {
        Alert alert = new Alert(tipo);
        alert.setTitle(titulo);
        alert.setHeaderText(null);
        alert.setContentText(mensaje);
        alert.showAndWait();
    }

    @FXML
    private void handleVerHistorial(ActionEvent event) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/com/javafx/techmindinterface/Interfaces/HistorialView.fxml"));
            Parent root = loader.load();

            Stage stage = (Stage) mainContainer.getScene().getWindow();
            stage.getScene().setRoot(root);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}