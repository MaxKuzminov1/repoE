from PyQt6.QtWidgets import QMainWindow, QWidget, QMessageBox
from PyQt6.QtGui import QPixmap
from products import Ui_MainWindow as ProductsUI
from product_card import Ui_Form
from db import select, execute
from product_form import ProductForm
from orders_window import OrdersWindow

class ProductsWindow(QMainWindow):
    def __init__(self, role, fio):
        super().__init__()
        self.ui = ProductsUI()
        self.ui.setupUi(self)
        self.setWindowTitle("Товары")
        self.ui.line_search.textChanged.connect(self.search)
        self.ui.combo_supplier.currentIndexChanged.connect(self.search)
        self.ui.combo_sort.currentIndexChanged.connect(self.search)
        self.ui.btn_add.clicked.connect(self.open_add)
        self.ui.btn_edit.clicked.connect(self.open_edit)
        self.ui.btn_delete.clicked.connect(self.delete_product)
        self.ui.btn_logout.clicked.connect(self.logout)
        self.ui.btn_orders.clicked.connect(self.open_orders)
        self.role = role
        self.fio = fio
        self.ui.label_user.setText(self.fio)

        if self.role == "Администратор":
            pass
        elif self.role == "Менеджер":
            self.ui.btn_add.hide()
            self.ui.btn_edit.hide()
            self.ui.btn_delete.hide()
        else:
            self.ui.btn_add.hide()
            self.ui.btn_edit.hide()
            self.ui.btn_delete.hide()
            self.ui.line_search.hide()
            self.ui.combo_supplier.hide()
            self.ui.combo_sort.hide()
            self.ui.btn_orders.hide()

        self.search()
        self.load_suppliers()

    def load_products(self, query, params=()):
        products = select(query, params)
        for i in reversed(range(self.ui.verticalLayout.count())):
            item = self.ui.verticalLayout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        for product in products:
            card = self.create_card(product)
            self.ui.verticalLayout.addWidget(card)
        self.ui.verticalLayout.addStretch()

    def search(self):
        text = self.ui.line_search.text()
        query = f"""
            SELECT p.ProductID, p.Name, c.Name, p.Description,
                   m.Name, s.Name, p.Price,
                   p.Unit, p.Quantity, p.Discount, p.Image
            FROM Products p
            JOIN Categories c ON p.CategoryID = c.CategoryID
            JOIN Manufacturers m ON p.ManufID = m.ManufID
            JOIN Suppliers s ON p.SupID = s.SupID
            WHERE (p.Name LIKE %s OR c.Name LIKE %s OR p.Description LIKE %s OR m.Name LIKE %s OR s.Name LIKE %s)
            {self.get_filter()}
            {self.get_sort()}
        """
        self.load_products(query, (f"%{text}%",) * 5)

    def get_filter(self):
        supplier_id = self.ui.combo_supplier.currentData()
        if supplier_id and supplier_id != "Все поставщики":
            return f" AND p.SupID = {supplier_id}"
        return ""

    def get_sort(self):
        sort = self.ui.combo_sort.currentText()
        if sort == "Количество по возрастанию":
            return " ORDER BY p.Quantity ASC"
        elif sort == "Количество по убыванию":
            return " ORDER BY p.Quantity DESC"
        return ""

    def load_suppliers(self):
        suppliers = select("SELECT SupID, Name FROM Suppliers")
        self.ui.combo_supplier.addItem("Все поставщики", None)
        for sid, name in suppliers:
            self.ui.combo_supplier.addItem(name, sid)

    def create_card(self, product):
        widget = QWidget()
        widget.setMinimumHeight(250)
        ui = Ui_Form()
        ui.setupUi(widget)
        widget.product_id = product[0]
        widget.mousePressEvent = lambda event: setattr(self, 'selected_id', widget.product_id)

        ui.label_name.setText(product[1])
        ui.label_category.setText(product[2])
        ui.label_description_value.setText(product[3])
        ui.label_manufacturer_value.setText(product[4])
        ui.label_supplier_value.setText(product[5])
        ui.label_unit_value.setText(product[7])
        ui.label_quantity_value.setText(str(product[8]))
        ui.label_8.setText(f"Действующая скидка: {product[9]}%" if product[9] > 0 else "Действующей скидки нет")

        p, d = product[6], product[9]
        ui.label_price_value.setText(
            f'<span style="text-decoration: line-through; color: red;">{p:.2f}</span> {p * (100 - d) / 100:.2f}' if d > 0
            else f'{p:.2f}'
        )

        if product[8] == 0:
            widget.setStyleSheet("background-color: lightblue;")
        elif d > 15:
            widget.setStyleSheet("background-color: #2E8B57;")

        if product[10]:
            ui.label_image.setPixmap(QPixmap(product[10]).scaled(200, 200))
        return widget

    def open_add(self):
        self.form = ProductForm(self)
        self.form.show()

    def open_edit(self):
        if not hasattr(self, "selected_id"):
            QMessageBox.warning(self, "Ошибка", "Сначала кликни на товар")
            return
        self.form = ProductForm(self, self.selected_id)
        self.form.show()

    def delete_product(self):
        if not hasattr(self, "selected_id"):
            QMessageBox.warning(self, "Ошибка", "Сначала кликни на товар")
            return
        execute("DELETE FROM Products WHERE ProductID=%s", (self.selected_id,))
        self.search()

    def open_orders(self):
        self.orders_window = OrdersWindow(self.role)
        self.orders_window.show()

    def logout(self):
        from login_app import LoginApp
        self.login_window = LoginApp()
        self.login_window.show()
        self.close()