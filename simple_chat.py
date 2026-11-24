"""
Najjednostavniji primjer razgovora sa LLM-om kroz FastAPI i Swagger.

Pokretanje:
    python simple_chat.py

Ili preko Uvicorn CLI komande:
    uvicorn simple_chat:app --reload --port 8017

Swagger:
    http://localhost:8017/docs
"""

import os

import uvicorn
from dotenv import load_dotenv
from fastapi import Body, FastAPI
from openai import AsyncOpenAI


# Učitava varijable iz .env fajla u okruženje aplikacije.
load_dotenv()

# FastAPI automatski pravi Swagger dokumentaciju na putanji /docs.
app = FastAPI(
    title="Najjednostavniji AI Chat",
    description="Uvodni primjer: jedna korisnička poruka ide direktno LLM-u.",
)

# Ako postoji DeepSeek ključ, koristimo DeepSeek.
# U suprotnom koristimo lokalni Ollama server.
api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()

if api_key and api_key != "sk-vas-kljuc-ovdje":
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
    )
    model = "deepseek-chat"
else:
    client = AsyncOpenAI(
        api_key="ollama",
        base_url=f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/v1",
    )
    model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")


# POST /chat prima JSON oblika: {"poruka": "Tekst pitanja"}
@app.post("/chat")
async def chat(
    poruka: str = Body(
        ...,
        # embed=True daje naziv "poruka" polju u JSON tijelu zahtjeva.
        embed=True,
        description="Pitanje ili poruka koju šaljemo AI modelu",
        examples=["Objasni mi šta je API u jednoj rečenici."],
    ),
):
    # Za sada šaljemo samo korisničku poruku, bez system prompta i historije.
    response = await client.chat.completions.create(
        model=model,
        messages=[
            # Odkomentarišite system poruku da zadate ponašanje AI asistenta:
            # {
            #     "role": "system",
            #     "content": "Ti si ljubazan AI asistent. Odgovaraj kratko na bosanskom jeziku.",
            # },
            {"role": "user", "content": poruka},
        ],
    )

    # choices[0] je prvi odgovor modela, a message.content njegov tekst.
    return {
        "odgovor": response.choices[0].message.content,
        "model": model,
    }


# Drugi primjer: korisnik kroz Swagger šalje i system prompt i svoju poruku.
# Ovaj endpoint očekuje JSON:
# {
#     "sistemski_prompt": "Ti si nastavnik. Odgovaraj jednostavno.",
#     "poruka": "Objasni mi šta je API."
# }
@app.post("/chat-sa-system-promptom")
async def chat_sa_system_promptom(
    sistemski_prompt: str = Body(
        ...,
        description="Uputa koja određuje ponašanje AI asistenta",
        examples=["Ti si nastavnik. Odgovaraj kratko i jednostavno."],
    ),
    poruka: str = Body(
        ...,
        description="Pitanje ili poruka korisnika",
        examples=["Objasni mi šta je API."],
    ),
):
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sistemski_prompt},
            {"role": "user", "content": poruka},
        ],
    )

    return {
        "odgovor": response.choices[0].message.content,
        "sistemski_prompt": sistemski_prompt,
        "model": model,
    }


# Ovaj dio se izvršava samo kada pokrenemo: python simple_chat.py
# Ne izvršava se kada koristimo: uvicorn simple_chat:app ...
if __name__ == "__main__":
    port = int(os.getenv("APP_PORT", "8017"))
    uvicorn.run(app, host="127.0.0.1", port=port)
