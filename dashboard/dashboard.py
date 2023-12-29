import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
import seaborn as sns
import streamlit as st
import urllib

# load data
print('load dimulai')
order_purchase = pd.read_csv('https://raw.githubusercontent.com/andharsm/visualisasi-with-python/main/dashboard/dataset_order_purchase.csv')
print('load berhasil')
# order_purchase = pd.read_csv('D:/Kuliah/Dicoding/visualisasi-with-python/dashboard/dataset_order_purchase.csv')

# Fungsi bantuan

# Define your Streamlit app
st.title("E-Commerce Public Data Analysis")

# Daily Orders Purchase
st.subheader("Order Harian")

# Convert 'order_purchase_timestamp' to datetime
order_purchase['order_purchase_timestamp'] = pd.to_datetime(order_purchase['order_purchase_timestamp'])

# min_date = pd.to_datetime(order_purchase["order_purchase_timestamp"]).min().date()
# max_date = pd.to_datetime(order_purchase["order_purchase_timestamp"]).max().date()

min_date = order_purchase["order_purchase_timestamp"].min().date()
max_date = order_purchase["order_purchase_timestamp"].max().date()

# Date Range
start_date, end_date = st.date_input(
    label="Select Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter data berdasarkan rentang tanggal yang dipilih
filtered_data = order_purchase[
    (order_purchase['order_purchase_timestamp'].dt.date >= start_date) &
    (order_purchase['order_purchase_timestamp'].dt.date <= end_date)
]

# Menghitung jumlah order untuk setiap tanggal
daily_orders = filtered_data['order_purchase_timestamp'].dt.date.value_counts().sort_index()

col1, col2 = st.columns(2)

with col1:
    total_order = len(filtered_data)
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = filtered_data['price'].sum().round(2)
    st.markdown(f"Total Revenue: **{total_revenue}**")

# Plotting
fig, ax = plt.subplots(figsize=(20, 6))
sns.lineplot(x=daily_orders.index, y=daily_orders.values, color='skyblue', ax=ax)
ax.set_title('Banyaknya Orderan per Tanggal')
ax.set_xlabel('Tanggal')
ax.set_ylabel('Banyaknya Orderan')

# Menentukan format dan interval untuk label tanggal
date_format = mdates.DateFormatter('%Y-%m-%d')
# Calculate the difference in days between start and end dates
date_difference = (end_date - start_date).days

# Choose the appropriate locator based on the date range
if date_difference <= 7:  # Daily
    locator = mdates.DayLocator()
elif date_difference <= 31:  # Weekly
    locator = mdates.WeekdayLocator()
else:  # Monthly
    locator = mdates.MonthLocator()

ax.xaxis.set_major_formatter(date_format)
ax.xaxis.set_major_locator(locator)

ax.tick_params(axis='x', rotation=45)  # Memutar label tanggal untuk memperbaiki keterbacaan
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Display plot in Streamlit
st.pyplot(fig)

# Daily Orders Purchase
st.subheader("Persebaran Wilayah Pembeli")