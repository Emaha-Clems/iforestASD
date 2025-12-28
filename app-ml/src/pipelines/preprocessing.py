import pandas as pd
from typing import Dict, Any

class PreprocessingPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.column_mapping = config['preprocessing'].get('column_mapping', {})
        self.columns_to_drop = config['preprocessing'].get('drop_columns', [])

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # rename only columns present
        rename_map = {k: v for k, v in self.column_mapping.items() if k in df.columns}
        if rename_map:
            df.rename(columns=rename_map, inplace=True)
        # drop requested columns
        drop_list = [c for c in self.columns_to_drop if c in df.columns]
        df.drop(columns=drop_list, errors='ignore', inplace=True)
     
        return df
