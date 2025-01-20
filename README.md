# FastAPI JWT Authentication Template

Шаблон проекта на **FastAPI** c аутентификацией (JWT), который поможет быстро стартовать разработку веб-приложения. Включает в себя пример структуры папок, базовую конфигурацию, модели пользователей, эндпоинты для регистрации/входа, а также примеры интеграции с базой данных и миграциями.

## Возможности
- Регистрация пользователя
- Аутентификация через **JWT**
- Хэширование паролей (например, с помощью **bcrypt**)
- CRUD (создание, чтение, обновление, удаление) для пользователей
- Структурированный код по принципу «слоистой» архитектуры (routers, services, models, schemas)
- Пример миграций (через Alembic или подобный инструмент)
- Конфигурация окружения через `.env` (Pydantic или python-dotenv)

```bash 

```
# Автор
##  •	Ибрахим Нурберген
##	•	GitHub @nurbergenoovv
##	•	Telegram @nurbergenoovv


```bash 

```

## Требования

- **Python 3.9+** (рекомендуется использовать виртуальное окружение `venv` или Anaconda)
- **FastAPI** (0.70+)
- **Uvicorn** (для запуска сервера)
- **SQLAlchemy** (для работы с БД)
- **Alembic** (для миграций)
- **pyjwt**, **passlib** (или другие библиотеки для JWT и хэширования)
- (опционально) PostgreSQL или любая другая реляционная база данных

## Установка и запуск

1. **Клонировать** репозиторий:
   ```bash
   git clone https://github.com/USERNAME/fastapi-auth-template.git
   cd fastapi-auth-template
   ```
2. Создать виртуальное окружение и активировать его (пример для macOS/Linux):
    ```bash
   python3 -m venv venv
   source venv/bin/activate
    ```
3. **Установить** зависимости
    ```bash
   pip install -r requirements.txt
   ```
4. Создать и настроить файл окружения
    ```bash
   ## Данные PostgrSQL
    DATABASE_HOST=DBHost
    DATABASE_PORT=5432
    DATABASE_USERNAME=DBUsername
    DATABASE_PASSWORD=DBPassword
    DATABASE_NAME=DATABASE
   
    ## Секретный ключ для JWT
    JWT_SECRET_KEY=SECRET_KEY
    
    ## Доменное имя Frontend
    DOMAIN_NAME=example.com
    RESET_PASS_URL=auth/reset-password/

   ## Данные SMTP
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=example@gmail.com
    SMTP_PASSWORD=PasswordGoogleSMTP
    MAIL_STARTTLS=1
    MAIL_SSL_TLS=0
    VALIDATE_CERTS=0
    ```
5.  Выполнить миграции (пример с Alembic)
   ```bash
    alembic upgrade head
   ```
6. Запустить сервер
   ```bash
   uvicorn app.main:app --reload
   ```
   
**Приложение будет доступно на http://127.0.0.1:8000**

##Структура проекта
```bash
app/
├── api/
│   ├── auth.py
│   ├── dependencies.py    # Общие зависимости (зависимости по БД, проверка токена)
│   └── __init__.py
├── db/
│   ├── database.py            # Общие декларативные базовые модели      
│   └── __init__.py
├── models/
│   ├── auth.py            # Модель пользователя
│   └── __init__.py
├── schemas/
│   ├── auth.py            # Pydantic-схемы для логина/регистрации
│   └── __init__.py
├── services/
│   ├── auth.py    # Бизнес-логика авторизации
│   └── __init__.py
├── utils/
│   ├──config.py           # Чтение настроек из .env (Pydantic BaseSettings)
│   └── __init__.py
├── main.py                # Точка входа. Создание FastAPI-приложения и подцепление роутеров
├── requirements.txt
└── README.md
```