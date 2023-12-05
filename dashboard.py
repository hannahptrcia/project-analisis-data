import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df


def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bycity_df

def create_rfm_df(df):
    rfm = df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "price": "sum"
    })
    rfm.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm["max_order_timestamp"] = rfm["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm["recency"] = rfm["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm

df = pd.read_csv("Hasil Analisis.csv")

datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
df.sort_values(by="order_purchase_timestamp", inplace=True)
df.reset_index(inplace=True)
for column in datetime_columns:
    df[column] = pd.to_datetime(df[column])

min_date = df["order_purchase_timestamp"].min()
max_date = df["order_purchase_timestamp"].max()

with st.sidebar:

    st.title("Laporan Hasil Penjualan")

    st.image("https://www.pngkit.com/png/detail/253-2533001_shopping-cart-logo-ecommerce-design-solutions.png")
    
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = df[(df["order_purchase_timestamp"] >= str(start_date)) & 
            (df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
bycity_df = create_bycity_df(main_df)
rfm = create_rfm_df(main_df)

st.header('Dashboard')

st.set_option('deprecation.showPyplotGlobalUse', False)

st.subheader('Grafik Penjualan Per Bulan')
order_per_bulan = df.resample(rule='M', on='order_purchase_timestamp').agg({
    "order_id":"nunique"
})
order_per_bulan.index = order_per_bulan.index.strftime('%Y-%m')
order_per_bulan = order_per_bulan.reset_index()
order_per_bulan.rename(columns={
    "order_id": "order_count"
}, inplace=True)
plt.figure(figsize=(10, 5))
plt.plot(order_per_bulan["order_purchase_timestamp"], order_per_bulan["order_count"],  linewidth=1.5, color="#72BCD4")
plt.title("Jumlah Orderan Per Bulan", loc="center", fontsize=20)
plt.xticks(fontsize=10, rotation=45, ha='right')
plt.yticks(fontsize=10)
plt.ylabel('Jumlah Order')
plt.xlabel('Bulan Pembelian')
st.pyplot()


st.subheader('Kategori Produk yang Paling Sering dan Jarang Dibeli')

col1, col2 = st.columns(2)

with col1:
    df.product_category_name.value_counts().nlargest(10).plot(kind='bar', figsize=(10,5))
    plt.title('Kategori Produk yang Paling Sering Dibeli')
    plt.ylabel('Jumlah Produk')
    plt.xlabel('Kategori Produk')
    
    st.pyplot()

with col2:
    df.product_category_name.value_counts().nsmallest(10).plot(kind='bar', figsize=(10,5))
    plt.title('Kategori Produk yang Paling Jarang Dibeli')
    plt.ylabel('Jumlah Produk')
    plt.xlabel('Kategori Produk')
    st.pyplot()


st.subheader('Analisis RFM (Recency, Frequency, dan Monetary)')

rfm = df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "price": "sum"
})
rfm.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

rfm["max_order_timestamp"] = rfm["max_order_timestamp"].dt.date
recent_date = df["order_purchase_timestamp"].dt.date.max()
rfm["recency"] = rfm["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm.monetary.mean(), "BRL", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 

rfm.drop("max_order_timestamp", axis=1, inplace=True)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="customer_id", data=rfm.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel("Recency", fontsize=14)
ax[0].set_xlabel("Customer ID", fontsize=14)
ax[0].set_xticklabels(ax[0].get_xticklabels(),rotation=90)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)

sns.barplot(y="frequency", x="customer_id", data=rfm.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel("Frequency", fontsize=14)
ax[1].set_xlabel("Customer ID", fontsize=14)
ax[1].set_xticklabels(ax[0].get_xticklabels(),rotation=90)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="customer_id", data=rfm.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel("Monetary", fontsize=14)
ax[2].set_xlabel("Customer ID", fontsize=14)
ax[2].set_xticklabels(ax[0].get_xticklabels(),rotation=90)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
 
st.pyplot()


st.set_option('deprecation.showPyplotGlobalUse', False)