from fastapi import FastAPI, HTTPException
import openai
import requests
import os
from dotenv import load_dotenv
import uvicorn

# Загрузка переменных окружения
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY")

# Инициализация FastAPI
app = FastAPI()

# Конфигурация OpenAI API
openai.api_key = OPENAI_API_KEY

# Функция для получения новостей по теме
def get_news(topic: str):
    url = f"https://api.currentsapi.services/v1/latest-news?keywords={topic}&apiKey={CURRENTS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("news", [])
        return "\n".join([article["title"] for article in articles[:3]])  # Берем три заголовка
    else:
        return ""

# Функция генерации блог-поста с учетом новостей
def generate_post(topic: str):
    news_context = get_news(topic)
    prompt = f"Напишите подробный пост для блога на тему: {topic}. Вот несколько актуальных новостей по теме: {news_context}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Эндпоинт для генерации поста
@app.get("/generate/")
def generate(topic: str):
    if not topic:
        raise HTTPException(status_code=400, detail="Тема не может быть пустой")
    return {"topic": topic, "post": generate_post(topic)}

# Эндпоинт для проверки работоспособности
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
