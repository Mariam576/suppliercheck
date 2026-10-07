from fastapi import FastAPI,HTTPException
from companies_house import get_company, search_companies
from config import get_settings
from location import flood_warning, lookup_postcode

app=FastAPI(title=get_settings().APP_NAME)

@app.get("/health")
async def health()-> dict:
    return{"status":"ok"}
@app.get("/search")
async def search(name:str)-> list[dict]:
    return await search_companies(name)

@app.get("/check/{number}")
async def check (number:str)-> dict:
    try:
        company = await get_company(number)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    place= None
    flood=[]
    if company["postcode"]:
        try:
            place= await lookup_postcode(company["postcode"])
        except ValueError:
            place=None
        if place and place["latitude"] is not None:
            flood= await flood_warning(place["latitude"],place["longitude"])
    return { "company":company,"place":place, "flood_warning":flood}

