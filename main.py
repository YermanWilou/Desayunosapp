import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window

class DesayunosApp(App):
    def build(self):
        self.cart = {
            'tea': 0,
            'beverage': 0,
            'cake': 0,
            'dobladita_no_cheese': 0,
            'dobladita_cheese': 0,
            'sandwich': 0
        }

        self.prices = {
            'tea': 400,
            'beverage': 400,
            'cake': 400,
            'dobladita_no_cheese': 600,
            'dobladita_cheese': 800,
            'sandwich': 1000
        }

        self.conn = sqlite3.connect('sales.db')
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            products TEXT,
            quantities TEXT,
            total INTEGER,
            payment INTEGER,
            change INTEGER
        )
        ''')

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Título de la sección de artículos con botón de reiniciar en la esquina superior derecha
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        title_label = Label(text="Artículos", font_size='24sp', size_hint_y=None, height=50, padding=[0, 10])
        title_layout.add_widget(title_label)

        reset_button = Button(text="Reiniciar", size_hint_x=None, width=100)
        reset_button.bind(on_press=self.reset_cart)
        title_layout.add_widget(reset_button)

        layout.add_widget(title_layout)

        # Área desplazable para las imágenes
        scroll_view = ScrollView(size_hint=(1, 0.55), do_scroll_x=False, do_scroll_y=True)
        scroll_layout = GridLayout(cols=2, spacing=0, padding=[50, -20, 100, 10], size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Agregar botones con imágenes y etiquetas
        for product in self.cart.keys():
            item_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=250, spacing=5)
            
            # Envolver el label y el botón en otro BoxLayout para centrar el texto
            text_and_image_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=250, spacing=5, padding=[20, 0])
            
            # Etiqueta con texto centrado
            label = Label(
                text=self.get_product_label(product),
                size_hint_y=None,
                height=30,
                font_size='18sp',
                halign='center',
                valign='middle',
                text_size=(None, None)  # Ajusta el tamaño del texto
            )
            label.bind(size=label.setter('text_size'))
            text_and_image_layout.add_widget(label)

            # Cargar imagen y ajustar tamaño
            img_path = f'images/{product}.png'
            image_button = Button(size_hint=(None, None), size=(200, 200), background_normal=img_path, background_down=img_path)
            image_button.bind(on_press=self.add_to_cart(product))

            text_and_image_layout.add_widget(image_button)

            # Envolver en otro layout para centrar
            wrapper_layout = BoxLayout(size_hint=(1, None), height=250, padding=(20, 0))
            wrapper_layout.add_widget(text_and_image_layout)

            scroll_layout.add_widget(wrapper_layout)

        scroll_view.add_widget(scroll_layout)
        layout.add_widget(scroll_view)

        # Etiquetas de total y cambio
        info_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.25), spacing=5)

        self.total_label = Label(text="Total: 0 pesos", font_size='20sp', size_hint_y=None, height=40)
        info_layout.add_widget(self.total_label)

        self.payment_input = TextInput(hint_text="Ingrese monto", input_type='number', size_hint_y=None, height=40, font_size='18sp')
        info_layout.add_widget(self.payment_input)

        self.change_label = Label(text="Cambio: 0 pesos", font_size='20sp', size_hint_y=None, height=40)
        info_layout.add_widget(self.change_label)

        layout.add_widget(info_layout)

        # Botones de funcionalidad (solo dos botones abajo)
        button_layout = BoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=50)

        calculate_change_button = Button(text="Calcular Cambio", size_hint_x=0.5)
        calculate_change_button.bind(on_press=self.calculate_change)
        button_layout.add_widget(calculate_change_button)

        pay_button = Button(text="Pagar", size_hint_x=0.5)
        pay_button.bind(on_press=self.process_payment)
        button_layout.add_widget(pay_button)

        layout.add_widget(button_layout)

        return layout

    def get_product_label(self, product):
        labels = {
            'tea': 'Té',
            'beverage': 'Bebida',
            'cake': 'Pastel',
            'dobladita_no_cheese': 'Doblada sin queso',
            'dobladita_cheese': 'Doblada con queso',
            'sandwich': 'Sándwich'
        }
        return labels.get(product, product).capitalize()

    def add_to_cart(self, product):
        def callback(instance):
            self.cart[product] += 1
            self.update_total()
        return callback

    def update_total(self):
        total = sum(self.prices[product] * quantity for product, quantity in self.cart.items())
        self.total_label.text = f"Total: {total} pesos"

    def calculate_change(self, instance):
        total = sum(self.prices[product] * quantity for product, quantity in self.cart.items())
        payment = int(self.payment_input.text) if self.payment_input.text.isdigit() else 0
        change = payment - total
        self.change_label.text = f"Cambio: {change} pesos"

    def process_payment(self, instance):
        total = sum(self.prices[product] * quantity for product, quantity in self.cart.items())
        payment = int(self.payment_input.text) if self.payment_input.text.isdigit() else 0
        change = payment - total
        if change >= 0:
            self.save_sale(total, payment, change)
            self.reset_cart()
            self.change_label.text = "Cambio: 0 pesos"
        else:
            self.change_label.text = "Fondos insuficientes"

    def reset_cart(self, instance=None):
        for product in self.cart.keys():
            self.cart[product] = 0
        self.update_total()
        self.payment_input.text = ''
        self.change_label.text = "Cambio: 0 pesos"

    def save_sale(self, total, payment, change):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        products = ','.join(self.cart.keys())
        quantities = ','.join(str(q) for q in self.cart.values())

        self.conn.execute('''
        INSERT INTO sales (date, products, quantities, total, payment, change)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, products, quantities, total, payment, change))

        self.conn.commit()

    def on_stop(self):
        self.conn.close()

if __name__ == '__main__':
    DesayunosApp().run()
