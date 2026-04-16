from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from cart_service import CartService


class CartWindow(QMainWindow):
    cart_updated = pyqtSignal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.cart_service = CartService()
        self.initUI()
        self.load_cart()

    def initUI(self):
        self.setWindowTitle("Корзина - TechStore")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)

        # Шапка
        header = QWidget()
        header.setStyleSheet("background-color: #19493f;")
        header_layout = QHBoxLayout(header)

        logo = QLabel("TechStore")
        logo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(logo)

        header_layout.addStretch()

        title = QLabel("КОРЗИНА")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.btn_theme = QPushButton("🌓")
        self.btn_theme.setFixedSize(35, 35)
        self.btn_theme.setStyleSheet("background-color: transparent; color: white;")
        header_layout.addWidget(self.btn_theme)

        layout.addWidget(header)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Название", "Описание", "Кол-во", "Цена", "Сумма"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Сумма
        sum_widget = QWidget()
        sum_widget.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        sum_layout = QHBoxLayout(sum_widget)

        sum_label = QLabel("Общая сумма заказов:")
        sum_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        sum_layout.addWidget(sum_label)

        sum_layout.addStretch()

        self.lbl_total = QLabel("0 ₽")
        self.lbl_total.setStyleSheet("font-weight: bold; font-size: 18px; color: #359A85;")
        sum_layout.addWidget(self.lbl_total)

        layout.addWidget(sum_widget)

        # Нижняя панель
        footer = QWidget()
        footer.setStyleSheet("background-color: #19493f;")
        footer_layout = QHBoxLayout(footer)

        self.btn_clear = QPushButton("🗑 ОЧИСТИТЬ КОРЗИНУ")
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #fc8181;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
        """)
        self.btn_clear.clicked.connect(self.clear_cart)
        footer_layout.addWidget(self.btn_clear)

        footer_layout.addStretch()

        self.btn_checkout = QPushButton("ОФОРМИТЬ ЗАКАЗ")
        self.btn_checkout.setStyleSheet("""
            QPushButton {
                background-color: #359A85;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #19493f;
            }
        """)
        self.btn_checkout.clicked.connect(self.checkout)
        footer_layout.addWidget(self.btn_checkout)

        layout.addWidget(footer)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

    def load_cart(self):
        items = self.cart_service.get_cart(self.user["id"])

        self.table.setRowCount(len(items))
        total = 0

        for i, item in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(item["name"]))
            self.table.setItem(i, 1, QTableWidgetItem(item["description"][:50]))
            self.table.setItem(i, 2, QTableWidgetItem(str(item["quantity"])))
            self.table.setItem(i, 3, QTableWidgetItem(f"{item['final_price']:,.0f} ₽"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{item['total']:,.0f} ₽"))

            self.table.item(i, 0).setData(Qt.UserRole, item["product_id"])
            total += item["total"]

        self.lbl_total.setText(f"{total:,.0f} ₽")

    def clear_cart(self):
        reply = QMessageBox.question(self, "Подтверждение", "Очистить всю корзину?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.cart_service.clear_cart(self.user["id"])
            self.load_cart()
            self.cart_updated.emit()

    def checkout(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Подтвердить заказ?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.cart_service.create_order(self.user["id"]):
                QMessageBox.information(self, "Успех", "Заказ оформлен!")
                self.load_cart()
                self.cart_updated.emit()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось оформить заказ")

    def show_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if index.isValid():
            product_id = self.table.item(index.row(), 0).data(Qt.UserRole)

            menu = QMenu()
            remove_action = menu.addAction("❌ Удалить из корзины")
            remove_action.triggered.connect(lambda: self.remove_item(product_id))
            menu.exec_(self.table.mapToGlobal(pos))

    def remove_item(self, product_id):
        self.cart_service.remove_from_cart(self.user["id"], product_id)
        self.load_cart()
        self.cart_updated.emit()