import csv
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
if not API_KEY:
    print("ERROR: GOOGLE_PLACES_API_KEY not set in .env")
    sys.exit(1)

# Geocoded once: 6869 W 74th Ave, Arvada, CO 80003
CENTER_LAT = 39.8285
CENTER_LNG = -105.0892
RADIUS_METERS = 16093  # 10 miles

INCLUDED_TYPES = [
    "plumber",
    "electrician",
    "roofing_contractor",
    "general_contractor",
    "painter",
    "locksmith",
    "moving_company",
    "house_cleaning_service",
    "car_repair",
    "hair_salon",
    "barber_shop",
    "nail_salon",
    "beauty_salon",
    "pet_grooming",
    "dog_walker",
    "lawn_care_service",
    "landscaping_service",
    "pest_control_service",
    "appliance_repair_service",
    "tutoring_service",
    "auto_body_shop",
    "tire_shop",
]

NEARBY_SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby"
FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.websiteUri,"
    "places.nationalPhoneNumber,"
    "places.primaryType,"
    "places.rating,"
    "places.userRatingCount,"
    "places.businessStatus"
)

COST_PER_CALL = 0.032  # Nearby Search New as of 2026
COST_WARNING_THRESHOLD = 5.00


def estimated_cost(num_calls: int) -> float:
    return num_calls * COST_PER_CALL


def check_cost_warning(num_categories: int) -> None:
    total_cost = estimated_cost(num_categories)
    if total_cost > COST_WARNING_THRESHOLD:
        print(
            f"\nWARNING: Estimated cost for {num_categories} API calls is "
            f"${total_cost:.2f}, which exceeds the ${COST_WARNING_THRESHOLD:.2f} threshold."
        )
        answer = input("Do you want to continue? (yes/no): ").strip().lower()
        if answer not in ("yes", "y"):
            print("Aborted.")
            sys.exit(0)


def search_nearby(category: str) -> list[dict]:
    payload = {
        "includedTypes": [category],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {"latitude": CENTER_LAT, "longitude": CENTER_LNG},
                "radius": RADIUS_METERS,
            }
        },
    }
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    resp = requests.post(NEARBY_SEARCH_URL, json=payload, headers=headers)
    if resp.status_code != 200:
        print(f"\nERROR: API returned {resp.status_code} for category '{category}':")
        print(resp.text)
        sys.exit(1)
    return resp.json().get("places", [])


def is_active(place: dict) -> bool:
    status = place.get("businessStatus", "")
    return status not in ("CLOSED_PERMANENTLY", "CLOSED_TEMPORARILY")


def has_no_website(place: dict) -> bool:
    return not place.get("websiteUri")


def maps_url(place_id: str) -> str:
    return f"https://www.google.com/maps/place/?q=place_id:{place_id}"


def main() -> None:
    check_cost_warning(len(INCLUDED_TYPES))

    seen_ids: set[str] = set()
    leads: list[dict] = []
    total_found = 0
    api_calls = 0

    for category in INCLUDED_TYPES:
        places = search_nearby(category)
        api_calls += 1
        total_found += len(places)

        without_website = 0
        for place in places:
            if not is_active(place):
                continue
            if not has_no_website(place):
                continue
            place_id = place.get("id", "")
            if place_id in seen_ids:
                continue
            seen_ids.add(place_id)
            without_website += 1
            leads.append({
                "name": place.get("displayName", {}).get("text", ""),
                "category": category,
                "address": place.get("formattedAddress", ""),
                "phone": place.get("nationalPhoneNumber", ""),
                "rating": place.get("rating", ""),
                "review_count": place.get("userRatingCount", 0),
                "place_id": place_id,
                "maps_url": maps_url(place_id),
            })

        print(f"[{category}] Found {len(places)} results, {without_website} without website")

    leads.sort(key=lambda x: x["review_count"], reverse=True)

    output_path = "leads.csv"
    fieldnames = ["name", "category", "address", "phone", "rating", "review_count", "place_id", "maps_url"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

    cost = estimated_cost(api_calls)
    print(f"\n--- Summary ---")
    print(f"API calls made:          {api_calls}")
    print(f"Total businesses found:  {total_found}")
    print(f"Without website (dedup): {len(leads)}")
    print(f"Estimated cost:          ${cost:.4f}")
    print(f"Output written to:       {output_path}")


if __name__ == "__main__":
    main()
