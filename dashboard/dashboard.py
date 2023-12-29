import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
import seaborn as sns
import streamlit as st
import urllib

# load data
@st.cache  # Menambahkan decorator st.cache untuk menyimpan data dalam cache
def load_data():
    order_purchase = pd.read_csv('https://raw.githubusercontent.com/andharsm/visualisasi-with-python/main/dashboard/dataset_order_purchase.csv')
    customer_distribution = pd.read_csv('https://raw.githubusercontent.com/andharsm/visualisasi-with-python/main/dashboard/dataset_customer_distribution.csv')
    order_items = pd.read_csv('https://raw.githubusercontent.com/andharsm/visualisasi-with-python/main/dashboard/dataset_order_items.csv')
    product_rating = pd.read_csv('https://raw.githubusercontent.com/andharsm/visualisasi-with-python/main/dashboard/dataset_product_rating.csv')
    return order_purchase, customer_distribution, order_items, product_rating

order_purchase, customer_distribution, order_items, product_rating = load_data()
print('load berhasil')
# order_purchase = pd.read_csv('D:/Kuliah/Dicoding/visualisasi-with-python/dashboard/dataset_order_purchase.csv')
# customer_distribution = pd.read_csv('D:/Kuliah/Dicoding/visualisasi-with-python/dashboard/dataset_customer_distribution.csv')
# order_items = pd.read_csv('D:/Kuliah/Dicoding/visualisasi-with-python/dashboard/dataset_order_items.csv')
# product_rating = pd.read_csv('D:/Kuliah/Dicoding/visualisasi-with-python/dashboard/dataset_product_rating.csv')

# Fungsi bantuan
def plot_brazil_map(data):
    brazil_map = mpimg.imread(urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'), format='jpg')

    fig, ax = plt.subplots(figsize=(10, 10))

    # Menghitung frekuensi kemunculan setiap state
    state_counts = data['geolocation_state'].value_counts()

    # Mengambil state dengan jumlah terbanyak
    states_ordered = state_counts.index

    # Menggunakan peta warna dari merah ke kuning (warna hangat)
    colors = plt.cm.RdYlBu([i/float(len(states_ordered)-1) for i in range(len(states_ordered))])

    for state, color in zip(states_ordered, colors):
        state_data = data[data['geolocation_state'] == state]
        ax.scatter(state_data['geolocation_lng'], state_data['geolocation_lat'], alpha=0.7, s=20, c=[color], label=state)

    # Menampilkan peta Brasil sebagai background
    ax.imshow(brazil_map, extent=[-73.98283055, -33.75116944, -33.8, 5.4])

    # Menyembunyikan sumbu x dan y
    ax.axis('off')

    # Menambahkan legenda
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

    return fig

# Define your Streamlit app
st.title("E-Commerce Public Data Analysis")

# Convert 'order_purchase_timestamp' to datetime
order_purchase['order_purchase_timestamp'] = pd.to_datetime(order_purchase['order_purchase_timestamp'])
customer_distribution['order_purchase_timestamp'] = pd.to_datetime(customer_distribution['order_purchase_timestamp'])
order_items['order_purchase_timestamp'] = pd.to_datetime(order_items['order_purchase_timestamp'])

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
filtered_order = order_purchase[
    (order_purchase['order_purchase_timestamp'].dt.date >= start_date) &
    (order_purchase['order_purchase_timestamp'].dt.date <= end_date)
]

filtered_customer = customer_distribution[
    (customer_distribution['order_purchase_timestamp'].dt.date >= start_date) &
    (customer_distribution['order_purchase_timestamp'].dt.date <= end_date)
]

filtered_customer['order_purchase_timestamp'] = filtered_customer['order_purchase_timestamp'].dt.date.value_counts().sort_index()

filtered_orders = order_items[
    (order_items['order_purchase_timestamp'].dt.date >= start_date) &
    (order_items['order_purchase_timestamp'].dt.date <= end_date)
]

filtered_orders['order_purchase_timestamp'] = filtered_orders['order_purchase_timestamp'].dt.date.value_counts().sort_index()

# Daily Orders Purchase
st.subheader("Order Harian")

# Menghitung jumlah order untuk setiap tanggal
daily_orders = filtered_order['order_purchase_timestamp'].dt.date.value_counts().sort_index()

col1, col2 = st.columns(2)

with col1:
    total_order = len(filtered_order)
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = filtered_order['price'].sum().round(2)
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
st.subheader("Persebaran Wilayah Pembeli ")

map_customer = plot_brazil_map(filtered_customer)

# Display plot in Streamlit
st.pyplot(map_customer)

# Daily Order Items
st.subheader("Order Items")

# Groupby berdasarkan 'product_category_name' dan menjumlahkan 'order_item_id'
result = filtered_orders.groupby('product_category_name')['order_item_id'].sum().reset_index()

# Mengambil 10 terbanyak dan terendah
top_10_sold = result.nlargest(10, 'order_item_id')
bottom_10_sold = result.nsmallest(10, 'order_item_id')

# Menentukan palet warna menggunakan cmap
cmap_top = sns.color_palette("RdBu_r", n_colors=len(top_10_sold))
cmap_bottom = sns.color_palette("RdBu", n_colors=len(bottom_10_sold))

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='order_item_id', y='product_category_name', data=top_10_sold, palette=cmap_top)
ax.set_title('Top 10 Kategori Produk Berdasarkan Jumlah Order')
ax.set_xlabel('Jumlah Order')
ax.set_ylabel('Kategori Produk')
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x='order_item_id', y='product_category_name', data=bottom_10_sold, palette=cmap_bottom)
ax.set_title('Bottom 10 Kategori Produk Berdasarkan Jumlah Order')
ax.set_xlabel('Jumlah Order')
ax.set_ylabel('Kategori Produk')
st.pyplot(fig)

# Daily Rating Produk
st.subheader("Rating Produk")
col1, col2 = st.columns(2)

colors = ['#66b2ff', '#ff6666']

with col1:
    st.markdown(f"Distribusi Rating Produk")

    # Menghitung rata-rata rating untuk setiap product_id
    average_rating_per_product = product_rating.groupby('product_id')['review_score'].mean().round(1)

    value_rating = average_rating_per_product.value_counts()

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Bar plot for rating distribution
    sns.countplot(x=average_rating_per_product, hue=average_rating_per_product >= 4.5, palette={False: colors[0], True: colors[1]}, ax=ax)

    # Set plot labels and title
    ax.set_title('Distribusi Rating Produk')
    ax.set_xlabel('Rating')
    ax.set_ylabel('Jumlah')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)  # Rotate x-axis labels

    # Add legend
    ax.legend(title='Rating', labels=['< 4.5', '>= 4.5'], loc='upper right')

    st.pyplot(fig)

with col2:
    st.markdown(f"Presentase Rating Produk")

    # Membuat dua kategori: Rating > 4.5 dan Rating <= 4.5
    high_ratings = average_rating_per_product[average_rating_per_product >= 4.5]
    low_ratings = average_rating_per_product[average_rating_per_product < 4.5]

    # Menghitung jumlah produk di setiap kategori
    high_ratings_count = len(high_ratings)
    low_ratings_count = len(low_ratings)

    # Membuat data untuk pie chart
    ratings_data = [high_ratings_count, low_ratings_count]
    labels = ['Rating >= 4.5', 'Rating < 4.5']

    # Membuat pie chart
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.pie(ratings_data, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.set_title('Distribusi Rating Produk')
    
    st.pyplot(fig)