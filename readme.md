# Телеграм-бот Stomatology_bot
Проект Telegram-бота для стоматологической клиники. Выполнен в качестве учебного проекта для самостоятельного изучения.

### ⚙ Технологии:

- Python (асинхронный фреймворк **Aiogram**)
- ORM: **SQLAlchemy**
- База данных: **PostgreSQL**
- Docker и docker-compose
- Деплой на **VPS** 

### 🚀 Функциональность

- Просмотр информации о клинике и предоставляемых услугах
- Выбор врача по интересующей процедуре
- Онлайн-запись на приём с выбором даты
- Сохранение данных о пациентах в JSON-файл
- Админ-панель для редактирования информации

### 🖼 Скриншоты

![Главная](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/main_page.png)

| Услуги | Врачи | Запись |
|:--:|:--:|:--:|
| ![Услуги](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/services.png) | ![Врачи](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/dentist.png) | ![Запись](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/reception.png) |

Панель администратора:

![Админка](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/admin_pn.png)


### 🛠 Установка и запуск:

1. Откройте терминал и выберите папку, куда Вы будете клонировать Git-репозиторий.  
   ```bash
   cd <имя_папки>
   ```

2. Создайте локальную копию Git-репозитория на Вашем компьютере с помощью команды:   
   ```bash
   git clone https://github.com/Oksana-Bachish/bot_stomatology.git
   ```

3. Перейдите в директорию проекта:  
   ```bash
   cd bot_stomatology
   ```
   
4. Создайте Telegram-бота через [@BotFather](https://t.me/BotFather) и получите токен.  

5. Создайте файл `.env` в корне проекта:
   ```bash
   touch .env
   ```
   
6. Добавьте в `.env` следующие переменные:
   ```env
   TOKEN=your_token
   DB_URL=postgresql+asyncpg://login:password@db_bot:port/db_name
   POSTGRES_DB=db_name
   POSTGRES_PASSWORD=password
   POSTGRES_USER=login
   POSTGRES_PORT=port
   ADMINS=admins_id
   ```

7. Убедитесь, что у вас установлен Docker:
   ```bash
   docker --version
   ```

Если докер отсутствует, установите его в соответствии с официальной документацией - https://docs.docker.com/  

8. Запустите проект:
   ```bash
   docker compose up
   ```
9. После запуска проекта перейдите в созданного Telegram-бота и войдите в панель администратора с помощью команды:
   ```bash
   /admin
   ```
10. Заполните первоначальные данные для корректной работы бота:
   ```
   добавьте баннеры основного меню (banner)
   добавьте специалистов (dentist)
   добавьте изображения услуг (service)
```


После заполнения первоначальных данных бот будет полностью готов к работе.

### 🌐 Сайт

[Перейти к боту в Telegram](https://t.me/best_stomatologiya_bot)  
Или отсканируйте QR-код:

![QR-код](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/qr-code.png)

### 👩‍💻 Автор:
*Оксана Бачиш*  
https://github.com/Oksana-Bachish?tab=repositories
