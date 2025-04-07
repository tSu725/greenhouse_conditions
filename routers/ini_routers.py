import os
import json
import configparser
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from greenhouse_conditions.config import Config
from greenhouse_conditions.deps.depends import Deps

router = APIRouter(prefix="/ini", tags=["Манипуляции с ini"])

# Нормализация пути (удаление дублирующихся слэшей)
@router.post("/set_ini_path/{path}", summary="Устанавливаем путь до файла конфигураций")
def set_ini_path(path: str):
    try:
        with open(Config.CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Файл конфигурации отсутствует или поврежден")
    data["ini_path"] = Deps.normalize_path(path)
    with open(Config.CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return {"ok": True}
@router.get("/parse_ini", summary="Парсим INI-файл и возвращаем данные")
def parse_ini():
    try:
        with open(Config.CONFIG_FILE, "r", encoding="utf-8") as config:
            data = json.load(config)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Файл конфигурации отсутствует или поврежден")

    ini_path = Deps.normalize_path(data.get("ini_path", ""))
    if not ini_path or not os.path.isfile(ini_path):
        raise HTTPException(status_code=400, detail="INI-файл не найден или путь указывает на папку")
    config = configparser.ConfigParser()
    config.read(ini_path, encoding="utf-8")
    ini_dict = {section: dict(config.items(section)) for section in config.sections()}
    return ini_dict
@router.post("/write_to_ini", summary="Вносим изменения в INI из макроса")

def write_macros_to_ini(
        macro_name: str,
        ini_path: str = Depends(Deps.get_ini_path),
        macros_data: Dict = Depends(Deps.get_macros_data)
):
    section = "general"
    macro = macros_data[macro_name]
    Deps.write_macro_to_ini(ini_path, section, macro)
    return {"message": f"Макрос '{macro_name}' успешно добавлен в {ini_path}"}

@router.post("/write_to_ini_from_template", summary="Вносим изменения в INI из шаблона")
def write_macros_to_ini_from_template(
        template: str,
        template_entry: Dict = Depends(Deps.get_template_entry),
        macros_data: Dict = Depends(Deps.get_macros_data),
        ini_path: str = Depends(Deps.get_ini_path)
):
    # Применяем макросы для каждого макроса в шаблоне
    section = "general"
    for macro_name in template_entry["value"]:
        if macro_name not in macros_data:
            raise HTTPException(status_code=400, detail=f"Макрос '{macro_name}' из шаблона не найден")
        macro = macros_data[macro_name]
        # Используем вспомогательную функцию для записи макроса в INI
        Deps.write_macro_to_ini(ini_path, section, macro)
    return {"message": f"Шаблон '{template}' успешно применён к {ini_path}"}