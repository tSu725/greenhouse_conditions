from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Union
import json



MACROS_FILE = "macros.json"

router = APIRouter(prefix='/macros', tags=["Макросы"])

# Функция для получения количества макросов в файле
def get_macros_filename_length():
    try:
        with open(MACROS_FILE, 'r', encoding='utf-8') as f:
            file = json.load(f)
            return len(file)
    except FileNotFoundError:
        return 0

class Macros(BaseModel):
    name: str = Field(default="macros")
    key: str
    value: Union[int, float]

@router.post('/create_macros', summary='Создаем новый макрос')
def create_macros(macros: Macros):
    # Считываем текущие макросы
    try:
        with open(MACROS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    new_macro = {
        'key': macros.key,
        'value': macros.value
    }
    # Добавляем новый макрос в словарь
    data[macros.name if macros.name != "macros" else f'macros_{len(data)}'] = new_macro

    # Записываем обновленный словарь обратно в файл
    with open('macros.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return {"message": "Макрос добавлен", "macro": new_macro}

@router.get('/get_list_macros', summary='Получаем все макросы')
def get_list_macros():
    with open(MACROS_FILE, 'r', encoding='utf-8') as file:
        file = json.load(file)
        return file

# @router.delete('/delete_macros')
# def delete_macros(name: Macros.name):



