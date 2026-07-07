import json
from pathlib import Path
from string import Template

def build_site():
    # Определение путей (работает корректно при запуске из любого места)
    base_dir = Path(__file__).parent
    public_dir = base_dir / "public"
    public_dir.mkdir(exist_ok=True)
    
    # 1. Загрузка данных из JSON
    with open(base_dir / "content.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 2. Загрузка HTML шаблона
    with open(base_dir / "template.html", "r", encoding="utf-8") as f:
        template_content = f.read()
        
    # 3. Динамическая генерация HTML для списка услуг
    services_list = []
    for s in data.get("services", []):
        card = f'''
        <div class="card">
            <h3>{s["name"]}</h3>
            <p>{s["desc"]}</p>
        </div>'''
        services_list.append(card)
    data["services_html"] = "\n".join(services_list)
    
    # 4. Динамическая генерация валидного JSON-LD для локального SEO
    schema_data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": data.get("og_site_name"),
        "description": data.get("meta_description"),
        "email": data.get("contact_email"),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Tbilisi",
            "addressCountry": "GE"
        }
    }
    # Превращаем в строку с отступами для красоты кода страницы
    data["schema_json"] = json.dumps(schema_data, ensure_ascii=False, indent=2)
    
    # 5. Сборка страницы через безопасный шаблонизатор string.Template
    template = Template(template_content)
    final_html = template.safe_substitute(data)
    
    # 6. Запись готового файла в целевую директорию
    output_path = public_dir / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"🎉 Сайт успешно сгенерирован в: {output_path.resolve()}")

if __name__ == "__main__":
    build_site()
