from kivy.config import Config
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
import subprocess
import threading
import kivytransitions.transitions
from kivymd.theming import ThemeManager
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.uix.list import OneLineListItem
import queue
from kivy.clock import Clock
from kivymd.uix.filemanager import MDFileManager
import os
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton
import shutil
from data.Package_Mail.zip_password import f_zip_encrypt
from data.Package_Mail.send_mail import f_send_mail
import netifaces as ni

Window.keyboard_anim_args = {"d":.2,"t":"linear"}
Config.set('kivy','keyboard_mode','dock')
Config.write()

class Accueil(Screen):
    pass


class Option(Screen):

    def save_options(self, options, name):
        i=0
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(current_dir, "data", "ressources", "parametres", "options.txt")
        path = os.path.expanduser(folder)
        with open(path, "w") as file:
            ip_info = ni.ifaddresses('eth0')
            ip_address = ip_info[ni.AF_INET][0]['addr']
            subnet_mask = ip_info[ni.AF_INET][0]['netmask']
            default_gateway = ni.gateways()['default'][ni.AF_INET][0]
            for option in options:
                if name[i] == "ip":
                    tmp = option.text
                if name[i] == "masque_sous_reseau" and option.text == "" and tmp != "0.0.0.0":
                    option.text = "24"
                if name[i] == "gateway" and option.text == "" and tmp != "0.0.0.0":
                    try:
                        cut = tmp.strip().split(".")
                        for z in range(3):
                            option.text += cut[z] + "."
                        option.text += "1"
                    except:
                        pass
                if name[i] == "ip" and option.text == "0.0.0.0":
                    try:
                        cut = ip_address.strip().split(".")
                        option.text = ''
                        for z in range(3):
                            option.text += cut[z] + "."
                        option.text += "0"
                    except:
                        pass
                if name[i] == "masque_sous_reseau" and option.text == "" and tmp == "0.0.0.0":
                    option.text = str(sum([bin(int(x)).count('1') for x in subnet_mask.split('.')]))
                if name[i] == "gateway" and option.text == "" and tmp == "0.0.0.0":
                    option.text = default_gateway
                file.write(f"{name[i]} : {option.text}\n")
                i= i+1
            file.close()

    def drop(self, instance):
        self.menu = MDDropdownMenu(
            caller=instance,
            items=[{"viewclass": "OneLineListItem", "text": "Public", "on_release": lambda x="Public": self.set_item(x)},
            {"viewclass": "OneLineListItem", "text": "Accès limité", "on_release": lambda x="Accès limité": self.set_item(x)}, 
            {"viewclass": "OneLineListItem", "text": "confidentiel", "on_release": lambda x="Document confidentiel": self.set_item(x)},
            {"viewclass": "OneLineListItem", "text": "Secret", "on_release": lambda x="Document secret": self.set_item(x)},
            {"viewclass": "OneLineListItem", "text": "Restreint", "on_release": lambda x="Diffusion restreinte": self.set_item(x)}
            ],
            position='bottom',
            width_mult=3,
            border_margin=dp(12),
            radius=[12, 12, 12, 12],
            elevation=4,
        )
        self.menu.open()

    def set_item(self, text__item):
        self.ids.niveau_diffusion.text = text__item
        self.menu.dismiss()


