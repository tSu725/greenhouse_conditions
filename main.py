import os
import json
import uvicorn
from fastapi import FastAPI
from routers.ini_routers import router as ini_router
from routers.macros import router as macros_router

CONFIG_FILE = "settings.config"
MACROS_FILE = "macros.json"

app = FastAPI()

app.include_router(ini_router)
app.include_router(macros_router)

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




if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
