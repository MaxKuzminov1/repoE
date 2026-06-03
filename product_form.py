from PyQt6.QtWidgets import QMainWindow, QFileDialog
from PyQt6.QtGui import QPixmap
from edit_product import Ui_MainWindow as EditUI
from db import select, execute

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