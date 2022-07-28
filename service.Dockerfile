FROM python:3.6.9

#
WORKDIR /code

#
COPY ./service.requirements.txt /code/requirements.txt
COPY ./main.py /code/main.py

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]