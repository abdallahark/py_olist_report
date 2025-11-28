import os 
import pandas as pd
import zipfile
import requests

#configrations  
DATASET_URL = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce"
DATA_DIR    = 'data'
DATA_FILE   = os.path.join(DATA_DIR,'olist_dataset.zip')
DATA_FRAME_DIR  ='dataframe'


#this function reads dataset from provided url 
def load_data(url):
    '''
    downloading olist dataset from like, unzip file content and clean files names return a dictionary with table names and data frames 
    '''
    # creating data directory 
    if not os.path.exists(DATA_DIR):
        os.makedirs('data')
    else:
        print('data file exists')    
    try: 
        if not os.path.exists(DATA_FILE):
            print('downloading dataset...')
            response= requests.get(url, stream=True)
            response.raise_for_status()
            with open(DATA_FILE,'wb') as f:
                for chunck in response.iter_content(chunk_size=8192):
                    f.write(chunck)
    except requests.exceptions.RequestException as e:
        print(f'Error loading data {e}')
        return
    try:
        with zipfile.ZipFile(DATA_FILE,'r') as zf:
            zf.extractall(DATA_DIR)
    except zipfile.BadZipFile as e:
        print(f'unable to extract files {e}')
        return
    try:
        os.remove(DATA_FILE)
    except OSError as e:
        print(f'errer deleting zipfile {e}')

    
if __name__=='__main__':
    
    load_data(DATASET_URL)
