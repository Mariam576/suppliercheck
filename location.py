import asyncio
import sys
import httpx

POSTCODE_URL="https://api.postcodes.io/postcodes/"
FLOOD_URL= "https://environment.data.gov.uk/flood-monitoring/id/floods"

async def lookup_postcode(postcode: str)-> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        response=await client.get(POSTCODE_URL + postcode.replace(" ",""))
        if response.status_code==404:
            raise ValueError(f"{postcode!r} is not a UK postcode on record.")
        response.raise_for_status()
        result=response.json()["result"]
    return {
        "postcode": result["postcode"],
        "country": result.get("country") or "",
        "region": result.get("region") or "",
        "district": result.get("admin_district") or "",
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
    }

async def flood_warning(latitude: float, longitude: float, within_km:int=10)-> list[dict]:
    async with httpx.AsyncClient(timeout=15) as client:
        response= await client.get(FLOOD_URL, params={"lat": latitude, "long": longitude, "dist" :within_km})
        response.raise_for_status()
        items=response.json().get("items",[])
        return[{
            "area": item.get("description", ""),
            "severity": item.get("severity", "unknown"),
            "level": item.get("severityLevel"),
            "raised": item.get("timeRaised"),
        }
        for item in items
        ]
async def main(postcode: str) -> None:
    place = await lookup_postcode(postcode)
    print("Place:")
    for field, value in place.items():
        print(f"  {field}: {value}")
    print()
    if place["latitude"] is None:
        print("This postcode has no coordinates, so flood warnings cannot be checked.")
        return
    warnings = await flood_warning(place["latitude"], place["longitude"])
    print(f"Flood warnings within 10 km: {len(warnings)}")
    for warning in warnings:
        print(f"  {warning['severity']}: {warning['area']} (raised {warning['raised']})")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "AL7 1GA"))