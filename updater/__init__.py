#!/usr/bin/python3
import requests, zipfile, os, shutil

class UpdaterConfig:
    def __init__(self, 
                github_name: str = "", 
                github_repository_name: str = "", 
                update_mode: str = "", 
                release_tag: str = "", 
                file_name: str = "", 
                file_url: str = "", 
                chunk_size: int = 8192, 
                update_check_url: str = "", 
                current_ver_file: str = "ver.txt", 
                update_folder_name: str = ""):
        self.github_name = github_name
        self.github_repository_name = github_repository_name
        self.update_mode = update_mode
        self.release_tag = release_tag
        self.file_name = file_name
        self.file_url = file_url
        self.chunk_size = chunk_size
        self.update_check_url = update_check_url
        self.current_ver_file = current_ver_file
        self.update_folder_name = update_folder_name

class Updater:
    def __init__(self, config: UpdaterConfig):
        self.config = config
        self.new_ver = None
        self.file_url = None
        self.current_ver = None
    def check_update(self):
        try:
            check = requests.get(self.config.update_check_url, timeout=(5, 10))
            check.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            return False
        self.new_ver = check.text

        if self.config.update_mode == "release":
            self.file_url = "https://github.com/" + self.config.github_name + "/" + self.config.github_repository_name + "/releases/download/" + self.config.release_tag + "/" + self.config.file_name

        self.current_ver = open(self.config.current_ver_file, "r").read()

        if self.new_ver > self.current_ver:
            print("A new version update is available. (You can download the update using the `download_update` function.)")
    def download_update(self):
        if self.new_ver > self.current_ver:
            try:
                download = requests.get(self.file_url, stream=True, timeout=(5, 20))
                download.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(e)
                return False
            with open(self.config.file_name, "wb") as f:
                for chunk in download.iter_content(self.config.chunk_size):
                    if chunk:
                        f.write(chunk)
        with zipfile.ZipFile(self.config.file_name, 'r') as zip_ext:
            zip_ext.extractall()
    def apply_update(self):
        main_folder = os.path.dirname(os.path.abspath(__file__))
        update_folder = os.path.join(main_folder, self.config.update_folder_name)

        for item in os.listdir(update_folder):
            src = os.path.join(update_folder, item)
            dist = os.path.join(main_folder, item)

            if os.path.exists(dist):
                if os.path.isfile(dist) or os.path.islink(dist):
                    os.remove(dist)
                elif os.path.isdir(dist):
                    shutil.rmtree(dist)
            shutil.move(src, dist)
        os.rmdir(update_folder)