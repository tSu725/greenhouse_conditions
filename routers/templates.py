import json
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from greenhouse_conditions.config import Config
from greenhouse_conditions.deps.depends import Deps


router = APIRouter(prefix='/templates', tags=["Шаблоны"])

class TemplateSchema(BaseModel):
    name: str = Field(default="template")
    macros_list: list[str]
# Pydantic-модель для тела запроса
class MacrosInput(BaseModel):
    macros_name: str

def get_len_list_templates(data: Dict = Depends(Deps.get_template_data)):
    return len(data)

@router.get('/get_list_templates', summary='Получаем список шаблонов')
def get_list_templates(data: Dict = Depends(Deps.get_template_data)):
    return data

@router.post('/create_template', summary='Создаем новый шаблон')
def create_template(template: TemplateSchema,
                    templates_data: Dict = Depends(Deps.get_template_data),
                    len_templates_data: int = Depends(get_len_list_templates),
                    macros_data: Dict = Depends(Deps.get_macros_data),
):
    # Проверяем, существуют ли макросы
    for macros in template.macros_list:
        if macros not in macros_data:
            raise HTTPException(status_code=400, detail=f"Макрос '{macros}' не найден")
    # Создаём новый шаблон
    new_template_name = template.name if template.name != 'template' else f"template_{len_templates_data}"
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
def add_macros(template_name: str,
               macros: MacrosInput,
               templates_data: Dict = Depends(Deps.get_template_data),
               macros_data: Dict = Depends(Deps.get_macros_data)
               ):
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
def delete_macros_from_template(template_name: str,
                                macros: MacrosInput,
                                data: Dict = Depends(Deps.get_template_data)
):

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
def delete_template(template_name: str,
                    templates_data: Dict = Depends(Deps.get_template_data)):
    # Проверяем, существует ли шаблон
    if template_name not in templates_data:
        raise HTTPException(status_code=404, detail=f"Шаблон '{template_name}' не найден.")
    # Удаляем шаблон
    del templates_data[template_name]
    # Записываем обновленные данные обратно в файл
    with open(Config.TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates_data, f, indent=4, ensure_ascii=False)
    return {"message": f"Шаблон '{template_name}' успешно удалён."}
