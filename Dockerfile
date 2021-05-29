FROM python:3.9

WORKDIR /code

COPY requirements.txt .

COPY environment.yml .

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_lg

COPY src/ .

CMD ["python", "program.py"]