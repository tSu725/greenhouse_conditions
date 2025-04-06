import os
import json
import uvicorn
from fastapi import FastAPI
from routers.ini_routers import router as ini_router
from routers.macros import router as macros_router
from routers.templates import router as templates_router
from config import Config

app = FastAPI()

app.include_router(ini_router)
app.include_router(macros_router)
app.include_router(templates_router)

# Инициализация файлов (если их нет)
def init_files():
    if not os.path.exists(Config.CONFIG_FILE):
        config_data = {"ini_path": None}
        with open(Config.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print(f"Создан файл конфигурации: {Config.CONFIG_FILE}")
    if not os.path.exists(Config.MACROS_FILE):
        with open(Config.MACROS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
        print(f"Создан файл макросов: {Config.MACROS_FILE}")
    if not os.path.exists(Config.TEMPLATES_FILE):
        with open(Config.TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
        print(f"Создан файл шаблонов: {Config.TEMPLATES_FILE}")
if __name__ == "__main__":
    init_files()
    uvicorn.run("main:app", reload=True)
