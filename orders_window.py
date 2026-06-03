from PyQt6.QtWidgets import QMainWindow, QWidget, QMessageBox
from orders import Ui_MainWindow as OrdersUI
from order_card import Ui_Form as OrderCardUI
from db import select, execute
from order_form import OrderEdit

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