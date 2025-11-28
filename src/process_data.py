import os 
import glob
import pandas as pd
import numpy as np

# configration variables 
DATA_DIR = 'data'
DATA_FRAME='dataframe'
 
def processing_data()->dict:
    # reading csv files after extracting 
    extracted_files= glob.glob(os.path.join(DATA_DIR,'*.csv'))
    dataframes= {}
    if not extracted_files:
        print('no csv files in data folder')
    
    else:
        for file in extracted_files:
            table_name= os.path.basename(file).replace('olist_','').replace('_dataset','').replace('.csv','')
            df= pd.read_csv(file)
            dataframes[table_name]=df
            print(f'reading {table_name}: {df.shape}')

        return dataframes

def cleaning_data(dataframes):

  # changing the type date related columns to a datetime 
  data_columns=["order_purchase_timestamp",'order_approved_at','order_delivered_customer_date','order_delivered_carrier_date','order_estimated_delivery_date']
  for column in data_columns:
    dataframes['orders'][column]=pd.to_datetime(dataframes['orders'][column])

  # translating product category 
  dataframes['products']= dataframes['products'].merge(dataframes['product_category_name_translation'],on='product_category_name',how='left')
  dataframes['products']= dataframes['products'].drop(columns='product_category_name')
  #dropping columns
  reviews_cols_to_drop=['review_comment_title','review_comment_message','review_creation_date','review_answer_timestamp']
  dataframes['order_reviews']=dataframes['order_reviews'].drop(columns=reviews_cols_to_drop, errors='ignore')

  #handling missing data
  dataframes['products']['product_category_name_english']=dataframes['products']['product_category_name_english'].fillna('unknown')

  # Feature Engineering stage
  dataframes['orders']['delivery_time_days']=(dataframes['orders']['order_delivered_customer_date']-dataframes['orders']['order_purchase_timestamp']).dt.days
  dataframes['orders']['delivery_diff_days']=(dataframes['orders']['order_estimated_delivery_date']-dataframes['orders']['order_delivered_customer_date']).dt.days

  # delivery status column depends on the values of delvery_diff_days
  conditions = [
    dataframes['orders']['delivery_diff_days'].isnull(),        
    dataframes['orders']['delivery_diff_days'] < 0,             
    dataframes['orders']['delivery_diff_days'] >= 0             
    ]
  choices = [
    'In Transit/Cancelled',
    'Delayed',
    'On Time'
  ]
  dataframes['orders']['delivery_status'] = np.select(conditions, choices, default='Error')
  
    # Extract year, month, and day of week from purchase timestamp for time-series analysis
  dataframes['orders']['purchase_year'] = dataframes['orders']['order_purchase_timestamp'].dt.year
  dataframes['orders']['purchase_month'] = dataframes['orders']['order_purchase_timestamp'].dt.month
  dataframes['orders']['purchase_dayofweek'] = dataframes['orders']['order_purchase_timestamp'].dt.day_name()  
  return dataframes

if __name__=="__main__":
    dataframes=processing_data()
     
    final_dataframes=cleaning_data(dataframes)
    if final_dataframes is not None:
        for filename, df in final_dataframes.items():
           df.to_csv(os.path.join(DATA_FRAME,f'{filename}.csv'),index=False,header=True)
    else:
        print('error happened master data frame is impty')    
    





