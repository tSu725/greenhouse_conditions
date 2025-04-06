import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from greenhouse_conditions.config import Config


router = APIRouter(prefix='/templates', tags=["Шаблоны"])

class TemplateSchema(BaseModel):
    name: str = Field(default="template")
    macros_list: list[str]

# Pydantic-модель для тела запроса
class MacrosInput(BaseModel):
    macros_name: str

@router.get('/get_list_templates', summary='Получаем список шаблонов')
def get_list_templates():
    with open(Config.TEMPLATES_FILE, 'r', encoding='utf-8') as f:
        file = json.load(f)
        return file

@router.post('/create_template', summary='Создаем новый шаблон')
def create_template(template: TemplateSchema):
    # Загружаем список шаблонов
    try:
        with open(Config.TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            templates_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        templates_data = {}
    # Загружаем список макросов
    try:
        with open(Config.MACROS_FILE, 'r', encoding='utf-8') as f:
            macros_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        macros_data = {}
    # Проверяем, существуют ли макросы
    for macros in template.macros_list:
        if macros not in macros_data:
            raise HTTPException(status_code=400, detail=f"Макрос '{macros}' не найден")
    # Создаём новый шаблон
    new_template_name = template.name if template.name != 'template' else f"template_{len(templates_data)}"
    new_template = {
        'key': new_template_name,
        'value': template.macros_list
    }
    templates_data[new_template_name] = new_template

    # Записываем обновлённые данные в файл
    with open(Config.TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates_data, f, indent=4, ensure_ascii=False)
    return {"message": "Шаблон добавлен", "template": new_template}
@router.post('/add_macros/{template_name}', summary='Добавляем макрос в шаблон')
def add_macros(template_name: str, macros: MacrosInput):
    try:
        with open(Config.TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            templates_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Файл шаблонов {Config.TEMPLATES_FILE} не найден")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка при чтении JSON-файла")

    try:
        with open(Config.MACROS_FILE, 'r', encoding='utf-8') as f:
            macros_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Файл макросов {Config.MACROS_FILE} не найден")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка при чтении JSON-файла")

    # Проверяем, есть ли шаблон
    if template_name not in templates_data:
        raise HTTPException(status_code=404, detail=f"Шаблон '{template_name}' не найден.")

    # Проверяем, существует ли макрос
    if macros.macros_name not in macros_data:
        raise HTTPException(status_code=404, detail=f"Макрос '{macros.macros_name}' не найден.")

    # Проверяем, есть ли уже этот макрос в шаблоне
    if macros.macros_name in templates_data[template_name]["value"]:
        raise HTTPException(status_code=400, detail=f"Макрос '{macros.macros_name}' уже существует в шаблоне '{template_name}'.")

    # Добавляем макрос в шаблон
    templates_data[template_name]["value"].append(macros.macros_name)

    # Записываем обновленные данные обратно в файл
    with open(Config.TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates_data, f, indent=4, ensure_ascii=False)

    return {"message": f"Макрос '{macros.macros_name}' добавлен в шаблон '{template_name}'."}
@router.delete('/delete_macros/{template_name}', summary='Удаляем макрос из шаблона')
def delete_macros_from_template(template_name: str, macros: MacrosInput):
    try:
        with open(Config.TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл шаблонов не найден")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка при чтении JSON-файла")

    if template_name not in data:
        raise HTTPException(status_code=404, detail=f"Шаблон '{template_name}' не найден")

    if "value" not in data[template_name]:
        raise HTTPException(status_code=400, detail=f"Шаблон '{template_name}' не содержит макросов")

    # Удаляем макрос, если он есть
    if macros.macros_name in data[template_name]["value"]:
        data[template_name]["value"].remove(macros.macros_name)
    else:
        raise HTTPException(status_code=404, detail=f"Макрос '{macros.macros_name}' не найден в шаблоне {template_name}")

    # Если в шаблоне больше нет макросов, удаляем шаблон
    if not data[template_name]["value"]:
        del data[template_name]

    # Записываем обновлённые данные в файл
    with open(Config.TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return {"message": "Макрос удалён", "template": data}
@router.delete('/delete_template/{template_name}', summary='Удалить шаблон')
def delete_template(template_name: str):
    try:
        with open(Config.TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            templates_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Файл шаблонов {Config.TEMPLATES_FILE} не найден")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка при чтении JSON-файла")

    # Проверяем, существует ли шаблон
    if template_name not in templates_data:
        raise HTTPException(status_code=404, detail=f"Шаблон '{template_name}' не найден.")

    # Удаляем шаблон
    del templates_data[template_name]

    # Записываем обновленные данные обратно в файл
    with open(Config.TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates_data, f, indent=4, ensure_ascii=False)

    return {"message": f"Шаблон '{template_name}' успешно удалён."}
