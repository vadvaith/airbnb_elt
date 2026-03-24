import streamlit as st
import pandas as pd
import snowflake.connector
import altair as alt
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Airbnb Analytics Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for premium dark look ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15, 15, 30, 0.95);
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px 24px;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
}
div[data-testid="stMetric"] label {
    color: rgba(255,255,255,0.55) !important;
    font-weight: 500;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700;
    font-size: 1.8rem;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: rgba(255,255,255,0.5);
    border-radius: 8px;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #818cf8 !important;
    border-bottom-color: #818cf8 !important;
}

/* Subheader styling */
h1, h2, h3 {
    color: #e2e8f0 !important;
    font-weight: 700 !important;
}

/* Dataframe styling */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}

/* Divider */
hr {
    border-color: rgba(255,255,255,0.06) !important;
}

/* Selectbox / multiselect */
div[data-baseweb="select"] {
    border-radius: 10px;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_listings():
    conn = snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"],
    )
    query = """
    SELECT
        id, name, host_id, host_name, neighbourhood, latitude, longitude,
        room_type, price, minimum_nights, number_of_reviews,
        reviews_per_month, calculated_host_listings_count,
        availability_365, number_of_reviews_ltm
    FROM AIRBNB_DB.ANALYTICS.STG_AIRBNB_LISTINGS
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df.columns = [c.lower() for c in df.columns]
    # Clean up types
    for col in ["price", "minimum_nights", "number_of_reviews", "reviews_per_month",
                "calculated_host_listings_count", "availability_365", "number_of_reviews_ltm"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    return df


df_raw = load_listings()

# ── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏠 Filters")
    st.markdown("---")

    # Room type filter
    room_types = sorted(df_raw["room_type"].dropna().unique())
    selected_rooms = st.multiselect("Room Type", room_types, default=room_types)

    # Neighbourhood filter
    neighbourhoods = sorted(df_raw["neighbourhood"].dropna().unique())
    selected_neighbourhoods = st.multiselect(
        "Neighbourhood",
        neighbourhoods,
        default=[],
        placeholder="All neighbourhoods",
    )

    # Price range
    price_min = int(df_raw["price"].min()) if not df_raw["price"].isna().all() else 0
    price_max = int(df_raw["price"].max()) if not df_raw["price"].isna().all() else 1000
    price_max = min(price_max, 10000)  # Cap outliers for slider
    price_range = st.slider("Price Range ($)", price_min, price_max, (price_min, price_max))

    # Min reviews
    min_reviews = st.number_input("Minimum Reviews", min_value=0, value=0, step=1)

    st.markdown("---")
    st.caption(f"📊 Dataset: {len(df_raw):,} total listings")

# Apply filters
df = df_raw.copy()
df = df[df["room_type"].isin(selected_rooms)]
if selected_neighbourhoods:
    df = df[df["neighbourhood"].isin(selected_neighbourhoods)]
df = df[(df["price"] >= price_range[0]) & (df["price"] <= price_range[1])]
df = df[df["number_of_reviews"] >= min_reviews]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 10px 0 5px 0;">
    <h1 style="margin:0; font-size:2.2rem; background: linear-gradient(135deg, #818cf8, #c084fc, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:800;">
        Airbnb Analytics Dashboard
    </h1>
    <p style="color: rgba(255,255,255,0.45); font-size:0.95rem; margin-top:4px;">
        Real-time insights from your Snowflake data warehouse
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ── KPI Cards ────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Total Listings", f"{len(df):,}")
with k2:
    avg_price = df["price"].mean()
    st.metric("Avg Price", f"${avg_price:,.0f}" if not np.isnan(avg_price) else "N/A")
with k3:
    median_price = df["price"].median()
    st.metric("Median Price", f"${median_price:,.0f}" if not np.isnan(median_price) else "N/A")
with k4:
    avg_reviews = df["number_of_reviews"].mean()
    st.metric("Avg Reviews", f"{avg_reviews:,.1f}" if not np.isnan(avg_reviews) else "N/A")
with k5:
    avg_avail = df["availability_365"].mean()
    st.metric("Avg Availability", f"{avg_avail:,.0f} days" if not np.isnan(avg_avail) else "N/A")

st.markdown("")

# ── Altair color scheme ──────────────────────────────────────────────────────
PALETTE = ["#818cf8", "#c084fc", "#f472b6", "#fb923c", "#34d399", "#38bdf8", "#facc15"]

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🗺️ Map", "🏘️ Neighbourhoods", "📋 Data Explorer"])

# ─── Tab 1: Overview ─────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Listings by Room Type")
        room_counts = df.groupby("room_type").size().reset_index(name="count")
        chart_room = (
            alt.Chart(room_counts)
            .mark_arc(innerRadius=60, cornerRadius=6, padAngle=0.02)
            .encode(
                theta=alt.Theta("count:Q"),
                color=alt.Color("room_type:N", scale=alt.Scale(range=PALETTE), legend=alt.Legend(title=None, orient="bottom")),
                tooltip=["room_type:N", "count:Q"],
            )
            .properties(height=320)
        )
        st.altair_chart(chart_room, width="stretch")

    with col2:
        st.markdown("#### Average Price by Room Type")
        room_price = df.groupby("room_type")["price"].mean().reset_index()
        chart_price = (
            alt.Chart(room_price)
            .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
            .encode(
                x=alt.X("room_type:N", axis=alt.Axis(labelAngle=0, title=None)),
                y=alt.Y("price:Q", title="Avg Price ($)"),
                color=alt.Color("room_type:N", scale=alt.Scale(range=PALETTE), legend=None),
                tooltip=["room_type:N", alt.Tooltip("price:Q", format="$.0f")],
            )
            .properties(height=320)
        )
        st.altair_chart(chart_price, width="stretch")

    st.markdown("---")

    # Price distribution
    st.markdown("#### Price Distribution")
    price_cap = int(df["price"].quantile(0.95)) if len(df) > 0 else 500
    df_hist = df[df["price"] <= price_cap]
    chart_hist = (
        alt.Chart(df_hist)
        .mark_area(
            opacity=0.6,
            interpolate="monotone",
            line={"color": "#818cf8", "strokeWidth": 2},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color="rgba(129,140,248,0.4)", offset=0),
                    alt.GradientStop(color="rgba(129,140,248,0.01)", offset=1),
                ],
                x1=1, x2=1, y1=1, y2=0,
            ),
        )
        .encode(
            x=alt.X("price:Q", bin=alt.Bin(maxbins=60), title="Price ($)"),
            y=alt.Y("count():Q", title="Number of Listings"),
            tooltip=[
                alt.Tooltip("price:Q", bin=alt.Bin(maxbins=60), title="Price Range"),
                alt.Tooltip("count():Q", title="Listings"),
            ],
        )
        .properties(height=280)
    )
    st.altair_chart(chart_hist, width="stretch")

    st.markdown("---")

    # Reviews vs Price scatter
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Reviews vs Price")
        df_scatter_base = df[(df["price"] <= price_cap) & (df["number_of_reviews"] > 0)]
        df_scatter = df_scatter_base.sample(
            min(2000, len(df_scatter_base)), random_state=42
        ) if len(df_scatter_base) > 0 else df_scatter_base
        chart_scatter = (
            alt.Chart(df_scatter)
            .mark_circle(opacity=0.5, size=40)
            .encode(
                x=alt.X("price:Q", title="Price ($)"),
                y=alt.Y("number_of_reviews:Q", title="Number of Reviews"),
                color=alt.Color("room_type:N", scale=alt.Scale(range=PALETTE), legend=alt.Legend(title=None)),
                tooltip=["name:N", "price:Q", "number_of_reviews:Q", "room_type:N"],
            )
            .properties(height=340)
            .interactive()
        )
        st.altair_chart(chart_scatter, width="stretch")

    with col4:
        st.markdown("#### Availability Distribution")
        chart_avail = (
            alt.Chart(df)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, opacity=0.7)
            .encode(
                x=alt.X("availability_365:Q", bin=alt.Bin(maxbins=30), title="Days Available / Year"),
                y=alt.Y("count():Q", title="Listings"),
                color=alt.value("#c084fc"),
                tooltip=[
                    alt.Tooltip("availability_365:Q", bin=alt.Bin(maxbins=30), title="Availability Range"),
                    alt.Tooltip("count():Q", title="Listings"),
                ],
            )
            .properties(height=340)
        )
        st.altair_chart(chart_avail, width="stretch")

# ─── Tab 2: Map ──────────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### Listing Locations")
    map_df = df[["latitude", "longitude", "name", "price", "room_type"]].dropna()
    if len(map_df) > 0:
        st.map(map_df, latitude="latitude", longitude="longitude", size=8, color="#818cf8")
        st.caption(f"Showing {len(map_df):,} listings on map")
    else:
        st.info("No listings match your current filters.")

# ─── Tab 3: Neighbourhoods ───────────────────────────────────────────────────
with tab3:
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("#### Top 15 Neighbourhoods by Listings")
        top_n = df.groupby("neighbourhood").size().reset_index(name="count").nlargest(15, "count")
        chart_top = (
            alt.Chart(top_n)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("count:Q", title="Number of Listings"),
                y=alt.Y("neighbourhood:N", sort="-x", title=None),
                color=alt.Color("count:Q", scale=alt.Scale(scheme="purples"), legend=None),
                tooltip=["neighbourhood:N", "count:Q"],
            )
            .properties(height=420)
        )
        st.altair_chart(chart_top, width="stretch")

    with col6:
        st.markdown("#### Avg Price by Top 15 Neighbourhoods")
        top_names = top_n["neighbourhood"].tolist()
        nbh_price = df[df["neighbourhood"].isin(top_names)].groupby("neighbourhood")["price"].mean().reset_index()
        chart_nbh_price = (
            alt.Chart(nbh_price)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("price:Q", title="Avg Price ($)"),
                y=alt.Y("neighbourhood:N", sort="-x", title=None),
                color=alt.Color("price:Q", scale=alt.Scale(scheme="magma"), legend=None),
                tooltip=["neighbourhood:N", alt.Tooltip("price:Q", format="$.0f")],
            )
            .properties(height=420)
        )
        st.altair_chart(chart_nbh_price, width="stretch")

    st.markdown("---")

    st.markdown("#### Room Type Breakdown by Top Neighbourhoods")
    nbh_room = df[df["neighbourhood"].isin(top_names)].groupby(["neighbourhood", "room_type"]).size().reset_index(name="count")
    chart_nbh_room = (
        alt.Chart(nbh_room)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Listings", stack="normalize"),
            y=alt.Y("neighbourhood:N", sort=top_names, title=None),
            color=alt.Color("room_type:N", scale=alt.Scale(range=PALETTE), legend=alt.Legend(title=None, orient="top")),
            tooltip=["neighbourhood:N", "room_type:N", "count:Q"],
        )
        .properties(height=420)
    )
    st.altair_chart(chart_nbh_room, width="stretch")

# ─── Tab 4: Data Explorer ───────────────────────────────────────────────────
with tab4:
    st.markdown("#### Explore the Data")
    show_cols = st.multiselect(
        "Select columns",
        df.columns.tolist(),
        default=["name", "neighbourhood", "room_type", "price", "number_of_reviews", "availability_365"],
    )
    if show_cols:
        sort_col = st.selectbox("Sort by", show_cols, index=show_cols.index("price") if "price" in show_cols else 0)
        sort_asc = st.toggle("Ascending", value=False)
        display_df = df[show_cols].sort_values(sort_col, ascending=sort_asc).head(500)
        st.dataframe(display_df, width="stretch", height=500)
        st.caption(f"Showing top 500 of {len(df):,} filtered listings")
    else:
        st.info("Select at least one column to display.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:rgba(255,255,255,0.25); font-size:0.8rem;'>"
    "Airbnb Analytics Dashboard · Powered by Snowflake & dbt · Built with Streamlit"
    "</p>",
    unsafe_allow_html=True,
)