#----importing libraries---
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#----helper function----
# create_daily_order_df
def create_daily_order_df(df):
    daily_order_df = df.resample(rule='D', on='order_delivered_carrier_date').agg({
        'order_id':'nunique',
        'price':'sum'
    })
    daily_order_df = daily_order_df.reset_index()
    daily_order_df.rename(columns={
        'order_id':'order_count',
        'price':'revenue'
    },inplace=True)
    return daily_order_df

# create_sum_order_items_df
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby(by='product_category_name_english').order_id.size().sort_values(ascending=False).reset_index()
    sum_order_items_df.rename(columns={
        'product_category_name_english':'product_category',
        'order_id':'quantity'
    },inplace=True)
    return sum_order_items_df

# create_customer_geolocation
def create_customer_geolocation(df):
    customer_geolocation = df.groupby(by=['geolocation_lat','geolocation_lng']).customer_id.size().sort_values(ascending=False).reset_index()
    customer_geolocation.rename(columns={
        'geolocation_lat':'latitude',
        'geolocation_lng':'longitude',
        'customer_id':'number_of_customer'
    },inplace=True) 
    return customer_geolocation

#----load all_data.csv----
all_df = pd.read_csv('C:/Users/Nafi Kareem/OneDrive/Dokumen/Data MIning/Course College/submission/dashboard/all_data_E-Commerce.csv')
 
#----filter keys----
datetime_columns = ['order_delivered_carrier_date','order_delivered_customer_date','shipping_limit_date',]
all_df.sort_values(by='order_delivered_carrier_date',inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

#----filters components---
min_date = all_df['order_delivered_carrier_date'].min()
max_date = all_df['order_delivered_carrier_date'].max()
 
with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Time Span',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# stored into main_df
main_df = all_df[(all_df["order_delivered_carrier_date"] >= str(start_date)) & 
                (all_df["order_delivered_carrier_date"] <= str(end_date))]

# calling helper function
daily_order_df = create_daily_order_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
customer_geolocation = create_customer_geolocation(main_df)

#-dashboard header
st.header('Data Science Dashboard 📉')

#-dashboard subheader
#total order dan revenue
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_order_df.shape[0]
    st.metric('Total Orders', value=total_orders)

with col2:
    total_revenue = format_currency(daily_order_df.revenue.sum(),'AUD',locale='es_CO')
    st.metric('Total Revenue',value=total_revenue)

fig, ax = plt.subplots(figsize=(16,8))
ax.plot(
    daily_order_df['order_delivered_carrier_date'],
    daily_order_df['order_count'],
    marker='o',
    linewidth=2,
    color='red'
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#product categories sales
st.subheader('Product Categories Sales')

fig, ax = plt.subplots(nrows=1,ncols=2,figsize=(35,15))

colors = ['red','rosybrown','rosybrown','rosybrown','rosybrown','rosybrown','rosybrown','rosybrown','rosybrown','rosybrown']

sns.barplot(x='quantity',y='product_category',data=sum_order_items_df.head(10),palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel('Number of Sales', fontsize=30)
ax[0].set_title('The Most Sold Product Categories', loc='center',fontsize=50)
ax[0].tick_params(axis='y',labelsize=35)
ax[0].tick_params(axis='x',labelsize=30)

sns.barplot(x='quantity',y='product_category',data=sum_order_items_df.sort_values(by='quantity',ascending=True).head(10),palette=colors,ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('Number of Sales', fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].set_title('The Least Sold Products Categories', loc='center', fontsize=50)
ax[1].tick_params(axis='y',labelsize=35)
ax[1].tick_params(axis='x',labelsize=30)

st.pyplot(fig)

#customer distribution plot
st.subheader('Customer Distribution')

fig, ax = plt.subplots(figsize=(16,8))

plt.scatter(customer_geolocation['longitude'],customer_geolocation['latitude'],s=20,alpha=0.5)
ax.set_title('Customer Distribution',fontsize=30)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)

# customer density heatmap
st.subheader('Customer Density Heatmap')
customer_geolocation.drop(columns='number_of_customer',axis=1,inplace=True)

fig, ax = plt.subplots(figsize=(16,8))

sns.heatmap(customer_geolocation)
ax.set_title('Customer Density',fontsize=30)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=15)
st.pyplot(fig)