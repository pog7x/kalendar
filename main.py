import os
import platform
from datetime import datetime, timezone

from picsexl import PIcsExl, PIcsExlException

if platform.system() == "Windows":
    os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix import textinput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

DEBUG = False

Window.size = (1200, 1500)


class TextInput(textinput.TextInput):
    def __init__(self, **kwargs):
        super(TextInput, self).__init__(**kwargs)
        self.padding_x = (
            [
                self.center[0]
                - self._get_text_width(
                    max(self._lines, key=len), self.tab_width, self._label_cached
                )
                / 2.0,
                0,
            ]
            if self.text
            else [self.center[0], 0]
        )
        self.padding_y = [
            self.height / 2.0 - (self.line_height / 2.0) * len(self._lines),
            0,
        ]


BLACK = 0, 0, 0, 1
YELLOW = 0.988, 0.725, 0.074, 1


class CalendarMachineLayout(GridLayout):
    def __init__(self, **kwargs):
        super(CalendarMachineLayout, self).__init__(**kwargs)

        with self.canvas.before:
            Color(*YELLOW, mode="rgba")
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(size=self.update_rect)

        self.cols = 1
        self.height = self.minimum_height

        self.general_input = GridLayout(
            cols=2,
            size_hint_y=1,
        )
        self.general_input.add_widget(
            Label(
                text="Путь до директории/файла:",
                color=BLACK,
                bold=True,
                text_size=(None, None),
                font_size="20sp",
            )
        )
        self.directory = TextInput(
            multiline=True,
            hint_text="User/example/path/to/directory",
            is_focusable=True,
        )
        self.general_input.add_widget(self.directory)

        self.general_input.add_widget(
            Label(
                text="Электронная почта:",
                color=BLACK,
                bold=True,
                text_size=(None, None),
                font_size="20sp",
            )
        )
        self.email = TextInput(
            multiline=True,
            hint_text="example@gmail.com",
            is_focusable=True,
        )
        self.general_input.add_widget(self.email)

        self.general_input.add_widget(
            Label(
                text="Дата начала:",
                color=BLACK,
                bold=True,
                text_size=(None, None),
                font_size="20sp",
            )
        )
        self.start_date = TextInput(
            multiline=True,
            hint_text="2022-07-01",
            is_focusable=True,
        )
        self.general_input.add_widget(self.start_date)

        self.general_input.add_widget(
            Label(
                text="Дата окончания:",
                color=BLACK,
                bold=True,
                text_size=(None, None),
                font_size="20sp",
            )
        )
        self.end_date = TextInput(
            multiline=True,
            hint_text="2022-07-31",
            is_focusable=True,
        )
        self.general_input.add_widget(self.end_date)

        self.add_widget(self.general_input)

        self.submit = Button(
            text="Выполнить",
            background_normal="",
            background_color=BLACK,
            size_hint_y=0.3,
            bold=True,
            text_size=(None, None),
            font_size="20sp",
            color=YELLOW,
        )

        self.submit.bind(on_press=self.press)
        self.add_widget(self.submit)

        self.error = Label(
            bold=True,
            text_size=(None, None),
            font_size="20sp",
            padding=[100, 100],
            color=BLACK,
        )
        self.add_widget(self.error)

    def press(self, instance):
        try:
            sd = datetime.strptime(self.start_date.text, "%Y-%m-%d")
            ed = datetime.strptime(self.end_date.text, "%Y-%m-%d")
            icj = PIcsExl(
                file_path=self.directory.text,
                mail_to=self.email.text,
                start_date=datetime(
                    sd.year, sd.month, sd.day, 0, 0, 0, tzinfo=timezone.utc
                ),
                end_date=datetime(
                    ed.year, ed.month, ed.day, 23, 59, 59, tzinfo=timezone.utc
                ),
            )
            new_excel = icj.run_sniff_and_write_ics_lines()
            self.error.color = "green"
            self.error.text = f"Успешно:\n{new_excel}"
        except PIcsExlException as e:
            self.error.color = "red"
            self.error.text = f"{e.msg}\n{e.exc}"
            if DEBUG is True:
                raise
        except Exception as e:
            self.error.color = "red"
            self.error.text = f"{e}"
            if DEBUG is True:
                raise

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class CalendarMachineApp(App):
    icon = "calendar_ico.png"
    title = "Calendar 🗓"

    def build(self):
        return CalendarMachineLayout()


if __name__ == "__main__":
    CalendarMachineApp().run()
