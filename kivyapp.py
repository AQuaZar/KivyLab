import kivy
from kivy.app import App
from kivy.uix.label import Label
kivy.require('2.0.0')


class DesignerApp(App):
    def build(self):
        return Label(text="Hello world!")

if __name__ == '__main__':
    DesignerApp().run()
