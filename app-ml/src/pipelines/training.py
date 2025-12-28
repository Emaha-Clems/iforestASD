# pipelines/training.py
import pandas as pd
from typing import Dict, Any
from pysad.models.iforest_asd import IForestASD

class TrainingPipeline:
    def __init__(self, config: Dict[str, Any]):
        self.config = config['iforestASD_params']
        self.model = IForestASD(window_size = self.config.get('window_size'))

    def run(self, df: pd.DataFrame):
       n_init = self.config['initial_window_X']
       for i in range(n_init):
            x = df.iloc[i].to_numpy(dtype=float)
            self.model.fit_partial(x)
       return self.model

