from kivy.config import Config
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
import subprocess
import threading
import kivytransitions.transitions
from kivymd.theming import ThemeManager

Window.keyboard_anim_args = {"d":.2,"t":"linear"}
Config.set('kivy', 'keyboard_mode','dock')
Config.write()

class Accueil(Screen):
    pass


class Option(Screen):
    def save_options(self, options, name):
        i=0
        with open("options.txt", "w") as file:
            for option in options:
                file.write(f"{name[i]} : {option.text}\n")
                i= i+1
            file.close()

class PentestScreen(Screen):

    def check_checkbox(self, instance, name, file_name):
        with open(file_name, "w") as file:
            for i in range(0, len(name)):
                file.write(f'{name[i]}: {instance[i].active}\n')
            file.close()

    def start_loading(self):
        self.thread_test = threading.Thread(target=self.start_test)
        self.thread_test.start()

        self.thread_bar = threading.Thread(target=self.progress_bar)
        self.thread_bar.start()

    def start_test(self):
        subprocess.run(['python', 'nmapjson.py'])

    def stop_thread(self):
        self.thread_bar.join()
        self.thread_test.join()

    def progress_bar(self):
        self.progress_bar_var = self.manager.get_screen('LoadScreen').ids.progress_bar
        self.progress_bar_var.start()
        while True:
            try:
                with open("options.txt", "r") as file:
                    file.close()
            except:
                self.progress_bar_var.stop()
                self.manager.current = "Accueil"
                self.stop_thread()
                break

class PentestReseau(PentestScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "reseau"
        self.file_name = "reseau.txt"

class PentestSysteme(PentestScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "systeme"
        self.file_name = "systeme.txt"

class PentestReseauSysteme(PentestScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "reseausysteme"
        self.file_name = "reseausysteme.txt"


class LoadScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass

class MenuApp(MDApp):
    def build(self):
        Window.size = (480, 320)
        Window.fullscreen = False
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "900"
        return Builder.load_file("app.kv")


if __name__ == '__main__':
    MenuApp().run()