FROM python:3.10-slim as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1

# Install pipenv and compilation dependencies
RUN python3 -m pip install wheel pip --upgrade && pip install pipenv
RUN apt-get update && apt-get install

COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --system

# Create and switch to a new user to ensure security
RUN useradd --create-home appuser
WORKDIR /home/appuser
RUN mkdir -p /home/appuser/mzId_convertor_temp
RUN mkdir -p /home/appuser/logs
USER appuser

# Install application into container
COPY app ./app
COPY dbs ./dbs
COPY log ./log
COPY logs ./logs
COPY obo ./obo
COPY parser ./parser
COPY tests ./tests
COPY *.py .
COPY default.database.ini .
COPY logging.ini .
COPY .kubernetes.yml .

#CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "6000"]