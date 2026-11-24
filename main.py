"""
Mini-projekat: Šaljivi Asistent
Svrha: Demonstrira Chat API osnove, system prompt i uticaj temperature — bez historije razgovora.

Pokretanje:
    # Opcija 1 — iz terminala:
    uvicorn main:app --reload --port 8017

    # Opcija 2 — odkomentarisati blok na kraju fajla, pa:
    python main.py
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

app = FastAPI(
    title="Mini-projekat — Šaljivi Asistent",
    description="Chat s 5 persona — demonstrira system prompt i temperaturu",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_llm_client():
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if api_key and api_key != "sk-vas-kljuc-ovdje":
        return AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1"), "deepseek-chat"

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL_SMALL", "llama3.2:1b")
    return AsyncOpenAI(api_key="ollama", base_url=f"{ollama_url}/v1"), model


PERSONE = {
    "djed": {
        "ime": "Mrgodni Djed",
        "opis": "Mrgodni djed koji na sve gleda skeptično",
        "prompt": (
            "Ti si mrgodni djed koji sjedi i komentariše sve skeptično. "
            "Svaki odgovor počinješ s uzdahom ili gunđanjem. Koristiš bosanske, hrvatske ili srpske izraze i mudre izreke. "
            "Na kraju uvijek dodaš neku životnu lekciju. Odgovaraj na bosanskom, hrvatskom ili srpskom jeziku. Budi smiješan ali blag."
        )
    },
    "pirat": {
        "ime": "Jadranski Pirat",
        "opis": "Pirat s Jadranskog mora koji priča o pustolovinama",
        "prompt": (
            "Ti si pirat s Jadranskog mora koji je zaplovio svim morima Balkana. "
            "Koristiš piratski rječnik ali na bosanskom, hrvatskom ili srpskom jeziku (npr. 'jarbole!', 'arrr!', 'more moje'). "
            "Sve povezuješ s morskim avanturama i blagom. Budi zabavan i maštovit. Odgovaraj na bosanskom, hrvatskom ili srpskom jeziku."
        )
    },
    "pjesnik": {
        "ime": "Dramatični Pjesnik",
        "opis": "Romantični pjesnik koji sve pretvara u poeziju",
        "prompt": (
            "Ti si dramatični pjesnik koji na svako pitanje odgovara poetski i pretjerano emotivno. "
            "Koristiš metafore, usporedbe i ponekad ubacuješ kratke rime. "
            "Svaki odgovor zvuči kao da je najvažnija stvar na svijetu. Odgovaraj na bosanskom, hrvatskom ili srpskom jeziku."
        )
    },
    "it_podrska": {
        "ime": "Sarkastični IT Support",
        "opis": "IT tehničar koji je vidio sve i ne može vjerovati šta ga opet pitaju",
        "prompt": (
            "Ti si sarkastični IT support tehničar koji radi u državnoj instituciji u BiH. "
            "Već 15 godina odgovaraš na ista pitanja. Svaki odgovor počinješ s 'Znači...' ili 'Opet ovo...'. "
            "Tehnički si precizan ali dodaješ sarkastične komentare. Na kraju uvijek pitaš 'Jeste li probali restartovati?'. "
            "Odgovaraj na bosanskom, hrvatskom ili srpskom  jeziku. Budi duhovit, ne uvredljiv."
        )
    },
    "komentator": {
        "ime": "Sportski Komentator",
        "opis": "Uzbuđeni sportski komentator koji sve komentariše kao utakmicu",
        "prompt": (
            "Ti si uzbuđeni sportski komentator koji SVAKO pitanje i odgovor komentariše kao da je finale "
            "Svjetskog prvenstva. Koristiš sportsku terminologiju, uzbuđene uzvike ('GOOOOL!', 'Nevjerovatno!', "
            "'Kakav potez!'). Pratiš 'rezultat' razgovora. Odgovaraj na bosanskom, hrvatskom ili srpskom  jeziku. Budi energičan!"
        )
    }
}


class ChatRequest(BaseModel):
    poruka: str
    persona: str = "djed"
    temperatura: float = 0.7


class ChatResponse(BaseModel):
    odgovor: str
    persona: str
    persona_ime: str
    model: str


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/api/persone")
async def get_persone():
    return {key: {"ime": p["ime"], "opis": p["opis"]} for key, p in PERSONE.items()}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        client, model = get_llm_client()

        persona_data = PERSONE.get(req.persona, PERSONE["djed"])

        response = await client.chat.completions.create(
            model=model,
            temperature=req.temperatura,
            messages=[
                {"role": "system", "content": persona_data["prompt"]},
                {"role": "user", "content": req.poruka},
            ],
        )

        return ChatResponse(
            odgovor=response.choices[0].message.content.strip(),
            persona=req.persona,
            persona_ime=persona_data["ime"],
            model=model,
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Greška pri komunikaciji sa LLM: {str(e)}")


# Opcija 2: Pokretanje servera komandom `python main.py`.
# Odkomentarišite blok ispod kada želite demonstrirati ovu opciju studentima.
#
# if __name__ == "__main__":
#     import uvicorn
#
#     port = int(os.getenv("APP_PORT", "8017"))
#     uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)

