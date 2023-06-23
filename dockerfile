FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

RUN pip install poetry

WORKDIR /home/jetoslabs/autobots

COPY ./pyproject.toml ./poetry.lock ./README.md ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY ./autobots ./autobots


LABEL "com.datadoghq.ad.check_names"='["autobots"]'
LABEL "com.datadoghq.ad.init_configs"='[{}]'
LABEL "com.datadoghq.ad.instances"='[{"autobots_status_url": "https://%%host%%:%%port%%/v1/hello"}]'
LABEL "com.datadoghq.ad.logs"='[{"source": "autobots", "service": "autobots"}]'


ENTRYPOINT ["uvicorn", "autobots.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "20", "--lifespan", "on"]