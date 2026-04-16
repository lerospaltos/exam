from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from product_service import ProductService
from cart_service import CartService


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.product_service = ProductService()
        self.cart_service = CartService()
        self.all_products = []
        self.current_products = []
        self.initUI()
        self.load_products()
        self.update_cart_count()

    def initUI(self):
        self.setWindowTitle(f"TechStore - {self.user['username']}")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(0)

        # Шапка
        header = QWidget()
        header.setStyleSheet("background-color: #19493f;")
        header_layout = QHBoxLayout(header)

        logo = QLabel("TechStore")
        logo.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        header_layout.addWidget(logo)

        header_layout.addStretch()

        self.btn_theme = QPushButton("🌓")
        self.btn_theme.setFixedSize(40, 40)
        self.btn_theme.setStyleSheet("background-color: transparent; color: white; font-size: 18px;")
        header_layout.addWidget(self.btn_theme)

        layout.addWidget(header)

        # Панель поиска
        search_panel = QWidget()
        search_panel.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        search_layout = QHBoxLayout(search_panel)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Поиск по названию или описанию...")
        self.txt_search.setStyleSheet("height: 35px; padding: 5px;")
        search_layout.addWidget(self.txt_search)

        self.cmb_sort = QComboBox()
        self.cmb_sort.addItems(["Без сортировки", "от 0% до 14.99%", "от 15% до 24.99%", "более 25%"])
        self.cmb_sort.setStyleSheet("height: 35px;")
        search_layout.addWidget(self.cmb_sort)

        self.btn_search = QPushButton("НАЙТИ")
        self.btn_search.setStyleSheet("""
            QPushButton {
                background-color: #359A85;
                color: white;
                font-weight: bold;
                height: 35px;
                width: 80px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #19493f;
            }
        """)
        self.btn_search.clicked.connect(self.search_products)
        search_layout.addWidget(self.btn_search)

        layout.addWidget(search_panel)

        # Список товаров
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #f0f0f0;")

        self.products_widget = QWidget()
        self.products_layout = QGridLayout(self.products_widget)
        self.products_layout.setSpacing(15)

        scroll.setWidget(self.products_widget)
        layout.addWidget(scroll)

        # Нижняя панель
        footer = QWidget()
        footer.setStyleSheet("background-color: #19493f;")
        footer_layout = QHBoxLayout(footer)

        self.lbl_counter = QLabel("Показано: 0 из 0")
        self.lbl_counter.setStyleSheet("color: white;")
        footer_layout.addWidget(self.lbl_counter)

        footer_layout.addStretch()

        self.btn_cart = QPushButton("🛒 Корзина (0)")
        self.btn_cart.setStyleSheet("""
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
        self.btn_cart.clicked.connect(self.open_cart)
        footer_layout.addWidget(self.btn_cart)

        layout.addWidget(footer)

        # Контекстное меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def load_products(self):
        self.all_products = self.product_service.get_all_products()
        self.current_products = self.all_products.copy()
        self.display_products()

    def display_products(self):
        for i in reversed(range(self.products_layout.count())):
            self.products_layout.itemAt(i).widget().setParent(None)

        row = 0
        col = 0
        for product in self.current_products:
            card = self.create_product_card(product)
            self.products_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        self.lbl_counter.setText(f"Показано: {len(self.current_products)} из {len(self.all_products)}")

    def create_product_card(self, product):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        card.setFixedWidth(280)

        layout = QHBoxLayout(card)

        image = QLabel("🖼️")
        image.setFixedSize(70, 70)
        image.setAlignment(Qt.AlignCenter)
        image.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; font-size: 30px;")
        layout.addWidget(image)

        info_layout = QVBoxLayout()

        name = QLabel(product["name"])
        name.setStyleSheet("font-weight: bold; font-size: 14px;")
        name.setWordWrap(True)
        info_layout.addWidget(name)

        desc = QLabel(
            product["description"][:50] + "..." if len(product["description"]) > 50 else product["description"])
        desc.setStyleSheet("font-size: 11px; color: #666;")
        desc.setWordWrap(True)
        info_layout.addWidget(desc)

        layout.addLayout(info_layout)

        price_layout = QVBoxLayout()
        price_layout.setAlignment(Qt.AlignRight)

        final_price = QLabel(f"{product['final_price']:,.0f} ₽")
        final_price.setStyleSheet("font-weight: bold; font-size: 16px; color: #359A85;")
        price_layout.addWidget(final_price)

        if product["discount"] > 0:
            old_price = QLabel(f"{product['price']:,.0f} ₽")
            old_price.setStyleSheet("font-size: 11px; color: #999; text-decoration: line-through;")
            price_layout.addWidget(old_price)

        layout.addLayout(price_layout)

        card.setProperty("product_id", product["id"])
        card.setProperty("product_name", product["name"])

        return card

    def search_products(self):
        search_text = self.txt_search.text()
        sort_option = self.cmb_sort.currentText()

        if search_text:
            self.current_products = self.product_service.search_products(search_text)
        else:
            self.current_products = self.all_products.copy()

        if sort_option == "от 0% до 14.99%":
            self.current_products = [p for p in self.current_products if 0 <= p["discount"] < 15]
        elif sort_option == "от 15% до 24.99%":
            self.current_products = [p for p in self.current_products if 15 <= p["discount"] < 25]
        elif sort_option == "более 25%":
            self.current_products = [p for p in self.current_products if p["discount"] >= 25]

        self.display_products()

    def show_context_menu(self, pos):
        widget = self.childAt(pos)
        while widget and not isinstance(widget, QFrame):
            widget = widget.parent()

        if widget and isinstance(widget, QFrame):
            product_id = widget.property("product_id")
            product_name = widget.property("product_name")

            if product_id:
                menu = QMenu()

                refresh_action = menu.addAction("🔄 Обновить")
                refresh_action.triggered.connect(self.load_products)

                add_action = menu.addAction("🛒 Добавить в корзину")
                add_action.triggered.connect(lambda: self.add_to_cart(product_id, product_name))

                menu.exec_(widget.mapToGlobal(pos))

    def add_to_cart(self, product_id, product_name):
        self.cart_service.add_to_cart(self.user["id"], product_id)
        self.update_cart_count()
        QMessageBox.information(self, "Добавлено", f"Товар \"{product_name}\" добавлен в корзину")

    def update_cart_count(self):
        count = self.cart_service.get_cart_count(self.user["id"])
        self.btn_cart.setText(f"🛒 Корзина ({count})")

    def open_cart(self):
        from cart_window import CartWindow
        self.cart_window = CartWindow(self.user)
        self.cart_window.cart_updated.connect(self.update_cart_count)
        self.cart_window.show()