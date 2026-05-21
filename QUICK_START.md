# ⚡ БЫСТРАЯ ШПАРГАЛКА — РАЗВЕРТЫВАНИЕ ЗА 10 МИНУТ

## 🚀 СУПЕР БЫСТРО (5 минут)

### 1️⃣ Скопируйте токен БОТ_ТОКЕН и сохраните его отдельно!

```
BOT_TOKEN = ваш_токен_123456:ABCDEF...
FLASK_SECRET_KEY = любая_долгая_строка_12345
```

### 2️⃣ Git

```bash
cd "C:\Users\22722\Desktop\Lovio\финалочка"

git init
git add .
git commit -m "Deploy"

# Создайте репозиторий на GitHub.com
# Потом:

git remote add origin https://github.com/USERNAME/couple-tracker.git
git push -u origin main
```

### 3️⃣ Render.com

1. Откройте https://render.com
2. Нажмите "Sign up with GitHub"
3. "New Web Service"
4. Выберите ваш репозиторий
5. **Настройки:**
   - Name: `couple-tracker`
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
   - Instance: Free

6. **Переменные (Environment):**
   - `BOT_TOKEN` = ваш_токен
   - `FLASK_SECRET_KEY` = любая_строка

7. Нажмите "Create Web Service"

### 4️⃣ Ждём 10 минут и готово! 🎉

Ссылка: `https://couple-tracker.onrender.com`

---

## 🔄 ОБНОВЛЕНИЯ

Каждый раз:

```bash
git add .
git commit -m "Описание изменения"
git push
# Render автоматически обновит приложение
```

---

## 📝 ЛОКАЛЬНАЯ РАЗРАБОТКА

Если хотите тестировать локально:

```bash
# Установите зависимости
pip install -r requirements.txt

# Установите переменные (Windows)
set BOT_TOKEN=ваш_токен
set FLASK_SECRET_KEY=секретный_ключ

# Запустите
python app.py

# Откройте браузер
http://localhost:5000
```

---

## ⚠️ ВАЖНО

- ✅ Токен БОТ_ТОКЕН нигде не должен быть в коде!
- ✅ Используйте ТОЛЬКО переменные окружения
- ✅ `.env` файл в `.gitignore`
- ✅ На Render добавляйте переменные через панель "Environment"

---

## 🆘 ЕСЛИ НЕ РАБОТАЕТ

### Ошибка "Failed to deploy"

Проверьте:
1. Все ли файлы загружены в GitHub?
2. requirements.txt есть?
3. Procfile правильный?

### Ошибка при входе

Проверьте переменные окружения на Render:
```
Settings → Environment Variables
```

### Медленно загружается

Это нормально для Free плана на Render. Платный план: от $7/месяц.

---

## 📞 ÚTIL LINKS

- Render: https://render.com
- GitHub: https://github.com
- Flask: https://flask.palletsprojects.com
- Телеграм бот: https://t.me/BotFather

---

**Все готово к запуску!** 🚀💕
