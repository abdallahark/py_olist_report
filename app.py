import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.express as px
import os
import glob
import plotly.graph_objects as go

st.set_page_config(
    page_title="Olist E-commerce Analysis",
    page_icon="later",
    layout="wide",
    initial_sidebar_state="expanded"
)
######################################################################
def format_numbers(value, decimals=0):
    abs_v = abs(value)

    if abs_v >= 1_000_000:
        value /= 1_000_000
        suffix = "M"
    elif abs_v >= 1_000:
        value /= 1_000
        suffix = "K"
    else:
        suffix = ""

    num_str = f"{value:.{decimals}f}".rstrip("0").rstrip(".")
    return f" {num_str}{suffix}"
######################################################################
# metric styling
def load_css(file_path):
    with open(file_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css("src/css/styles.css")
######################################################################

DATA_DIR='dataframe'
@st.cache_data
def load_data(DATA_DIR)->dict:
    # reading csv files after extracting 
    extracted_files= glob.glob(os.path.join(DATA_DIR,'*.csv'))
    dataframes= {}
    if not extracted_files:
        print('no csv files in data folder')
    
    else:
        for file in extracted_files:
            table_name= os.path.basename(file).replace('.csv','')
            df= pd.read_csv(file)
            dataframes[table_name]=df

            print(f'reading {table_name}: {df.shape}') 
              # changing the type date related columns to a datetime 
        data_columns=["order_purchase_timestamp",'order_approved_at','order_delivered_customer_date','order_delivered_carrier_date','order_estimated_delivery_date']
        for column in data_columns:
          dataframes['orders'][column]=pd.to_datetime(dataframes['orders'][column])     
        return dataframes

# web page setup 
st.title("Olist E-commerce Performance Dashboard")
st.markdown("An interactive dashboard to analyze sales, customer satisfaction, and logistics.")

# filtering by product category
df= load_data(DATA_DIR)

if df is not None:
    #reading unfiltered dataframes
    orders_df=df['orders']
    customers_df=df['customers']
    reviews_df=df['order_reviews']
    payments_df=df['order_payments']
    products_df=df['products']
    order_items_df=df['order_items']
    geolocation_df=df['geolocation']
    orders_customers_df=pd.merge(orders_df,customers_df,on='customer_id',how='left')
    
    st.sidebar.header('filters')
#filtering by years:
    years= sorted(orders_df['purchase_year'].unique())
    selected_years=st.sidebar.multiselect(
        "selected years",
        options=years,
        default=years
    )
    if selected_years:
        selected_years_df=orders_df[orders_df['purchase_year'].isin(selected_years)]
        selected_years_ids=selected_years_df['order_id'].unique()
        
        # fitering dataframes on selected years
        orders_customers_df=orders_customers_df[orders_customers_df['order_id'].isin(selected_years_ids)]
        reviews_df=reviews_df[reviews_df['order_id'].isin(selected_years_ids)]
        payments_df=payments_df[payments_df['order_id'].isin(selected_years_ids)]

#filtering by customer states:
    customer_state= sorted(orders_customers_df['customer_state'].unique())
    selected_states=st.sidebar.multiselect(
        "selected customers states",
        options=customer_state,
        #default=customer_state[:5]
    )
    if selected_states:
        selected_states_df=orders_customers_df[orders_customers_df['customer_state'].isin(selected_states)]
        orderbystate_ids=selected_states_df['order_id'].unique()

        # fitering dataframes on selected customer state
        orders_customers_df=orders_customers_df[orders_customers_df['order_id'].isin(orderbystate_ids)]
        reviews_df=reviews_df[reviews_df['order_id'].isin(orderbystate_ids)]
        payments_df=payments_df[payments_df['order_id'].isin(orderbystate_ids)]

#Filtering by product category:
    # Get a sorted list of unique categories for the dropdown
    all_categories = sorted(products_df['product_category_name_english'].unique())
    selected_categories = st.sidebar.multiselect(
        "Select Product Categories",
        options=all_categories,
        default=all_categories[:10]
    )

    if selected_categories:
        categories= products_df[products_df['product_category_name_english'].isin(selected_categories)]
        selected_product_ids=categories["product_id"].unique()
        selected_items=order_items_df[order_items_df['product_id'].isin(selected_product_ids)]
        selected_order_ids=selected_items['order_id'].unique()

        # fitering dataframes on selected category
        orders_customers_df=orders_customers_df[orders_customers_df['order_id'].isin(selected_order_ids)]
        reviews_df=reviews_df[reviews_df['order_id'].isin(selected_order_ids)]
        payments_df=payments_df[payments_df['order_id'].isin(selected_order_ids)]

###################################
# KPIs measures
    st.header('Executive Summary ')
    total_orders= orders_customers_df['order_id'].nunique()
    total_Customers=orders_customers_df['customer_unique_id'].nunique()
    avg_review_score=reviews_df['review_score'].mean()
    ontime_delivery_rate=(orders_customers_df['order_status']=='delivered').mean()*100
    total_revenue= payments_df['payment_value'].sum()

    ## KPIs cards 
    col1, col2, col3, col4, col5 = st.columns(5)
 
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Orders</div>
                <div class="metric-value">{format_numbers(total_orders)}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">total customers</div>
                  <div class="metric-value">{format_numbers(total_Customers)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">On-time Delivery</div>
                <div class="metric-value">{ontime_delivery_rate:.2f} %</div>
            </div>
        """, unsafe_allow_html=True)
       
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Average Review Score</div>
                <div class="metric-value">{format_numbers(avg_review_score,2)}</div>
            </div>
        """, unsafe_allow_html=True)
               
    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Average Review Score</div>
                <div class="metric-value">{format_numbers(total_revenue,2)}</div>
            </div>
        """, unsafe_allow_html=True)

###############################################################################################33
################################################################################################333
 
    st.subheader('Monthly Revenue Trend')
    filtered_df= orders_df.merge(payments_df,on='order_id',how='left')
    monthly_revenue = filtered_df.set_index('order_purchase_timestamp').groupby(pd.Grouper(freq='ME'))['payment_value'].sum().reset_index()
    monthly_revenue['order_purchase_timestamp'] = monthly_revenue['order_purchase_timestamp'].dt.strftime('%Y-%m')

    fig_revenue = px.line(
        monthly_revenue,
        x='order_purchase_timestamp',
        y='payment_value', 
        title="Total Revenue per Month",
        markers=True,
        labels={'order_purchase_timestamp': 'Month', 'payment_value': 'Revenue (R$)'}
    )

    fig_revenue.update_layout(
        plot_bgcolor="#8eb2eb", 
        paper_bgcolor="#101010",
        font=dict(color="#1C78D5", size=14)
    )


    fig_revenue.update_xaxes(
        title_font=dict(color="#8eb2eb"),
        tickfont=dict(color="#8eb2eb")
    )
    fig_revenue.update_yaxes(
        title_font=dict(color="#8eb2eb"),
        tickfont=dict(color="#8eb2eb")
    )
    fig_revenue.update_traces(line_color="#1C78D5") 

    st.plotly_chart(fig_revenue, width='stretch', theme=None)

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Review Score Distribution")
        filtered_df=reviews_df
        review_counts = filtered_df['review_score'].value_counts().sort_index()
        fig_reviews = px.bar(review_counts, x=review_counts.index, y=review_counts.values,
                            labels={'index': 'Review Score', 'y': 'Number of Orders'},text_auto=True)
        
        fig_reviews.update_layout(
            plot_bgcolor="#5c6bdf", 
            paper_bgcolor="#1a1a1c",
            font=dict(color="#1B2426", size=16)
        )

        fig_reviews.update_xaxes(
            title_font=dict(color="#8eb2eb"),
            tickfont=dict(color="#8eb2eb"),
        )
        fig_reviews.update_yaxes(
            title_font=dict(color="#8eb2eb"),
            tickfont=dict(color="#8eb2eb")
        )
        
        st.plotly_chart(fig_reviews, width='stretch')
            
    with col6:
        st.subheader("Review Score vs. Delivery Time")
        orders_reviews_df=orders_df.merge(reviews_df,on='order_id',how='left')
        avg_delivery_by_score = orders_reviews_df.groupby(orders_reviews_df['review_score'])['delivery_time_days'].mean().reset_index()
        fig_delivery_review = px.bar(avg_delivery_by_score, x='review_score', y='delivery_time_days',
                                labels={'review_score': 'Review Score', 'delivery_time_days': 'Average Delivery Time (Days)'},text_auto=True)
        
        fig_delivery_review.update_layout(
            plot_bgcolor="#5f71f9", 
            paper_bgcolor="#1A1A1D",
            font=dict(color="#02080E", size=14)
        )
        fig_delivery_review.update_xaxes(
            title_font=dict(color="#8eb2eb"),
            tickfont=dict(color="#8eb2eb")
        )
        fig_delivery_review.update_yaxes(
            title_font=dict(color="#8eb2eb"),
            tickfont=dict(color="#8eb2eb")
        )
        
        st.plotly_chart(fig_delivery_review, width='stretch')


    # Merge customers with geolocation by zip code prefix
    geo_zip = (
     geolocation_df
     .groupby('geolocation_zip_code_prefix', as_index=False)
     .agg(
        geolocation_lat=('geolocation_lat', 'mean'),
        geolocation_lng=('geolocation_lng', 'mean'),
        geolocation_city=('geolocation_city', 'first'),
        geolocation_state=('geolocation_state', 'first'),
        )
    )

    orders_customers_geo = orders_customers_df.merge(
        geo_zip,
        left_on='customer_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    )
    orders_by_location = (
        orders_customers_geo
        .groupby(['geolocation_lat', 'geolocation_lng', 'geolocation_city', 'geolocation_state'])
        .agg(
         total_orders=('order_id', 'nunique')
        )
        .reset_index()
    )

    orders_by_location = orders_by_location.dropna(subset=['geolocation_lat', 'geolocation_lng'])
    orders_by_location['geolocation_lat'] = orders_by_location['geolocation_lat'].astype(float)
    orders_by_location['geolocation_lng'] = orders_by_location['geolocation_lng'].astype(float)

    center_lat = orders_by_location['geolocation_lat'].mean()
    center_lon = orders_by_location['geolocation_lng'].mean()

    fig_map = px.scatter_mapbox(
        orders_by_location,
        lat="geolocation_lat",
        lon="geolocation_lng",
        size="total_orders",
        color="total_orders",
        hover_name="geolocation_city",
        hover_data={"total_orders": True, "geolocation_state": True},
        zoom=4,
        height=500,
        color_continuous_scale="Viridis",
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": center_lat, "lon": center_lon},
        margin=dict(l=0, r=0, t=40, b=0),
        title="Orders by Customer Location",
    )

    st.plotly_chart(fig_map, use_container_width=True, theme=None)

else:
    print("dataframes are not loaded correctly no data to process")