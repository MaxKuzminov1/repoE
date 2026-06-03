from PyQt6.QtWidgets import QMainWindow, QComboBox
from PyQt6.QtCore import QDate
from edit_order import Ui_MainWindow as OrderEditUI
from db import select, execute

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