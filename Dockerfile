FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt . 
    #Copy req.txt into WD (/app)
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    #uses command uvicorn, which looks in main.py for app
    #--host 0.0.0.0 makes sure app listens outside of container