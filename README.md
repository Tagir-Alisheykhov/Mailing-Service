# 📨 Mail — Сервис email-рассылок

> Удобный и функциональный сервис рассылки электронных писем с поддержкой кастомной аутентификации, верификации email, управления получателями и расписанием рассылок.

[![Django](https://img.shields.io/badge/Django-3.2.18-blue?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

---

## 🧾 Описание 

**OpusMail** — это веб-приложение на базе **Django**, позволяющее:
- Создавать, управлять и отслеживать email-рассылки
- Добавлять сообщения и получателей
- Планировать отправку по времени
- Отслеживать статусы и историю отправок

Проект разработан с акцентом на безопасность, удобство использования и масштабируемость.

---

## 🚀 Функционал

| Категория        | Возможности |
|------------------|-------------|
| 🔐 Аутентификация | Регистрация, вход, восстановление пароля, верификация email |
| ✉️ Сообщения      | Создание, редактирование, черновики, отправка |
| 📣 Рассылки       | Расписание, фильтрация по статусу, история попыток |
| 📥 Получатели     | Добавление, удаление, комментарии |
| 📊 Статистика     | Подсчёт активных рассылок, уникальных получателей |
| 💾 Кэширование    | Redis для ускорения работы |

---

## 🛠 Технологии

- 🐍 **Python 3.11+**
- 🌐 **Django 5.2.2**
- 🗄️ **PostgreSQL**
- 🧠 **Redis** (кэширование)
- 📨 **SMTP** (для отправки email)
- 🎨 **Bootstrap 5.3**
- 🧱 **HTML / CSS**

---

## 🧰 Установка

### 1. Клонируй репозиторий
```commandline
git clone https://github.com/yourname/opusmail.git
``` 
```commandline
cd Mailing-Service
```

### 2. Настройка виртуального окружения
```bash
python -m venv venv
```
```bash
source venv/bin/activate  # Linux/Mac
```
```bash
venv\Scripts\activate     # Windows
```
```bash
pip install -r requirements.txt
```

### 3. Настройка .env
Создайте файл .env в корне проекта:
```bash
cp .env.example .env
```
- `DJANGO_SECRET_KEY` = 'django-project-secret-key'
- `DEBUG` = 'True/False'
- `DB_NAME` = 'your_db_name'
- `DB_USER` = 'your_db_user'
- `DB_PASSWORD` = 'your_db_password'
- `DB_HOST` = 'your_db_host' (for example 'localhost')
- `DB_PORT` = 'your_db_port' (for example '5432')
- `EMAIL_HOST` = 'your_host' (for example 'smtp.yandex.ru')
- `EMAIL_PORT` = 'your_port' (for example '465')
- `EMAIL_HOST_USER` = 'sender`s email'
- `EMAIL_HOST_PASSWORD` = 'your_pass'
- `SUPERUSER_FIRST_NAME`=Python
- `SUPERUSER_LAST_NAME`=Anakondovich
- `SUPERUSER_PASSWORD`='your_password'
- `SUPERUSER_EMAIL`='superuser_email'

### 4. Миграции
-- Выполните миграцию в базу данных
```bash
python manage.py migrate
```

### 5. Запуск сервера
```bash
python manage.py runserver
```
-- После успешного запуска откройте: http://localhost:8000


### 📦 Возможные доработки проекта
- ✅ Интеграция Celery
- ✅ Графики статистики
- ✅ API (DRF)
- ✅ Поддержка i18n
- ✅ Email-уведомления

### 📄 Лицензия
- MIT License © 2025
