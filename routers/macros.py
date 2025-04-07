from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Union, Dict
import json
from greenhouse_conditions.config import Config
from greenhouse_conditions.deps.depends import Deps

router = APIRouter(prefix='/macros', tags=["Макросы"])



class MacrosSchema(BaseModel):
    name: str = Field(default="macros")
    key: str
    value: Union[int, float]
# Функция для получения количества макросов в файле
def get_macros_filename_length(data: Dict = Depends(Deps.get_macros_data)):
    return len(data)
@router.get('/get_list_macros', summary='Получаем список макросов')
def get_list_macros(data: Dict = Depends(Deps.get_macros_data)):
    return data
@router.post('/create_macros', summary='Создаем новый макрос')
def create_macros(macros: MacrosSchema,
                  data: Dict = Depends(Deps.get_macros_data)
):
    new_macro = {
        'key': macros.key,
        'value': macros.value
    }
    data[macros.name if macros.name != "macros" else f'macros_{len(data)}'] = new_macro
    with open(Config.MACROS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return {"message": "Макрос добавлен", "macro": new_macro}
@router.delete('/delete_macros/{macros_name}', summary='Удалить макрос')
def delete_macros(
    macros_name: str,
    data: Dict = Depends(Deps.get_macros_data)  # Получаем данные макросов
):
    if not Deps.check_macro(macros_name, macros_data=data):  # Передаем данные через Depends
        raise HTTPException(status_code=404, detail=f"Макрос '{macros_name}' не найден")
    # Если макрос найден, удалить его
    del data[macros_name]
    with open(Config.MACROS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return {"message": f"Макрос '{macros_name}' успешно удалён"}
