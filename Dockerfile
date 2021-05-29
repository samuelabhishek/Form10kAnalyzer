FROM python:3.9

WORKDIR /marketintelligence

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_lg

COPY ./src ./src

COPY ./documentRepo ./documentRepo

CMD ["python", "./src/program.py"]