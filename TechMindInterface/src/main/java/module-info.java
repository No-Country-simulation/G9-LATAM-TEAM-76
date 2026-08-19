module com.javafx.techmindinterface {
    requires javafx.controls;
    requires javafx.fxml;
    requires javafx.web;
    requires java.net.http;

    requires org.controlsfx.controls;
    requires net.synedra.validatorfx;
    requires org.kordamp.ikonli.javafx;
    requires eu.hansolo.tilesfx;

    requires com.fasterxml.jackson.databind;
    requires com.fasterxml.jackson.core;

    opens com.javafx.techmindinterface to javafx.fxml;
    exports com.javafx.techmindinterface;
}