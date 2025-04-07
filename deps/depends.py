from fastapi import Depends, HTTPException
from typing import Dict
import json, os, configparser
from greenhouse_conditions.config import Config

class Deps:
    @staticmethod
    def normalize_path(path: str) -> str:
        return os.path.normpath(path)

    @staticmethod
    def get_macros_data() -> Dict:
        try:
            with open(Config.MACROS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Файл {Config.MACROS_FILE} не найден")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Ошибка при чтении JSON-файла")

    @staticmethod
    def get_config_data() -> Dict:
        try:
            with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Файл {Config.CONFIG_FILE} не найден")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Ошибка при чтении JSON-файла")

    @staticmethod
    def get_ini_path(config_data: Dict = Depends(get_config_data)) -> str:
        ini_path = Deps.normalize_path(config_data.get("ini_path"))
        if not ini_path or not os.path.isfile(ini_path):
            raise HTTPException(status_code=400, detail="Некорректный путь к INI-файлу")
        return ini_path

    # @staticmethod
    # def get_macro_entry(macro: str, macros_data: Dict = Depends(get_macros_data)) -> Dict:
    #     if macro not in macros_data:
    #         raise HTTPException(status_code=400, detail=f"Макрос '{macro}' не найден")
    #     return macros_data[macro]['key']

    @staticmethod
    def check_macro(macro: str, macros_data: Dict = Depends(get_macros_data)) -> bool:
        if macro not in macros_data:
            return False
        return True

    @staticmethod
    def get_template_data() -> Dict:
        try:
            with open(Config.TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Файл {Config.TEMPLATES_FILE} не найден")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Ошибка при чтении JSON-файла")

    @staticmethod
    def get_template_entry(template: str, template_data: Dict = Depends(get_template_data)) -> Dict:
        if template not in template_data:
            raise HTTPException(status_code=400, detail=f"Шаблон '{template}' не найден")
        return template_data[template]

    @staticmethod
    def write_macro_to_ini(ini_path: str, section: str, macro_entry: Dict):
        config = configparser.ConfigParser()
        config.read(ini_path, encoding='utf-8')
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, macro_entry["key"], str(macro_entry["value"]))
        with open(ini_path, "w", encoding="utf-8") as f:
            config.write(f)

