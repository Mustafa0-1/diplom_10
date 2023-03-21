FROM python:3.10.9-slim as base_image

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.3.2

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /tmp

COPY poetry.lock pyproject.toml ./

RUN poetry export --without dev,test -f requirements.txt -o requirements.prod.txt && \
    poetry export --with dev,test -f  requirements.txt -o requirements.dev.txt && \
    rm poetry.lock pyproject.toml && \
    pip uninstall poetry -y

WORKDIR /opt

COPY . .

EXPOSE 8000

ENTRYPOINT ["bash", "entrypoint.sh"]


FROM base_image as prod_image

RUN pip install -r /tmp/requirements.prod.txt
CMD ["gunicorn", "todolist.wsgi", "-w", "4", "-b", "0.0.0.0:8000"]

FROM base_image as dev_image

RUN pip install -r /tmp/requirements.dev.txt
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
