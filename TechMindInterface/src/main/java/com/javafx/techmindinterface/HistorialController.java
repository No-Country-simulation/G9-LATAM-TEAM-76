package com.javafx.techmindinterface;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.stage.Stage;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class HistorialController {

    @FXML private TableView<DocumentoModel> tablaDocumentos;
    @FXML private TableColumn<DocumentoModel, String> colTitulo;
    @FXML private TableColumn<DocumentoModel, String> colCategoria;
    @FXML private TableColumn<DocumentoModel, String> colFecha;
    @FXML private TableColumn<DocumentoModel, Void> colAccion;
    @FXML private ComboBox<String> cmbFiltroCategoria;

    private final List<DocumentoModel> listaMaestraDocumentos = new ArrayList<>();
    private final ObservableList<DocumentoModel> listaFiltrada = FXCollections.observableArrayList();
    private final ObjectMapper objectMapper = new ObjectMapper();

    @FXML
    public void initialize() {
        colTitulo.setCellValueFactory(new PropertyValueFactory<>("titulo"));
        colCategoria.setCellValueFactory(new PropertyValueFactory<>("categoria"));
        colFecha.setCellValueFactory(new PropertyValueFactory<>("fechaCreacion"));

        tablaDocumentos.getStylesheets().add(
                "data:text/css," +
                        ".table-view .column-header-background { -fx-background-color: #0F172A; }" +
                        ".table-view .column-header, .table-view .filler { -fx-background-color: #0F172A; -fx-border-color: #334155; }" +
                        ".table-view .column-header .label { -fx-text-fill: #38BDF8; -fx-font-weight: bold; -fx-alignment: CENTER-LEFT; }" +
                        ".table-view .corner { -fx-background-color: #0F172A; }"
        );

        aplicarEstiloTablaDark();
        configurarBotonDetalle();

        cargarDocumentos();
    }

    @FXML
    public void cargarDocumentos() {
        obtenerDocumentosDeBackend("http://localhost:8081/api/documentos");
    }

    @FXML
    private void handleFiltrar() {
        String seleccion = cmbFiltroCategoria.getValue();

        if (seleccion == null || seleccion.equals("Todas")) {
            listaFiltrada.setAll(listaMaestraDocumentos);
        } else {
            // Filtrado local en memoria
            List<DocumentoModel> filtrados = listaMaestraDocumentos.stream()
                    .filter(doc -> doc.getCategoria() != null && doc.getCategoria().equalsIgnoreCase(seleccion))
                    .collect(Collectors.toList());
            listaFiltrada.setAll(filtrados);
        }
    }

    private void obtenerDocumentosDeBackend(String urlStr) {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(urlStr))
                .GET()
                .build();

        client.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenAccept(response -> Platform.runLater(() -> {
                    if (response.statusCode() == 200) {
                        try {
                            listaMaestraDocumentos.clear();
                            JsonNode rootArray = objectMapper.readTree(response.body());

                            Set<String> categoriasExistentes = new HashSet<>();

                            for (JsonNode node : rootArray) {
                                String id = node.path("id").asText("");
                                String titulo = node.path("titulo").asText("Sin Título");
                                String categoria = node.path("categoria").asText("Uncategorized");
                                String fecha = node.path("fechaCreacion").asText("-").replace("T", " ");
                                String textoOriginal = node.path("textoOriginal").asText("");
                                String datosJson = node.path("datosJson").asText("{}");

                                if (fecha.length() > 16) {
                                    fecha = fecha.substring(0, 16);
                                }

                                listaMaestraDocumentos.add(new DocumentoModel(id, titulo, categoria, fecha, textoOriginal, datosJson));
                                if (!categoria.isBlank()) {
                                    categoriasExistentes.add(categoria);
                                }
                            }

                            poblarComboCategorias(categoriasExistentes);
                            listaFiltrada.setAll(listaMaestraDocumentos);
                            tablaDocumentos.setItems(listaFiltrada);

                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                }))
                .exceptionally(ex -> {
                    ex.printStackTrace();
                    return null;
                });
    }

    private void poblarComboCategorias(Set<String> categorias) {
        cmbFiltroCategoria.getItems().clear();
        cmbFiltroCategoria.getItems().add("Todas");
        cmbFiltroCategoria.getItems().addAll(categorias);
        cmbFiltroCategoria.getSelectionModel().selectFirst();
    }

    private void aplicarEstiloTablaDark() {
        colTitulo.setCellFactory(column -> crearCeldaEstilizada());
        colCategoria.setCellFactory(column -> crearCeldaEstilizada());
        colFecha.setCellFactory(column -> crearCeldaEstilizada());

        cmbFiltroCategoria.setCellFactory(lv -> new ListCell<>() {
            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                setText(empty ? null : item);
                setStyle("-fx-background-color: #1E293B; -fx-text-fill: #F8FAFC;");
            }
        });
        cmbFiltroCategoria.setButtonCell(new ListCell<>() {
            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                setText(empty ? null : item);
                setStyle("-fx-text-fill: #F8FAFC;");
            }
        });
    }

    private TableCell<DocumentoModel, String> crearCeldaEstilizada() {
        return new TableCell<>() {
            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                    setStyle("-fx-background-color: #1E293B;");
                } else {
                    setText(item);
                    setStyle("-fx-background-color: #1E293B; -fx-text-fill: #F8FAFC; -fx-font-size: 13px;");
                }
            }
        };
    }

    private void configurarBotonDetalle() {
        colAccion.setCellFactory(param -> new TableCell<>() {
            private final Button btn = new Button("Ver");

            {
                btn.setStyle("-fx-background-color: #38BDF8; -fx-text-fill: #0F172A; -fx-font-weight: bold; -fx-cursor: hand; -fx-background-radius: 4; -fx-padding: 4 12;");
                btn.setOnAction(event -> {
                    DocumentoModel doc = getTableView().getItems().get(getIndex());
                    mostrarDetalleDocumento(doc, event);
                });
            }

            @Override
            protected void updateItem(Void item, boolean empty) {
                super.updateItem(item, empty);
                if (empty) {
                    setGraphic(null);
                    setStyle("-fx-background-color: #1E293B;");
                } else {
                    setGraphic(btn);
                    setStyle("-fx-background-color: #1E293B; -fx-alignment: CENTER;");
                }
            }
        });
    }

    private void mostrarDetalleDocumento(DocumentoModel doc, ActionEvent event) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/com/javafx/techmindinterface/Interfaces/ResultadoView.fxml"));
            Parent root = loader.load();

            ResultadoController controller = loader.getController();

            double confianza = 95.0;
            String idioma = "es";
            List<String> palabrasClave = new ArrayList<>();

            try {
                JsonNode datosInner = objectMapper.readTree(doc.getDatosJson());
                if (datosInner.has("idioma")) idioma = datosInner.get("idioma").asText();
                if (datosInner.has("confianza")) confianza = datosInner.get("confianza").asDouble() * 100;
                if (datosInner.has("palabras_clave") && datosInner.get("palabras_clave").isArray()) {
                    for (JsonNode tag : datosInner.get("palabras_clave")) {
                        palabrasClave.add(tag.asText());
                    }
                }
            } catch (Exception ignored) {}

            controller.setDatosResultado(doc.getCategoria(), confianza, idioma, palabrasClave);

            Stage stage = (Stage) ((Node) event.getSource()).getScene().getWindow();
            stage.getScene().setRoot(root);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @FXML
    private void handleNuevoAnalisis(ActionEvent event) {
        try {
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/com/javafx/techmindinterface/Interfaces/FormularioAnalisisView.fxml"));
            Parent root = loader.load();

            Stage stage = (Stage) ((Node) event.getSource()).getScene().getWindow();
            stage.getScene().setRoot(root);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}