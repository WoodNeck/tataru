import os
import configparser

class BotConfig:
    def __init__(self):
        self.configPath = "config.ini"
        self.config = configparser.ConfigParser()
        if os.path.isfile(self.configPath):
            configFile = open(self.configPath, "r")
            self.config.read_file(configFile)
    
    def add(self, section, key, value):
        if section not in self.config:
            self.config.add_section(section)
        self.config[section][key] = value

    def request(self, section, key):
        if self.exist(section, key):
            return self.get(section, key)
        else:
            value = input("{}의 {}을(를) 입력해주세요: ".format(section, key))
            self.add(section, key, value)
            return value
    
    def save(self):
        with open(self.configPath, 'w') as f:
            self.config.write(f)
    
    def exist(self, section, key):
        if section in self.config:
            target = self.config[section]
            return key in target
        else:
            return False
    
    def get(self, section, key):
        if section in self.config:
            return self.config.get(section, key)
        else:
            return None