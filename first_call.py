import httpx
from config import get_settings

key=get_settings().COMPANIES_HOUSE_API_KEY.get_secret_value()

response= httpx.get( "https://api.company-information.service.gov.uk/search/companies",params={"q":"Tesco", "items_per_page":3},auth=(key,""), timeout=15)
print("Status", response.status_code)
for item in response.json().get("items",[]):
    print(item["company_number"], "|", item["title"], "|", item.get("company_status"))