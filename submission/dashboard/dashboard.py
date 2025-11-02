import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency

sns.set(style='darkgrid')

# Load df_day
try:
    df_day = pd.read_csv("submission/data/archive/day.csv")
except FileNotFoundError:
    try:
        df_day = pd.read_csv("data/archive/day.csv")
    except FileNotFoundError:
        raise FileNotFoundError("df_day.csv not found in either path!")

# Load df_hour
try:
    df_hour = pd.read_csv("submission/data/archive/hour.csv")
except FileNotFoundError:
    try:
        df_hour = pd.read_csv("data/archive/hour.csv")
    except FileNotFoundError:
        raise FileNotFoundError("df_hour.csv not found in either path!")
    
# Convert columns
df_day['dteday'] = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

df_day['season'] = df_day['season'].replace({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
df_hour['season'] = df_hour['season'].replace({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})

st.title("Bike Sharing Analysis Dashboard 🚴‍♂️")

weather_map = {
    1: 'Clear',
    2: 'Misty',
    3: 'Light_rainsnow',
    4: 'Heavy_rainsnow'
}
df_day['weathersit'] = df_day['weathersit'].replace(weather_map)
df_hour['weathersit'] = df_hour['weathersit'].replace(weather_map)

df_day['year'] = df_day['dteday'].dt.year
df_day['month'] = df_day['dteday'].dt.month
df_day['day'] = df_day['dteday'].dt.day
df_day['day_name'] = df_day['dteday'].dt.day_name()
df_day['week'] = df_day['dteday'].dt.isocalendar().week
df_day[['dteday', 'holiday', 'workingday', 'weekday', 'year', 'month', 'day', 'day_name', 'week']].head()

df_hour['year'] = df_hour['dteday'].dt.year
df_hour['month'] = df_hour['dteday'].dt.month
df_hour['day'] = df_hour['dteday'].dt.day
df_hour['day_name'] = df_hour['dteday'].dt.day_name()
df_hour['week'] = df_hour['dteday'].dt.isocalendar().week
df_hour[['dteday', 'holiday', 'workingday', 'weekday', 'year', 'month', 'day', 'hr', 'day_name', 'week']].head()

def get_category_days(day_name):
    if day_name in ["Saturday", "Sunday"]:
        return "weekend"
    else: 
        return "weekdays"

df_day["category_days"] = df_day["day_name"].apply(get_category_days)
df_hour["category_days"] = df_hour["day_name"].apply(get_category_days)

df_day.drop(['instant', 'yr', 'mnth', 'weekday', 'workingday'], axis = 1, inplace= True)
df_hour.drop(['instant', 'yr', 'mnth', 'weekday', 'workingday'], axis = 1, inplace= True)

columns = ['season', 'weathersit', 'day_name', 'category_days']
 
for column in columns:
    df_day[column] =  df_day[column].astype("category")
    df_hour[column] =  df_hour[column].astype("category")

# -------------------------
# Sidebar filters
# -------------------------
with st.sidebar:
    st.header("Filters")
    min_date = df_day['dteday'].min()
    max_date = df_day['dteday'].max()
    start_date, end_date = st.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Filter data
df_day_filtered = df_day[(df_day['dteday'] >= pd.to_datetime(start_date)) &
                         (df_day['dteday'] <= pd.to_datetime(end_date))]
df_hour_filtered = df_hour[(df_hour['dteday'] >= pd.to_datetime(start_date)) &
                           (df_hour['dteday'] <= pd.to_datetime(end_date))]

# -------------------------
# 1. Trend Penyewaan Sepeda
# -------------------------
st.header("1. Tren Penyewaan Sepeda")

df_cust_day = df_day_filtered.groupby('dteday').agg({'casual':'sum', 'registered':'sum', 'cnt':'sum'}).reset_index()
df_cust_day_melt = pd.melt(df_cust_day, id_vars=['dteday'], value_vars=['casual','registered','cnt'], var_name='status', value_name='count')

fig, ax = plt.subplots(figsize=(12,5))
sns.lineplot(data=df_cust_day_melt, x='dteday', y='count', hue='status', linewidth=2, palette='dark', ax=ax)
ax.set_xlabel("Date")
ax.set_ylabel("Count")
ax.set_title("Total Sharing Bikes by Customer")
st.pyplot(fig)

# -------------------------
# 2. Penyewaan per Musim
# -------------------------
st.header("2. Penyewaan Sepeda per Musim")
df_cust_season = df_day_filtered.groupby('season').agg({'casual':'sum', 'registered':'sum', 'cnt':'sum'}).reset_index()

df_cust_season_melt = pd.melt(df_cust_season, id_vars=['season'], value_vars=['casual','registered'], var_name='status', value_name='count')

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(data=df_cust_season_melt, x='season', y='count', hue='status', palette='pastel', ax=ax)
ax.set_title("Registered vs Casual Customer per Season")
st.pyplot(fig)

# -------------------------
# 3. Penyewaan per Jam
# -------------------------
st.header("3. Penyewaan Sepeda per Jam")

df_cust_hour = df_hour_filtered.groupby('hr').agg({'casual':'sum','registered':'sum','cnt':'sum'}).reset_index()
df_cust_hour_melt = pd.melt(df_cust_hour, id_vars=['hr'], value_vars=['casual','registered'], var_name='status', value_name='count')

fig, ax = plt.subplots(figsize=(12,5))
sns.lineplot(data=df_cust_hour_melt, x='hr', y='count', hue='status', palette='dark', linewidth=2, ax=ax)
ax.set_xlabel("Hour")
ax.set_ylabel("Count")
ax.set_title("Customer Rentals by Hour")
st.pyplot(fig)

# -------------------------
# 4. Penyewaan per Hari Kerja vs Akhir Pekan
# -------------------------
st.header("4. Penyewaan per Hari Kerja vs Akhir Pekan")

df_cust_days = df_hour_filtered.groupby(['hr','category_days']).agg({'casual':'sum','registered':'sum','cnt':'sum'}).reset_index()

fig, ax = plt.subplots(figsize=(12,5))
sns.lineplot(data=df_cust_days, x='hr', y='cnt', hue='category_days', palette='Set2', ax=ax)
ax.set_title("Count of Customer per Hour by Day Type")
ax.set_xlabel("Hour")
ax.set_ylabel("Count")
st.pyplot(fig)

# -------------------------
# 5. RFM Analysis
# -------------------------
st.header("5. RFM Analysis per Bulan")

latest_date = df_day_filtered['dteday'].max()
df_rfm = df_day_filtered.groupby('month', as_index=False).agg(
    recency=('dteday', lambda x: (latest_date - x.max()).days),
    frequency=('cnt','count'),
    monetary=('cnt','sum')
)

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(data=df_rfm, x='month', y='monetary', palette='Blues_d', ax=ax)
ax.set_title("Total Peminjaman per Bulan (Monetary)")
ax.set_xlabel("Month")
ax.set_ylabel("Total Rental (cnt)")
st.pyplot(fig)

col1, col2, col3 = st.columns(3)
col1.metric("Avg Recency (days)", round(df_rfm.recency.mean(),1))
col2.metric("Avg Frequency", round(df_rfm.frequency.mean(),1))
col3.metric("Avg Monetary (Rental Count)", round(df_rfm.monetary.mean(), 0))

st.caption("Copyright ©2025")
