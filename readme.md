# Телеграм-бот Stomatology_bot
Проект телеграм-бота стоматологии. Проект был выполнен в качестве упражнения для самообучения.

### Технологии:
Приложение разработано на асинхронной библиотеке Aiogram c использованием ORM SQLAlchemy + PostgreSQL.  

![Main page](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/main_page.png)

Бот позволяет просмотреть информацию о стоматологии и оказываемых ею услугах, выбрать подходящего специалиста по интересующей процедуре, 
произвести запись на прием с выбором необходимой даты. Все полученные данные о записи пациента сохраняются в JSON-файл.  

| ![Services](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/services.png) | ![Dentist](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/dentist.png) |
![Reception](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/reception.png)


В проекте также реализована панель администратора, позволяющая редактировать все данные. 

Использован Docker, docker-compose.yml для развертывания инфраструктуры.   

Произведен деплой проекта на VPS-сервер.

### Установка:
Убедитесь, что у Вас установлен Docker:  
``` docker ```   

Если докер отсутствует, установите его в соответствии с официальной документацией - https://docs.docker.com/  

Запустите все сервисы с помощью команды:  
``` docker compose up --build```  

Данная команда запустит бота на вашем ПК.

### Сайт: 
@best_stomatologiya_bot
![qr-code](https://github.com/Oksana-Bachish/bot_stomatology/blob/main/png_for_readme/qr-code.png)

### Автор:
*Оксана Бачиш*
