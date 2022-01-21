import json
import os
from datetime import datetime


class ConfigManager:
    def __init__(self):
        self.fb_username = None
        self.fb_password = None
        self.fb_page_name = None
        self.output_filename = None
        self.output_post_filename_prefix = None
        self.amount_posts = None
        self.gecko_binary = None
        self.load_config_data()

    def load_config_data(self):
        with open("config.json", "r") as config_file:
            filecontents = json.load(config_file)
            fbSection = filecontents["facebook"][0]
            self.fb_username = fbSection["user"]
            self.fb_password = fbSection["password"]
            self.amount_posts = fbSection["amount_posts"]
            self.fb_page_name = fbSection["page_name"]

            fsWebDriver = filecontents["WebDriver"][0]
            self.gecko_binary = fsWebDriver["gecko_binary"]

            fsSection = filecontents["FileStorageConfig"][0]
            self.base_path = fsSection["base_path"]
            input_filename_prefix = fsSection["input_filename"]
            self.input_filename = os.path.join(self.base_path, input_filename_prefix)
            output_filename_prefix = fsSection["output_filename"]
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_filename_prefix + "_" + current_date + ".csv"
            self.output_filename = os.path.join(self.base_path, filename)
            self.output_post_filename_prefix = fsSection["output_post_filename"]
