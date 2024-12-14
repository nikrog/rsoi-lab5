FROM python:3.9

WORKDIR /hotels_booking_system

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]