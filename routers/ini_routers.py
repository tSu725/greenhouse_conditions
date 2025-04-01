import os
import json
import re
import configparser
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/ini", tags=["Манипуляции с ini"])

CONFIG_FILE = "settings.config"

# Нормализация пути (удаление дублирующихся слэшей)
def normalize_path(path: str) -> str:
    return re.sub(r"\\+", r"\\", path)


@router.post("/set_ini_path/{path}", summary="Устанавливаем путь до файла конфигураций")
def set_ini_path(path: str):
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Файл конфигурации отсутствует или поврежден")

    data["ini_path"] = path
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return {"ok": True}


@router.get("/parse_ini", summary="Парсим INI-файл и возвращаем данные")
def parse_ini():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as config:
            data = json.load(config)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Файл конфигурации отсутствует или поврежден")

    ini_path = normalize_path(data.get("ini_path", ""))
    if not ini_path or not os.path.isfile(ini_path):
        raise HTTPException(status_code=400, detail="INI-файл не найден или путь указывает на папку")

    with open(ini_path, "r", encoding="utf-8") as ini_file:
        ini_content = ini_file.read()

    config = configparser.ConfigParser()
    config.read_string(ini_content)

    ini_dict = {section: dict(config.items(section)) for section in config.sections()}
    return ini_dict
