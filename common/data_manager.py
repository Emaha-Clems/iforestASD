import os
import pandas as pd
from typing import Dict, Any

class DataManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_stream_index = config['pipeline_runner']['first_point_index']
        self.anomaly_status = {}  
        self.prod_df = self.load_prod_data()

    def initialize_prod_database(self):
        raw_path = os.path.join(self.config['data_manager']['raw_data_folder'], self.config['data_manager']['raw_database_test_name'])
        prod_path = os.path.join(self.config['data_manager']['prod_data_folder'], self.config['data_manager']['prod_database_name'])
        os.makedirs(self.config['data_manager']['prod_data_folder'], exist_ok=True)
        df = pd.read_csv(raw_path)
        df.to_csv(prod_path, index=False)
        # reset anomaly_status
        self.anomaly_status = {}
    
    def load_data(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        df = df.reset_index(drop=True)
        return df

    
    def load_prod_data(self) -> pd.DataFrame:
        path = os.path.join(self.config['data_manager']['prod_data_folder'], self.config['data_manager']['prod_database_name'])
        return pd.read_csv(path)
    
    def load_label_data(self) -> pd.DataFrame:
        label_path = os.path.join(
            self.config['data_manager']['raw_data_folder'],
            self.config['data_manager']['raw_database_label_name']
        )
        df_labels = pd.read_csv(label_path)
        df_labels = df_labels.reset_index(drop=True)
        return df_labels

