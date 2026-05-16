# Arvada No-Website Leads

Finds service businesses within 10 miles of **6869 W 74th Ave, Arvada, CO 80003** that have no website listed on Google Maps. Outputs a `leads.csv` you can sort and click through.

## Setup

### 1. Create a Google Cloud project and enable the Places API (New)

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create or select a project.
2. Navigate to **APIs & Services → Library**.
3. Search for **Places API (New)** and click **Enable**.
4. Go to **APIs & Services → Credentials**, click **Create Credentials → API key**.
5. Copy the key.

### 2. Configure your environment

```bash
cp .env.example .env
# Open .env and paste your key:
#   GOOGLE_PLACES_API_KEY=AIza...
```

### 3. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run

```bash
python scraper.py
```

The script will:
- Warn you if estimated API cost exceeds $5 and ask for confirmation.
- Print per-category progress as it runs.
- Write `leads.csv` sorted by review count (most-established first).
- Print a summary of API calls made and estimated cost.

## Output columns

| Column | Description |
|---|---|
| `name` | Business name |
| `category` | Google Places type used to find it |
| `address` | Formatted address |
| `phone` | National phone number |
| `rating` | Google star rating (1–5) |
| `review_count` | Number of reviews |
| `place_id` | Google Place ID |
| `maps_url` | Clickable Google Maps link |

## Cost

Each category search costs **$0.032** (Nearby Search New rate). With 22 categories, a full run costs ~**$0.70**.
