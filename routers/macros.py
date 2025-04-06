from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Union, Dict
import json
from greenhouse_conditions.config import Config
from greenhouse_conditions.deps.depends import Deps

router = APIRouter(prefix='/macros', tags=["Макросы"])

# Функция для получения количества макросов в файле
def get_macros_filename_length():
    try:
        with open(Config.MACROS_FILE, 'r', encoding='utf-8') as f:
            file = json.load(f)
            return len(file)
    except FileNotFoundError:
        return 0


class MacrosSchema(BaseModel):
    name: str = Field(default="macros")
    key: str
    value: Union[int, float]


@router.post('/create_macros', summary='Создаем новый макрос')
def create_macros(macros: MacrosSchema):
    # Считываем текущие макросы
    data = Deps.get_macros_data()
    new_macro = {
        'key': macros.key,
        'value': macros.value
    }
    # Добавляем новый макрос в словарь
    data[macros.name if macros.name != "macros" else f'macros_{len(data)}'] = new_macro
    # Записываем обновленный словарь обратно в файл
    with open(Config.MACROS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return {"message": "Макрос добавлен", "macro": new_macro}
@router.get('/get_list_macros', summary='Получаем список макросов')
def get_list_macros():
    data = Deps.get_macros_data()
    return data


@router.delete('/delete_macros/{macros_name}', summary='Удалить макрос')
def delete_macros(macros_name: str, data: Dict = Deps.get_macros_data()):
    macros_entry = Deps.get_macro_entry(macros_name)['key']
    del data[macros_entry]  # Удаляем макрос
    with open(Config.MACROS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return {"message": f"Макрос '{macros_name}' успешно удалён"}


# @router.delete('/delete_macros/{macros_name}', summary='Удалить макрос')
# def delete_macros(macros_name: str):
#
#
#     data = Deps.get_macros_data()
#     name = macros_name
#     try:
#         # Читаем текущие макросы
#         with open(Config.MACROS_FILE, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#         # Проверяем, существует ли макрос
#         if name in data:
#             del data[name]  # Удаляем макрос
#             # Записываем обновлённые данные обратно в файл
#             with open(Config.MACROS_FILE, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, ensure_ascii=False, indent=4)
#             return {"message": f"Макрос '{name}' успешно удалён"}
#         else:
#             raise HTTPException(status_code=404, detail=f"Макрос '{name}' не найден")
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="Файл макросов не найден")
#     except json.JSONDecodeError:
#         raise HTTPException(status_code=500, detail="Ошибка при чтении JSON-файла")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))





