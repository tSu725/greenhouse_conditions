import os
import json
import re
import configparser
import uvicorn
from fastapi import FastAPI, HTTPException

CONFIG_FILE = "settings.config"
MACROS_FILE = "macros.json"

app = FastAPI()

# Инициализация файлов (если их нет)
def init_files():
    if not os.path.exists(CONFIG_FILE):
        config_data = {"macros_path": MACROS_FILE, "ini_path": None}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print(f"Создан файл конфигурации: {CONFIG_FILE}")

    if not os.path.exists(MACROS_FILE):
        with open(MACROS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
        print(f"Создан файл макросов: {MACROS_FILE}")

init_files()

# Нормализация пути (удаление дублирующихся слэшей)
def normalize_path(path: str) -> str:
    return re.sub(r'\\+', r'\\', path)

@app.post('/set_ini_path/{path}', summary='Устанавливаем путь до файла конфигураций')
def set_ini_path(path: str):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Файл конфигурации отсутствует или поврежден")
    data['ini_path'] = path
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return {'ok': True}
@app.get('/parse_ini', summary='Парсим INI-файл и возвращаем данные')
def parse_ini():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as config:
            data = json.load(config)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Файл конфигурации отсутствует или поврежден")
    ini_path = normalize_path(data.get('ini_path', ''))
    if not ini_path or not os.path.isfile(ini_path):
        raise HTTPException(status_code=400, detail="INI-файл не найден или путь указывает на папку")
    with open(ini_path, 'r', encoding='utf-8') as ini_file:
        ini_content = ini_file.read()
    config = configparser.ConfigParser()
    config.read_string(ini_content)
    ini_dict = {section: dict(config.items(section)) for section in config.sections()}
    return ini_dict



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
