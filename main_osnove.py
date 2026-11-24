# kreirat cemo osnovni API sa fast API-om
# za ucitavanje podataka koristiti pandas

from fastapi import Body, FastAPI # koristi se kreiranje API

# kreiramo aplikaciju / api
# app u pythonvarijabla koja sadrzi instancu FastAPI-au je 
app = FastAPI(
    title = "Naš API",
    description = "Demonstracija API-a"
)

# 
@app.get("/")
async def pocetna_stranica():
    return { "poruka" : "pocetna stranica!" }


@app.get("/health")
async def pocetna_stranica():
    return { "poruka" : "ziv i zdrav sam!" }
