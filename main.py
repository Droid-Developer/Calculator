import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import math
import re


class CalculatorWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)

        self.expression = ""
        self.result = "0"
        self.history = ""

        self.screen_width = Window.width
        self.screen_height = Window.height

        # УМЕРЕННЫЙ РАЗМЕР ДЛЯ ДИСПЛЕЯ, КНОПКИ ЧУТЬ МЕНЬШЕ
        self.display_font_size = self.get_display_font_size()
        self.button_font_size = self.get_button_font_size()
        self.history_font_size = self.display_font_size * 0.4

        # ---- Верхняя панель (дисплей) ----
        self.display_frame = BoxLayout(
            orientation='vertical',
            size_hint_y=0.2,
            padding=[dp(20), dp(10)]
        )
        with self.display_frame.canvas.before:
            Color(0.1647, 0.1647, 0.1647, 1)
            self.rect = Rectangle(size=self.display_frame.size, pos=self.display_frame.pos)
        self.display_frame.bind(pos=self.update_rect, size=self.update_rect)

        self.history_label = Label(
            text="",
            font_size=self.history_font_size,
            color=(0.4, 0.4, 0.4, 1),
            halign='right',
            valign='bottom',
            size_hint_y=0.3
        )
        self.history_label.bind(size=self.history_label.setter('text_size'))

        self.display_label = Label(
            text="0",
            font_size=self.display_font_size,
            bold=True,
            color=(1, 1, 1, 1),
            halign='right',
            valign='center',
            size_hint_y=0.7
        )
        self.display_label.bind(size=self.display_label.setter('text_size'))

        self.display_frame.add_widget(self.history_label)
        self.display_frame.add_widget(self.display_label)
        self.add_widget(self.display_frame)

        # ---- Сетка кнопок ----
        self.buttons_grid = GridLayout(cols=4, rows=5, spacing=dp(6), size_hint_y=0.8)
        self.add_widget(self.buttons_grid)

        buttons_data = [
            ('C', '#4a4a4a', '#ff6b6b', '#5a5a5a'),
            ('⌫', '#4a4a4a', '#ff6b6b', '#5a5a5a'),
            ('√', '#4a4a4a', '#6bcfff', '#5a5a5a'),
            ('÷', '#555555', '#ffffff', '#666666'),
            ('7', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('8', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('9', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('×', '#555555', '#ffffff', '#666666'),
            ('4', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('5', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('6', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('−', '#555555', '#ffffff', '#666666'),
            ('1', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('2', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('3', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('+', '#555555', '#ffffff', '#666666'),
            ('±', '#4a4a4a', '#6bcfff', '#5a5a5a'),
            ('0', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('.', '#3a3a3a', '#ffffff', '#4a4a4a'),
            ('=', '#555555', '#ffffff', '#666666')
        ]

        self.buttons = []
        for text, bg, fg, hover in buttons_data:
            btn = Button(
                text=text,
                font_size=self.button_font_size,
                bold=True,
                background_normal='',
                background_color=self.hex_to_rgb(bg),
                color=self.hex_to_rgb(fg),
                size_hint=(1, 1)
            )
            btn.bind(on_press=lambda instance, t=text: self.click(t))
            self.buttons_grid.add_widget(btn)
            self.buttons.append(btn)

        # ---- Клавиатура ----
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

        Clock.schedule_once(lambda dt: self.update_display(), 0.1)

    # ---- Вспомогательные методы ----
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (1,)

    def get_display_font_size(self):
        # УМЕРЕННО-КРУПНЫЙ ШРИФТ (без адаптации)
        if self.screen_width < 600:
            return 80
        elif self.screen_width < 1024:
            return 110
        else:
            return 140

    def get_button_font_size(self):
        # КНОПКИ ЧУТЬ МЕНЬШЕ ДИСПЛЕЯ
        if self.screen_width < 600:
            return 60
        elif self.screen_width < 1024:
            return 75
        else:
            return 90

    def update_display(self):
        # ФИКСИРОВАННЫЙ РАЗМЕР – НЕ УМЕНЬШАЕТСЯ
        self.display_label.text = self.result
        self.history_label.text = self.history
        self.display_label.font_size = self.display_font_size

    # ---- Структурированная логика вычислений ----
    def click(self, value):
        try:
            if value in '0123456789':
                self._handle_digit(value)
            elif value == '.':
                self._handle_dot()
            elif value in '+-−×÷':
                self._handle_operator(value)
            elif value == '=':
                self._handle_equal()
            elif value == 'C':
                self._handle_clear()
            elif value == '⌫':
                self._handle_backspace()
            elif value == '±':
                self._handle_negate()
            elif value == '√':
                self._handle_sqrt()
        except Exception:
            self.display_label.text = "Ошибка"
            self.expression = ""
            self.update_display()

    def _handle_digit(self, digit):
        if self.result in ["Ошибка", "0"]:
            self.expression = ""
        self.expression += digit
        self.result = self.expression
        self.update_display()

    def _handle_dot(self):
        parts = re.split(r'[+\−×÷]', self.expression)
        last_num = parts[-1] if parts else ''
        if '.' in last_num:
            return
        if not self.expression or self.expression[-1] in ['+', '−', '×', '÷']:
            self.expression += "0."
        else:
            self.expression += "."
        self.result = self.expression
        self.update_display()

    def _handle_operator(self, op):
        if op == '+':
            op = '+'
        elif op == '-':
            op = '−'
        elif op == '*':
            op = '×'
        elif op == '/':
            op = '÷'
        if not self.expression or self.expression in ["0", "Ошибка"]:
            if op == '−':
                self.expression = "-"
            else:
                self.expression = "0" + op
        else:
            last = self.expression[-1]
            if last in ['+', '−', '×', '÷']:
                if op == '−' and last != '−':
                    self.expression += op
                elif op == '−' and last == '−':
                    self.expression = self.expression[:-1] + '+'
                else:
                    self.expression = self.expression[:-1] + op
            else:
                self.expression += op
        self.result = self.expression
        self.update_display()

    def _handle_equal(self):
        try:
            self.history = self.expression + " ="
            expr = self.expression
            expr = expr.replace('÷', '/').replace('×', '*').replace('−', '-')
            if '√' in expr:
                expr = expr.replace('√', 'math.sqrt')
            result = eval(expr, {"__builtins__": None}, {"math": math})
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)
                    result = str(result).rstrip('0').rstrip('.')
                    if '.' not in str(result):
                        result = int(float(result))
            self.expression = str(result)
            self.result = str(result)
            self.update_display()
        except ZeroDivisionError:
            self.result = "Деление на ноль"
            self.expression = ""
            self.update_display()
        except Exception:
            self.result = "Ошибка"
            self.expression = ""
            self.update_display()

    def _handle_clear(self):
        self.expression = ""
        self.history = ""
        self.result = "0"
        self.update_display()

    def _handle_backspace(self):
        if self.expression:
            self.expression = self.expression[:-1]
            self.result = self.expression or "0"
            self.update_display()

    def _handle_negate(self):
        if self.expression and self.expression not in ["Ошибка", "0"]:
            if self.expression[0] == '-':
                self.expression = self.expression[1:]
            else:
                self.expression = '-' + self.expression
            self.result = self.expression
            self.update_display()

    def _handle_sqrt(self):
        try:
            num = float(self.expression) if self.expression else 0
            if num < 0:
                self.result = "Ошибка"
                self.expression = ""
            else:
                result = math.sqrt(num)
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)
                self.expression = str(result)
                self.result = str(result)
            self.update_display()
        except:
            self.result = "Ошибка"
            self.expression = ""
            self.update_display()

    # ---- Обработка клавиатуры ----
    def _keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'escape':
            App.get_running_app().stop()
        elif keycode[1] == 'enter':
            self.click('=')
        elif keycode[1] == 'backspace':
            self.click('←')
        elif keycode[1] == 'delete':
            self.click('C')
        else:
            if text in '0123456789':
                self.click(text)
            elif text == '.':
                self.click('.')
            elif text == '+':
                self.click('+')
            elif text == '-':
                self.click('−')
            elif text == '*':
                self.click('×')
            elif text == '/':
                self.click('÷')


class CalculatorApp(App):
    def build(self):
        Window.fullscreen = True
        return CalculatorWidget()

    def on_key_down(self, window, key, *args):
        if key == 27:
            self.stop()


if __name__ == '__main__':
    CalculatorApp().run()