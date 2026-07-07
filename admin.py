import json
import os
import subprocess
from pathlib import Path
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
BASE_DIR = Path(__file__).parent
JSON_PATH = BASE_DIR / "content.json"
TEMPLATE_PATH = BASE_DIR / "admin_form.html"

def load_data():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def git_push_changes():
    """Автоматически пушит изменения в репозиторий GitHub"""
    try:
        # Добавляем измененный json в индекс git
        subprocess.run(["git", "add", "content.json"], check=True)
        # Делаем коммит
        subprocess.run(["git", "commit", "-m", "📝 Контент обновлен через админ-панель"], check=True)
        # Пушим в ветку main
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("🚀 Данные успешно отправлены в GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка Git: {e}. Возможно, нет изменений или не настроен удаленный репозиторий.")

@app.route("/")
def index():
    data = load_data()
    success = request.args.get("success", False)
    
    # Читаем HTML шаблон админки
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    return render_template_string(html_content, data=data, success=success)

@app.route("/save", methods=["POST"])
def save():
    # Получаем текущую структуру, чтобы сохранить неизменяемые поля (например, lang или заголовки блоков)
    current_data = load_data()
    
    # Собираем плоские поля из формы
    current_data["meta_title"] = request.form.get("meta_title")
    current_data["meta_description"] = request.form.get("meta_description")
    current_data["hero_title"] = request.form.get("hero_title")
    current_data["hero_subtitle"] = request.form.get("hero_subtitle")
    current_data["about_text"] = request.form.get("about_text")
    current_data["contact_email"] = request.form.get("contact_email")
    current_data["contact_telegram"] = request.form.get("contact_telegram")
    
    # Собираем массив услуг обратно в JSON структуру
    services = []
    for i in range(3):
        name = request.form.get(f"service_name_{i}")
        desc = request.form.get(f"service_desc_{i}")
        if name:  # Добавляем только если заполнено имя услуги
            services.append({"name": name, "desc": desc})
            
    current_data["services"] = services
    
    # Сохраняем в файл
    save_data(current_data)
    
    # Отправляем в GitHub (это активирует ваш GitHub Actions воркфлоу)
    git_push_changes()
    
    return redirect(url_for("index", success=True))

if __name__ == "__main__":
    # Запускаем локальный сервер на порту 5000
    app.run(debug=True, port=5000)
