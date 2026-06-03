import sys
import MySQLdb as mdb
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from login import Ui_MainWindow as LoginWindow
from products import Ui_MainWindow as ProductsUI
from product_card import Ui_Form
from edit_product import Ui_MainWindow as EditUI
from orders import Ui_MainWindow as OrdersUI
from order_card import Ui_Form as OrderCardUI
from edit_order import Ui_MainWindow as OrderEditUI


def select(query, params=()):
    con = mdb.connect('localhost', 'root', 'root', 'shoes_shop2')
    cur = con.cursor()
    cur.execute(query, params)
    data = cur.fetchall()
    con.close()
    return data

def execute(query, params=()):
    con = mdb.connect('localhost', 'root', 'root', 'shoes_shop2')
    cur = con.cursor()
    cur.execute(query, params)
    con.commit()
    con.close()

class LoginApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = LoginWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Авторизация")
        self.ui.btn_login.clicked.connect(self.login)
        self.ui.btn_guest.clicked.connect(self.open_guest)

    def login(self):
        login = self.ui.line_login.text()
        password = self.ui.line_password.text()
        user = select(
            "SELECT r.name, u.FIO FROM Users u JOIN Roles r ON u.RoleID = r.RoleID WHERE u.Login=%s AND u.Password=%s",
            (login, password)
        )
        if not user:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return
        role, fio = user[0]
        self.open_products(role, fio)

    def open_guest(self):
        self.open_products("guest", "Гость")

    def open_products(self, role, fio):
        self.w = ProductsWindow(role, fio)
        self.w.show()
        self.close()

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
        self.login_window = LoginApp()
        self.login_window.show()
        self.close()

class OrdersWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.ui = OrdersUI()
        self.ui.setupUi(self)
        self.role = role
        self.setWindowTitle("Заказы")

        if self.role != "Администратор":
            self.ui.btn_add.hide()
            self.ui.btn_edit.hide()
            self.ui.btn_delete.hide()

        self.ui.btn_add.clicked.connect(self.add_order)
        self.ui.btn_edit.clicked.connect(self.edit_order)
        self.ui.btn_delete.clicked.connect(self.delete_order)

        self.load_orders()

    def load_orders(self):
        for i in reversed(range(self.ui.verticalLayout.count())):
            item = self.ui.verticalLayout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        orders = select("""
            SELECT o.OrderID, so.Name, 
                   CONCAT(pp.City, ', ', pp.Street, ', ', pp.Building, ' (', pp.PostCode, ')') AS Address,
                   o.Date_order, o.Delivery_date
            FROM Orders o
            JOIN StatusOrder so ON o.StatusID = so.StatusID
            JOIN PostPoints pp ON o.PostID = pp.PostID
            ORDER BY o.OrderID DESC
        """)

        for order in orders:
            card = self.create_order_card(order)
            self.ui.verticalLayout.addWidget(card)
        self.ui.verticalLayout.addStretch()

    def create_order_card(self, order):
        widget = QWidget()
        ui = OrderCardUI()
        ui.setupUi(widget)
        widget.order_id = order[0]

        ui.article.setText(str(order[0]))
        ui.status.setText(order[1])
        ui.address.setText(order[2])
        ui.date_order.setText(order[3] if order[3] else "")
        ui.date_delivery.setText(order[4] if order[4] else "")

        widget.mousePressEvent = lambda event, oid=order[0]: setattr(self, 'selected_order_id', oid)
        widget.setFixedHeight(300)
        return widget

    def add_order(self):
        self.order_edit = OrderEdit(self)
        self.order_edit.show()

    def edit_order(self):
        if not hasattr(self, 'selected_order_id'):
            QMessageBox.warning(self, "Ошибка", "Сначала выберите заказ")
            return
        self.order_edit = OrderEdit(self, self.selected_order_id)
        self.order_edit.show()

    def delete_order(self):
        if not hasattr(self, 'selected_order_id'):
            QMessageBox.warning(self, "Ошибка", "Сначала выберите заказ")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить заказ?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            execute("DELETE FROM ProductInOrders WHERE OrderID=%s", (self.selected_order_id,))
            execute("DELETE FROM Orders WHERE OrderID=%s", (self.selected_order_id,))
            self.load_orders()

