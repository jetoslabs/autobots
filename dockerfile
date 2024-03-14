FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

RUN apt-get upgrade
RUN apt-get update
RUN apt-get install firefox-esr -y

RUN pip install poetry

WORKDIR /home/jetoslabs/autobots

COPY ./pyproject.toml ./poetry.lock ./README.md ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY ./src/autobots ./src/autobots

## DataDog setup
ARG DD_ENV=default
ENV DD_ENV=$DD_ENV
ARG DD_VERSION=default
ENV DD_VERSION=$DD_VERSION

ENV DD_SERVICE=autobots
# DD_AGENT_HOST should match datadog-agent container name
ENV DD_AGENT_HOST=datadog-agent
ENV DD_TRACE_AGENT_PORT=8126

LABEL "com.datadoghq.ad.check_names"='["autobots"]'
LABEL "com.datadoghq.ad.init_configs"='[{}]'
LABEL "com.datadoghq.ad.instances"='[{"autobots_status_url": "https://%%host%%:%%port%%/v1/hello"}]'
LABEL "com.datadoghq.ad.logs"='[{"source": "autobots", "service": "autobots"}]'
##

ENTRYPOINT ["uvicorn", "--loop", "asyncio", "src.autobots.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "3", "--lifespan", "on"]