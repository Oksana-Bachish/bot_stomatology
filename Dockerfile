FROM python:3.10-slim

RUN useradd -s /bin/sh -u 1234 nonroot

WORKDIR /usr/src/tg_bot_stoma

RUN apt-get update && apt-get install -y locales &&  \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales &&  \
    apt-get install -y libpq-dev build-essential &&  \
    apt-get install -y netcat-openbsd

RUN pip install --no-cache-dir uv

ENV PYTHONUNBUFFERED=1
ENV LANG ru_RU.UTF-8
ENV LC_ALL ru_RU.UTF-8

COPY pyproject.toml .

RUN uv pip install --system --no-cache -e ".[dev]"

COPY . .

RUN sed -i 's/\r$//g' /usr/src/tg_bot_stoma/entrypoint.sh  # настройка для windows перенос каретки
RUN chmod +x /usr/src/tg_bot_stoma/entrypoint.sh  # добавляем флаг -x(разрешение запуска)

RUN chown -R nonroot:nonroot /usr/src/tg_bot_stoma
USER nonroot

ENTRYPOINT [ "./entrypoint.sh" ]

CMD ["python", "app.py"]
