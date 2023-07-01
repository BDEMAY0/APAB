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
from kivy.base import EventLoop
import netifaces
from kivy.properties import StringProperty
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from pdf2image import convert_from_path
from kivy.uix.carousel import Carousel
from kivy.uix.scrollview import ScrollView
from kivy.uix.scatter import Scatter
from kivy.uix.relativelayout import RelativeLayout
import time
import re

Window.keyboard_anim_args = {"d":.2,"t":"linear"}
Config.set('kivy','keyboard_mode','dock')
Config.write()

class Accueil(Screen):
    pass


class Option(Screen):

    def dialog(field):
        def close_dialog(*args):
            field_dialog.dismiss()
        field_dialog = MDDialog(
            title=f'{field} invalide',
            type="custom",
            buttons=[
                MDFlatButton(text="Fermer", on_release=close_dialog),
            ],
        )
        field_dialog.open()

    def is_valid_email(email):
        """Valide une adresse e-mail"""
        pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        return bool(pattern.match(email))

    def is_valid_ipv4(ip):
        """Valide une adresse IPv4"""
        pattern = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        return bool(pattern.match(ip))

    def is_valid_ip_range(ip_range):
        """Valide un range d'adresse IPv4 et vérifie que le premier nombre est plus petit que le second"""
        pattern = re.compile(r'^((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))(-((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))$|$))')
        match = pattern.match(ip_range)
        if match:
            start, end = map(int, ip_range.split(".")[-1].split("-"))
            return start < end
        return False
            

    def save_options(self, options, name):
        i = 0
        valid = 0
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
                    if Option.is_valid_ipv4(tmp) != True:
                        Option.dialog("IP")
                        valid = 1
                if name[i] == "masque_sous_reseau" and option.text != "":
                    if int(option.text) < 0 or int(option.text) > 32:
                        Option.dialog("Masque de sous réseau")
                        valid = 1
                if name[i] == "gateway" and option.text != "":
                    if Option.is_valid_ipv4(option.text) != True:
                        Option.dialog("Passerelle")
                        valid = 1
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
                if name[i] == "ip_ex" and option.text != "":
                    segments = [seg.strip() for seg in option.text.split(",")]
                    all_valid = all(Option.is_valid_ipv4(seg) or Option.is_valid_ip_range(seg) for seg in segments)
                    if all_valid != True:
                        Option.dialog("Ip exclu")
                        valid = 1
                if name[i] == "mail_entreprise" and option.text != "":
                    if Option.is_valid_email(option.text) != True:
                        Option.dialog("mail")
                        valid = 1
                file.write(f"{name[i]} : {option.text}\n")
                i= i+1
            file.close()
            if valid == 0:
                self.manager.current= 'PentestScreen'

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

    def dialog():
        def close_dialog(*args):
            field_dialog.dismiss()
        field_dialog = MDDialog(
            title=f'Aucun test choisi',
            type="custom",
            buttons=[
                MDFlatButton(text="Fermer", on_release=close_dialog),
            ],
        )
        field_dialog.open()

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
        check = 0
        for i in range(0, len(name)):
            if instance[i].active == True:
                check += 1
        if check > 0:
            with open(file_name, "w") as file:
                for i in range(0, len(name)):
                    file.write(f'{name[i]} : {instance[i].active}\n')
                file.write(f'En cours : chargement\n')
                file.close()
                PentestScreen.start_loading(self)
        else:
            PentestScreen.dialog()

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
    
    ip = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_ip, 1)  # update every 1 seconds
    
    def update_ip(self, *args):
        self.ip = self.ip_addr()

    def ip_addr(self, interface='eth0'):
        addr = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addr:
            return addr[netifaces.AF_INET][0]['addr']
        else:
            return ""

    def save_configuration(self, options, name):
        valid = 0
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
            if Option.is_valid_ipv4(options[1].text) != True or options[1].text== "":
                Option.dialog("IP")
                valid = 1
            if options[2].text != "":
                if int(options[2].text) < 0 or  int(options[2].text) > 32:
                    Option.dialog("Masque de sous réseau")
                    valid = 1
            if options[2].text == "":
                Option.dialog("Masque de sous réseau")
                valid = 1
            if options[3].text != "":
                if Option.is_valid_ipv4(options[3].text) != True:
                    Option.dialog("Passerelle")
                    valid = 1
            if valid == 0:
                config_line = f'interface eth0\nstatic ip_address={options[1].text}/{options[2].text}\nstatic routers={options[3].text}\n'
                with open('/etc/dhcpcd.conf', 'a') as f:
                    f.write(config_line)
                    f.close()
        
        if valid == 0:
            os.system('sudo systemctl restart dhcpcd')
            self.manager.current= 'Accueil'

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

    def on_start(self):
        EventLoop.window.bind(on_request_close=self.on_request_close)

    def on_request_close(self, *args, **kwargs):
        # Retournez True pour empêcher la fermeture de l'application
        return True

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
                current_dir = os.path.dirname(os.path.abspath(__file__))
                images = convert_from_path(path)
                folder = os.path.join(current_dir, "data", "previsualisation")
                path_options = os.path.expanduser(folder)
                subprocess.run(f'rm {path_options}/*.png', shell=True)
                time_suffix = str(time.time())
                for i, image in enumerate(images):
                    image.save(f'{path_options}/image_{i}_{time_suffix}.png', 'PNG')
                carousel = Carousel(direction='right')
                for i in range(len(images)):
                    scatter = Scatter(do_rotation=False, 
                              do_translation=True,
                              scale=5)
                    scatter.size = Window.size
                    img = Image(source=f'{path_options}/image_{i}_{time_suffix}.png', 
                                center_x=76 , center_y=45)
                    scatter.add_widget(img)
            
                    relative_layout = RelativeLayout()
                    relative_layout.add_widget(scatter)
                    
                    carousel.add_widget(relative_layout)

                # Créez un Popup avec le Carousel comme contenu :
                popup = Popup(title='Prévisualisation',
                            content=carousel,
                            size_hint=(0.8, 1))

                # Affichez le Popup :
                popup.open()

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
            subprocess.run(f'rm {fichier}/ressources/nmap/output.json', shell=True)
            subprocess.run(f'rm {fichier}/ressources/rapport/audit.json', shell=True)
            subprocess.run(f'rm {fichier}/ressources/rapport/rapport_attaque.json', shell=True)
            subprocess.run(f'rm {fichier}/ressources/wifi/capture*', shell=True)
            subprocess.run(f'rm {fichier}/previsualisation/*.png', shell=True)
            reset_dialog.dismiss()

        reset_dialog = MDDialog(
                    title="Réinitialiser la machine ?",
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
