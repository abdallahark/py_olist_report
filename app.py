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
# metric styling
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #0f172a, #1f2937);
    padding: 18px 16px;
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.35);
    text-align: center;                
}

.metric-label {
    font-size: 0.1.2rem;
    color: #1f6decff;
    font-weight: 500;
}

.metric-value {
    font-size: 1.8rem;
    color: #1f6decff;  /* main number color */
    font-weight: 700;
    margin-top: 4px;
}

.metric-delta {
    font-size: 0.9rem;
    margin-top: 4px;
    color: #10B981;  /* delta color */
}
</style>
""", unsafe_allow_html=True)

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
    
    st.sidebar.header('filters')
        #filtering by years
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
        orders_df=orders_df[orders_df['order_id'].isin(selected_years_ids)]
        reviews_df=reviews_df[reviews_df['order_id'].isin(selected_years_ids)]
        payments_df=payments_df[payments_df['order_id'].isin(selected_years_ids)]

        #filtering by customer states
    customer_state= sorted(customers_df['customer_state'].unique())
    selected_states=st.sidebar.multiselect(
        "selected customers states",
        options=customer_state,
        default=customer_state[:5]
    )
    if selected_states:
        selected_states_df=customers_df[customers_df['customer_state'].isin(selected_states)]
        customerbystate_ids=selected_states_df['customer_id'].unique()
        orderbystate_df=orders_df[orders_df['customer_id'].isin(customerbystate_ids)]
        orderbystate_ids=orderbystate_df['order_id'].unique()
        # fitering dataframes on selected category
        orders_df=orders_df[orders_df['order_id'].isin(orderbystate_ids)]
        reviews_df=reviews_df[reviews_df['order_id'].isin(orderbystate_ids)]
        payments_df=payments_df[payments_df['order_id'].isin(orderbystate_ids)] 
    #by categories filter
    # Get a sorted list of unique categories for the dropdown
    all_categories = sorted(products_df['product_category_name_english'].unique())
    selected_categories = st.sidebar.multiselect(
        "Select Product Categories",
        options=all_categories,
        default=all_categories[:5]
    )

    if selected_categories:
        categories= products_df[products_df['product_category_name_english'].isin(selected_categories)]
        selected_product_ids=categories["product_id"].unique()
        selected_items=order_items_df[order_items_df['product_id'].isin(selected_product_ids)]
        selected_order_ids=selected_items['order_id'].unique()

        # fitering dataframes on selected category
        orders_df=orders_df[orders_df['order_id'].isin(selected_order_ids)]
        reviews_df=reviews_df[reviews_df['order_id'].isin(selected_order_ids)]
        payments_df=payments_df[payments_df['order_id'].isin(selected_order_ids)]

    ###################################
    # KPIs measures
    st.header('Key Performance Indicator (KPIs)')
    total_revenue= payments_df['payment_value'].sum()
    total_orders= orders_df['order_id'].nunique()
    avg_review_score=reviews_df['review_score'].mean()

    ## KPIs cards 
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Revenue</div>
                <div class="metric-value">$ {total_revenue:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Orders</div>
                <div class="metric-value">{total_orders:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Average Review Score</div>
                <div class="metric-value">{avg_review_score:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

###############################################################################################33
################################################################################################333

    st.header('detailed analysis')
    st.subheader('Monthly Revenue Trend')
    filtered_df= orders_df.merge(payments_df,on='order_id',how='left')
    monthly_revenue = filtered_df.set_index('order_purchase_timestamp').groupby(pd.Grouper(freq='M'))['payment_value'].sum().reset_index()
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
        plot_bgcolor="#343437", 
        paper_bgcolor="#101010",
        font=dict(color="#1C78D5", size=14),
        title_x=0.5,
    )


    fig_revenue.update_xaxes(
        title_font=dict(color="#1C78D5"),
        tickfont=dict(color="#1C78D5")
    )
    fig_revenue.update_yaxes(
        title_font=dict(color="#1C78D5"),
        tickfont=dict(color="#1C78D5")
    )
    fig_revenue.update_traces(line_color="#1C78D5") 

    st.plotly_chart(fig_revenue, use_container_width=True, theme=None)

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Review Score Distribution")
        filtered_df=reviews_df
        review_counts = filtered_df['review_score'].value_counts().sort_index()
        fig_reviews = px.bar(review_counts, x=review_counts.index, y=review_counts.values,
                            title="Distribution of Customer Review Scores",
                            labels={'index': 'Review Score', 'y': 'Number of Orders'},text_auto=True)
        
        fig_reviews.update_layout(
            plot_bgcolor="#7f8298", 
            paper_bgcolor="#7f8298",
            font=dict(color="#1C78D5", size=16),
            title_x=0.5,
        )

        fig_reviews.update_xaxes(
            title_font=dict(color="#1C78D5"),
            tickfont=dict(color="#1C78D5")
        )
        fig_reviews.update_yaxes(
            title_font=dict(color="#1C78D5"),
            tickfont=dict(color="#1C78D5")
        )
        
        st.plotly_chart(fig_reviews, use_container_width=True)
            
    with col6:
        st.subheader("Review Score vs. Delivery Time")
        orders_reviews_df=orders_df.merge(reviews_df,on='order_id',how='left')
        avg_delivery_by_score = orders_reviews_df.groupby(orders_reviews_df['review_score'])['delivery_time_days'].mean().reset_index()
        fig_delivery_review = px.bar(avg_delivery_by_score, x='review_score', y='delivery_time_days',
                                title="Avg. Delivery Time by Review Score",
                                labels={'review_score': 'Review Score', 'delivery_time_days': 'Average Delivery Time (Days)'})
        
        fig_delivery_review.update_layout(
            plot_bgcolor="#7f8298", 
            paper_bgcolor="#7f8298",
            font=dict(color="#1C78D5", size=14),
            title_x=0.5,
        )
        fig_delivery_review.update_xaxes(
            title_font=dict(color="#1C78D5"),
            tickfont=dict(color="#1C78D5")
        )
        fig_delivery_review.update_yaxes(
            title_font=dict(color="#1C78D5"),
            tickfont=dict(color="#1C78D5")
        )
        
        st.plotly_chart(fig_delivery_review, use_container_width=True)


    st.dataframe(orders_df.head())
else:
    print("dataframes are not loaded correctly no data to process")