class OrderEdit(QMainWindow):
    def __init__(self, parent=None, order_id=None):
        super().__init__()
        self.ui = OrderEditUI()
        self.ui.setupUi(self)
        self.parent = parent
        self.order_id = order_id
        self.post_combo = QComboBox(self)
        self.post_map = {}
        self.load_post_points()
        self.ui.edit_address.hide()
        layout = self.ui.edit_address.parent().layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() == self.ui.edit_address:
                layout.replaceWidget(self.ui.edit_address, self.post_combo)
                break

        self.ui.btn_save.clicked.connect(self.save)
        self.ui.btn_cancel.clicked.connect(self.close)

        self.status_map = {}
        statuses = select("SELECT StatusID, Name FROM StatusOrder")
        self.ui.combo_status.clear()
        for sid, name in statuses:
            self.ui.combo_status.addItem(name, sid)
            self.status_map[name] = sid

        if order_id:
            self.load_data(order_id)

    def load_post_points(self):
        points = select("SELECT PostID, PostCode, City, Street, Building FROM PostPoints")
        self.post_combo.clear()
        for pid, code, city, street, building in points:
            display = f"{city}, {street}, {building} (индекс {code})"
            self.post_combo.addItem(display, pid)
            self.post_map[pid] = display

    def load_data(self, order_id):
        data = select("""
            SELECT o.StatusID, o.PostID, o.Date_order, o.Delivery_date
            FROM Orders o
            WHERE o.OrderID=%s
        """, (order_id,))
        if data:
            status_id, post_id, order_date, delivery_date = data[0]
            index = self.ui.combo_status.findData(status_id)
            if index >= 0:
                self.ui.combo_status.setCurrentIndex(index)
            idx = self.post_combo.findData(post_id)
            if idx >= 0:
                self.post_combo.setCurrentIndex(idx)
            self.ui.edit_id.setText(str(order_id))
            if order_date:
                self.ui.edit_date_order.setDate(QDate.fromString(order_date, "yyyy-MM-dd"))
            if delivery_date:
                self.ui.edit_delivery.setDate(QDate.fromString(delivery_date, "yyyy-MM-dd"))

    def save(self):
        status_id = self.ui.combo_status.currentData()
        post_id = self.post_combo.currentData()
        order_date = self.ui.edit_date_order.date().toString("yyyy-MM-dd")
        delivery_date = self.ui.edit_delivery.date().toString("yyyy-MM-dd")
        user_id = 1
        code = None

        if self.order_id:
            execute("""
                UPDATE Orders SET StatusID=%s, PostID=%s, Date_order=%s, Delivery_date=%s, UserId=%s, Code=%s
                WHERE OrderID=%s
            """, (status_id, post_id, order_date, delivery_date, user_id, code, self.order_id))
        else:
            execute("""
                INSERT INTO Orders (StatusID, PostID, Date_order, Delivery_date, UserId, Code)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (status_id, post_id, order_date, delivery_date, user_id, code))

        if self.parent:
            self.parent.load_orders()
        self.close()

class ProductForm(QMainWindow):
    def __init__(self, parent=None, product_id=None):
        super().__init__()
        self.ui = EditUI()
        self.ui.setupUi(self)
        self.parent = parent
        self.product_id = product_id
        self.image_path = None

        self.ui.btn_save.clicked.connect(self.save)
        self.ui.btn_cancel.clicked.connect(self.close)
        self.ui.btn_upload_image.clicked.connect(self.upload_image)
        self.load_categories()
        self.load_manufacturers()
        self.load_suppliers()

        if product_id:
            self.load_data(product_id)

    def upload_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выбрать фото", "", "Images (*.png *.jpg)")
        if file:
            self.image_path = file
            pixmap = QPixmap(file)
            self.ui.label_image_edit.setPixmap(pixmap.scaled(150, 150))

    def load_categories(self):
        categories = select("SELECT CategoryID, Name FROM Categories")
        for cid, name in categories:
            self.ui.combo_category.addItem(name, cid)

    def load_manufacturers(self):
        manufacturers = select("SELECT ManufID, Name FROM Manufacturers")
        for mid, name in manufacturers:
            self.ui.combo_manufacturer.addItem(name, mid)

    def load_suppliers(self):
        suppliers = select("SELECT SupID, Name FROM Suppliers")
        for sid, name in suppliers:
            self.ui.combo_supplier.addItem(name, sid)

    def load_data(self, pid):
        product = select("SELECT * FROM Products WHERE ProductID=%s", (pid,))
        if not product:
            return
        p = product[0]
        self.ui.edit_id.setText(str(p[0]))
        self.ui.edit_name.setText(p[1])
        self.ui.edit_description.setText(p[3])
        idx = self.ui.combo_category.findData(p[2])
        if idx >= 0:
            self.ui.combo_category.setCurrentIndex(idx)
        idx = self.ui.combo_manufacturer.findData(p[4])
        if idx >= 0:
            self.ui.combo_manufacturer.setCurrentIndex(idx)
        idx = self.ui.combo_supplier.findData(p[5])
        if idx >= 0:
            self.ui.combo_supplier.setCurrentIndex(idx)
        self.ui.edit_price.setText(str(p[6]))
        self.ui.edit_unit.setText(p[7])
        self.ui.edit_quantity.setText(str(p[8]))
        self.ui.edit_discount.setText(str(p[9]))
        self.image_path = p[10]
        if self.image_path:
            pixmap = QPixmap(self.image_path)
            self.ui.label_image_edit.setPixmap(pixmap.scaled(150, 150))

    def save(self):
        name = self.ui.edit_name.text()
        category_id = self.ui.combo_category.currentData()
        description = self.ui.edit_description.text()
        manufacturer_id = self.ui.combo_manufacturer.currentData()
        supplier_id = self.ui.combo_supplier.currentData()
        price = self.ui.edit_price.text()
        unit = self.ui.edit_unit.text()
        quantity = self.ui.edit_quantity.text()
        discount = self.ui.edit_discount.text()

        if self.product_id:
            execute("""
                UPDATE Products SET
                Name=%s, CategoryID=%s, Description=%s,
                ManufID=%s, SupID=%s,
                Price=%s, Unit=%s, Quantity=%s,
                Discount=%s, Image=%s
                WHERE ProductID=%s
            """, (name, category_id, description,
                  manufacturer_id, supplier_id,
                  price, unit, quantity,
                  discount, self.image_path, self.product_id))
        else:
            execute("""
                INSERT INTO Products
                (Name, CategoryID, Description, ManufID, SupID,
                 Price, Unit, Quantity, Discount, Image)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (name, category_id, description,
                  manufacturer_id, supplier_id,
                  price, unit, quantity,
                  discount, self.image_path))

        if self.parent:
            self.parent.search()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())