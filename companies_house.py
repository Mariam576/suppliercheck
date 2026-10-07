import asyncio 
import sys
import httpx
from config import get_settings
Base_Url= "https://api.company-information.service.gov.uk"
def _client()-> httpx.AsyncClient:
    key= get_settings().COMPANIES_HOUSE_API_KEY.get_secret_value()
    return httpx.AsyncClient(base_url=Base_Url, auth=(key, ""), timeout=15)

async def search_companies(name:str, limit:int=5)->list[dict]:
    async with _client() as client:
        response= await client.get("/search/companies", params={"q": name, "items_per_page":limit})
        response.raise_for_status()
        items=response.json().get("items", [])
        return[
            {"number": item["company_number"],
             "name":item["title"],
             "status": item.get("company_status", "unknown"),
              "created": item.get("date_of_creation"),
            "address": item.get("address_snippet", ""),
            }
            for item in items
        ]
async def get_company(number: str)-> dict:
    async with _client() as client:
        response =await client.get(f"/company/{number}")
        if response.status_code==400:
            raise ValueError(f"No company with the number {number!r} is on the register.")
        response.raise_for_status()
        data = response.json()
        accounts = data.get("accounts", {})
        office = data.get("registered_office_address", {})
        return {
            "number": data["company_number"],
            "name": data["company_name"],
            "status": data.get("company_status", "unknown"),
            "type": data.get("type", ""),
            "created": data.get("date_of_creation"),
            "postcode": office.get("postal_code", ""),
            "accounts_overdue": accounts.get("overdue", False),
            "accounts_next_due": accounts.get("next_due"),
            "last_accounts_made_up_to": accounts.get("last_accounts", {}).get("made_up_to"),
            "has_insolvency_history": data.get("has_insolvency_history", False),
            "has_charges": data.get("has_charges", False),
        }


async def main(name:str)-> None:
    matches=await search_companies(name)
    if not matches:
        print(f"no company called {name!r} was found")
        return
    print("Matches")
    for match in matches:
        print(f"{match['number']} {match['name']} ({match['status']})")
    print()
    print("Details of the first match:")
    for field, value in (await get_company(matches[0]["number"])).items():
        print(f"{field}:{value}")
if __name__=="__main__":
    asyncio.run(main(sys.argv[1] if  len(sys.argv)>1 else "Tesco"))