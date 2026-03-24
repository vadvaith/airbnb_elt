# 🏠 Airbnb ELT Pipeline

An end-to-end ELT data pipeline that extracts Airbnb listing data, loads it into **Snowflake**, transforms it with **dbt**, and visualizes insights through an interactive **Streamlit** analytics dashboard.

## Architecture

```
Airbnb CSV Data → Snowflake (Raw) → dbt (Transform) → Streamlit (Visualize)
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Storage** | Snowflake | Cloud data warehouse |
| **Transform** | dbt | SQL-based data modeling |
| **Visualization** | Streamlit | Interactive analytics dashboard |

## Project Structure

```
airbnb-elt/
├── app.py                          # Streamlit analytics dashboard
├── airbnb_project/
│   ├── dbt_project.yml             # dbt project configuration
│   ├── models/
│   │   ├── staging/
│   │   │   ├── src_airbnb.yml      # Source definitions
│   │   │   ├── stg_airbnb_listings.sql   # Staging model (view)
│   │   │   └── stg_sirbnb_listings.yml   # Schema tests
│   │   └── marts/
│   │       └── airbnb_summary.sql  # Summary analytics table
│   ├── seeds/                      # CSV seed data
│   └── tests/                      # Custom data tests
├── .streamlit/
│   └── secrets.toml                # Snowflake credentials (gitignored)
└── .gitignore
```

## Data Models

### Staging: `stg_airbnb_listings`
Cleans and type-casts raw Airbnb listing data including:
- Listing details (name, room type, price)
- Location (neighbourhood, latitude, longitude)
- Host information
- Review metrics
- Availability

### Marts: `airbnb_summary`
Aggregated summary by room type:
- Total listings count
- Average price
- Average availability (days/year)

## Dashboard Features

The Streamlit dashboard provides a premium dark-themed analytics interface with:

- **📊 Overview** — KPI cards, donut charts, price distribution, reviews vs price scatter plot
- **🗺️ Map** — Interactive geospatial map of all listings
- **🏘️ Neighbourhoods** — Top neighbourhoods by listings, pricing, and room type breakdown
- **📋 Data Explorer** — Sortable, filterable raw data table

### Sidebar Filters
- Room type
- Neighbourhood
- Price range
- Minimum reviews

## Setup

### Prerequisites
- Python 3.9+
- Snowflake account
- dbt CLI (`pip install dbt-snowflake`)

### 1. Clone the repo
```bash
git clone https://github.com/vadvaith/airbnb_elt.git
cd airbnb_elt
```

### 2. Install dependencies
```bash
pip install streamlit pandas snowflake-connector-python altair
```

### 3. Configure Snowflake credentials

Create `.streamlit/secrets.toml`:
```toml
[snowflake]
user = "YOUR_USER"
password = "YOUR_PASSWORD"
account = "YOUR_ACCOUNT"
warehouse = "AIRBNB_WH"
database = "AIRBNB_DB"
schema = "ANALYTICS"
role = "ACCOUNTADMIN"
```

### 4. Run dbt models
```bash
cd airbnb_project
dbt run
```

### 5. Launch the dashboard
```bash
streamlit run app.py
```

## Tech Stack

- **Snowflake** — Cloud data warehousing
- **dbt** — Data transformation & testing
- **Streamlit** — Interactive data visualization
- **Altair** — Declarative statistical charts
- **Python** — Orchestration & application logic
