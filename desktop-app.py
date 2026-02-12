from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (
    QApplication,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from models import (
    createProduct,
    create_tables,
    deleteProduct,
    listProducts,
    readProduct,
    updateProduct,
)


class ProductWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Product Manager")
        self.resize(820, 520)

        self.id_input = QLineEdit()
        self.id_input.setValidator(QIntValidator(1, 10**9))
        self.name_input = QLineEdit()
        self.qty_input = QLineEdit()
        self.qty_input.setValidator(QIntValidator(0, 10**9))
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator(0.0, 10**9, 4))

        form_layout = QFormLayout()
        form_layout.addRow("Product ID", self.id_input)
        form_layout.addRow("Name", self.name_input)
        form_layout.addRow("Quantity", self.qty_input)
        form_layout.addRow("Price", self.price_input)

        self.create_btn = QPushButton("Create")
        self.read_btn = QPushButton("Read")
        self.update_btn = QPushButton("Update")
        self.delete_btn = QPushButton("Delete")
        self.refresh_btn = QPushButton("Refresh")
        self.clear_btn = QPushButton("Clear")

        btn_row = QHBoxLayout()
        for btn in (
            self.create_btn,
            self.read_btn,
            self.update_btn,
            self.delete_btn,
            self.refresh_btn,
            self.clear_btn,
        ):
            btn_row.addWidget(btn)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Quantity", "Price"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignLeft)

        layout = QGridLayout()
        layout.addLayout(form_layout, 0, 0)
        layout.addLayout(btn_row, 1, 0)
        layout.addWidget(self.table, 2, 0)
        layout.addWidget(self.status_label, 3, 0)
        self.setLayout(layout)

        self.create_btn.clicked.connect(self.on_create)
        self.read_btn.clicked.connect(self.on_read)
        self.update_btn.clicked.connect(self.on_update)
        self.delete_btn.clicked.connect(self.on_delete)
        self.refresh_btn.clicked.connect(self.load_products)
        self.clear_btn.clicked.connect(self.clear_inputs)
        self.table.cellClicked.connect(self.on_table_click)

        create_tables()
        self.load_products()

    def _get_int(self, input_box, field_name, allow_empty=False):
        text = input_box.text().strip()
        if not text:
            if allow_empty:
                return None
            raise ValueError(f"{field_name} is required")
        return int(text)

    def _get_float(self, input_box, field_name, allow_empty=False):
        text = input_box.text().strip()
        if not text:
            if allow_empty:
                return None
            raise ValueError(f"{field_name} is required")
        return float(text)

    def set_status(self, message):
        self.status_label.setText(message)

    def clear_inputs(self):
        self.id_input.clear()
        self.name_input.clear()
        self.qty_input.clear()
        self.price_input.clear()

    def on_create(self):
        try:
            name = self.name_input.text().strip()
            if not name:
                raise ValueError("Name is required")
            quantity = self._get_int(self.qty_input, "Quantity")
            price = self._get_float(self.price_input, "Price")

            product = createProduct(name, quantity, price)
            self.set_status(f"Created product with id {product.id}")
            self.load_products()
        except Exception as exc:
            self.show_error(str(exc))

    def on_read(self):
        try:
            product_id = self._get_int(self.id_input, "Product ID")
            product = readProduct(product_id)
            if not product:
                self.set_status("Product not found")
                return
            self.name_input.setText(product.name)
            self.qty_input.setText(str(product.quantity_in_stock))
            self.price_input.setText(str(product.price_per_unit))
            self.set_status("Product loaded")
        except Exception as exc:
            self.show_error(str(exc))

    def on_update(self):
        try:
            product_id = self._get_int(self.id_input, "Product ID")
            name = self.name_input.text().strip() or None
            quantity = self._get_int(self.qty_input, "Quantity", allow_empty=True)
            price = self._get_float(self.price_input, "Price", allow_empty=True)

            product = updateProduct(product_id, name=name, quantity_in_stock=quantity, price_per_unit=price)
            if not product:
                self.set_status("Product not found")
                return
            self.set_status("Product updated")
            self.load_products()
        except Exception as exc:
            self.show_error(str(exc))

    def on_delete(self):
        try:
            product_id = self._get_int(self.id_input, "Product ID")
            deleted = deleteProduct(product_id)
            if not deleted:
                self.set_status("Product not found")
                return
            self.set_status("Product deleted")
            self.load_products()
        except Exception as exc:
            self.show_error(str(exc))

    def on_table_click(self, row, _column):
        self.id_input.setText(self.table.item(row, 0).text())
        self.name_input.setText(self.table.item(row, 1).text())
        self.qty_input.setText(self.table.item(row, 2).text())
        self.price_input.setText(self.table.item(row, 3).text())

    def load_products(self):
        products = listProducts()
        self.table.setRowCount(0)
        for product in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(product.id)))
            self.table.setItem(row, 1, QTableWidgetItem(product.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(product.quantity_in_stock)))
            self.table.setItem(row, 3, QTableWidgetItem(str(product.price_per_unit)))
        self.set_status(f"Loaded {len(products)} products")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication([])
    window = ProductWindow()
    window.show()
    app.exec_()