class PentestScreen(Screen):

    def __init__(self, **kwargs):
        super(PentestScreen, self).__init__(**kwargs)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(current_dir, "data", "ressources", "parametres", "pentest.txt")
        path = os.path.expanduser(folder)
        self.file_name= path
        self.message_queue = queue.Queue()

    def on_enter(self, *args):
        super(PentestScreen, self).on_enter(*args)
        Clock.schedule_interval(self.check_loading_finished, 0.5)

    def check_checkbox(self, instance, name, file_name):
        with open(file_name, "w") as file:
            for i in range(0, len(name)):
                file.write(f'{name[i]} : {instance[i].active}\n')
            file.write(f'En cours : chargement\n')
            file.close()

    def start_loading(self):
        self.stop_event = threading.Event()
        self.parent.current= 'LoadScreen'

        self.thread_test = threading.Thread(target=self.start_test)
        self.thread_test.start()

        self.thread_bar = threading.Thread(target=self.progress_bar)
        self.thread_bar.start()

    def start_test(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(current_dir, "data", "nmapjson.py")
        path = os.path.expanduser(folder)
        subprocess.run(['python', path])

    def check_loading_finished(self, dt):
        try:
            message = self.message_queue.get_nowait()
            if message == "finished":
                self.manager.current = "Accueil"
                self.stop_event.set()
                self.progress_bar_var.stop()
                Clock.unschedule(self.check_loading_finished)
        except queue.Empty:
            pass

    def progress_bar(self):
        self.progress_bar_var = self.manager.get_screen('LoadScreen').ids.progress_bar
        self.progress_bar_var.start()

        while not self.stop_event.is_set():
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                folder = os.path.join(current_dir, "data", "ressources", "parametres", "pentest.txt")
                path = os.path.expanduser(folder)
                with open(path, "r") as f:
                    for line in f:
                        key, value = line.strip().split(" :")
                        if key == "En cours" and value != " chargement":
                            self.message_queue.put("finished")
                            self.stop_event.set()
                    f.close()
            except:
                self.message_queue.put("finished")
                self.stop_event.set()

class Configuration(Screen):
    
    def save_configuration(self, options, name):
        if options[0].active == True:
            with open('/etc/dhcpcd.conf', 'r') as f:
                lines = f.readlines()
            with open('/etc/dhcpcd.conf', 'w') as f:
                for line in lines:
                    if f'interface eth0' in line:
                        break
                    f.write(line)
                f.close()
        else:
            config_line = f'interface eth0\nstatic ip_address={options[1].text}/{options[2].text}\nstatic routers={options[3].text}\n'
            with open('/etc/dhcpcd.conf', 'a') as f:
                f.write(config_line)
                f.close()
        os.system('sudo systemctl daemon-reload')
        os.system('sudo systemctl restart dhcpcd')

    def toggle_visibility(self, instance, value):
        # Modifier l'opacité des champs texte et boutons en fonction de l'état du bouton Switch
        ip_configuration = self.ids.ip_configuration
        masque_sous_reseau_configuration = self.ids.masque_sous_reseau_configuration
        gateway_configuration = self.ids.gateway_configuration

        if value:
            ip_configuration.opacity = 0
            masque_sous_reseau_configuration.opacity = 0
            gateway_configuration.opacity = 0
        else:
            ip_configuration.opacity = 1
            masque_sous_reseau_configuration.opacity = 1
            gateway_configuration.opacity = 1

class LoadScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass

class MenuApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )
        self.file_manager.ids.toolbar.right_action_items=[]
        self.file_manager.ids.toolbar.left_action_items=[]

    def file_manager_open(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(current_dir, "data", "rapport")
        path = os.path.expanduser(folder)
        self.file_manager.show(path)  # output manager to the screen
        self.manager_open = True
        self.file_manager.ids.toolbar.title = "Rapports"

    def exit_manager(self, *args):
        current_path = self.file_manager.current_path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(current_dir, "data", "rapport")
        path = os.path.expanduser(folder)

        if current_path == path:
            self.manager_open = False
            self.file_manager.close()
        else:
            self.file_manager.back()

    def rename_file(self, old_path, new_name):
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        os.rename(old_path, new_path)
        self.file_manager_open()

    def delete_file(self, path):
        os.remove(path)
        self.file_manager_open()

    def show_file(self, path):
        subprocess.run(["xdg-open", path], check=True)

    def extract_file(self, path):
        # Parcours des dossiers dans '/media'
        for folder in os.listdir('/media'):
            media_path = os.path.join('/media', folder)

            # Parcours des périphériques de stockage connectés
            for device in os.listdir(media_path):
                device_path = os.path.join(media_path, device)

                # Vérification que le chemin est un dossier (pour éviter les fichiers montés)
                if os.path.isdir(device_path):
                    # Copie du fichier vers le périphérique de stockage
                    try:
                        shutil.copy(path, device_path)
                        print(f'Fichier copié avec succès vers {device_path}')
                        return True
                    except Exception as e:
                        print(f'Erreur lors de la copie : {e}')
                        return False
        print("Aucun périphérique de stockage trouvé.")
        return False       

    def select_path(self, path):
        if path[-3:] == "pdf":
            def rename_callback():
                self.file_menu.dismiss()
                def close_rename_dialog(*args):
                    rename_dialog.dismiss()

                def rename_action(*args):
                    self.rename_file(path, rename_input.text)
                    close_rename_dialog()

                rename_dialog = MDDialog(
                    title="Renommer le fichier",
                    type="custom",
                    content_cls=MDTextField(
                        hint_text="Nouveau nom",
                        text=os.path.basename(path),
                    ),
                    buttons=[
                        MDFlatButton(text="Annuler", on_release=close_rename_dialog),
                        MDFlatButton(text="Renommer", on_release=rename_action),
                    ],
                )
                rename_input = rename_dialog.content_cls
                rename_dialog.open()

            def delete_callback():
                self.file_menu.dismiss()
                self.delete_file(path)

            def open_callback():
                self.file_menu.dismiss()
                subprocess.run(["xdg-open", path], check=True)

            def extract_callback():
                self.file_menu.dismiss()
                self.extract_file(path)

            def mail_callback(*args):
                name_file = os.path.basename(path)
                def close_pass_dialog(*args):
                    password = password_field.text
                    f_zip_encrypt(name_file, password)
                    f_send_mail(name_file)
                    pass_dialog.dismiss()

                def close_field_dialog(*args):
                    field_dialog.dismiss()

                current_dir = os.path.dirname(os.path.abspath(__file__))
                folder = os.path.join(current_dir, "data", "ressources", "parametres", "options.txt")
                path_options = os.path.expanduser(folder)
                with open(path_options, "r") as f:
                    for line in f:
                        key, value = line.strip().split(" :")
                        if key == "mail_entreprise" and value != "":
                            password_field = MDTextField(size_hint=(0.8, None), pos_hint={"center_x": 0.5})
                            pass_dialog = MDDialog(
                                title=f'Entrez le mot de passe de chiffrement du rapport :',
                                type="custom",
                                content_cls=password_field,
                                buttons=[
                                    MDFlatButton(text="Envoyer", on_release=close_pass_dialog),
                                ],
                            )
                            pass_dialog.open()
                            break
                        elif key == "mail_entreprise" and value == "":
                            field_dialog = MDDialog(
                                title=f'Pas de mail renseigner',
                                type="custom",
                                buttons=[
                                    MDFlatButton(text="Fermer", on_release=close_field_dialog),
                                ],
                            )
                            field_dialog.open()
                            break
                


            self.file_menu = MDDropdownMenu(
                caller=self.file_manager,
                items=[
                    {"viewclass": "OneLineListItem", "text": "Ouvrir", "on_release": open_callback},
                    {"viewclass": "OneLineListItem", "text": "Renommer", "on_release": rename_callback},
                    {"viewclass": "OneLineListItem", "text": "Supprimer", "on_release": delete_callback},
                    {"viewclass": "OneLineListItem", "text": "Extraire disque externe", "on_release": extract_callback},   
                    {"viewclass": "OneLineListItem", "text": "Extraire mail", "on_release": mail_callback},      
                ],
                position='bottom',
                width_mult=4,
                border_margin=dp(12),
                radius=[12, 12, 12, 12],
                elevation=4,
            )
            self.file_menu.open()
        else:
            self.file_manager.close()

    def reset_callback(self):
        def close_reset_dialog(*args):
            reset_dialog.dismiss()

        def reset(*args):
            with open('/etc/dhcpcd.conf', 'r') as f:
                lines = f.readlines()
            with open('/etc/dhcpcd.conf', 'w') as f:
                for line in lines:
                    if f'interface eth0' in line:
                        break
                    f.write(line)
            f.close()
            os.system('sudo systemctl daemon-reload')
            os.system('sudo systemctl restart dhcpcd')
            current_dir = os.path.dirname(os.path.abspath(__file__))
            fichier = os.path.join(current_dir, "data")
            subprocess.run(f'rm {fichier}/ressources/parametres/options.txt', shell=True)
            for pdf in os.listdir(f'{fichier}/rapport'):
                subprocess.run(f'rm {fichier}/rapport/{pdf}', shell=True)
            reset_dialog.dismiss()

        reset_dialog = MDDialog(
                    title="Réinitialisé la machine ?",
                    type="custom",
                    buttons=[
                        MDFlatButton(text="Oui", on_release=reset),
                        MDFlatButton(text="Non", on_release=close_reset_dialog),
                    ],
                )
        reset_dialog.open()

    def build(self):
        Window.size = (480, 320)
        Window.fullscreen = False
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "900"
        return Builder.load_file("app.kv")


if __name__ == '__main__':
    MenuApp().run()
