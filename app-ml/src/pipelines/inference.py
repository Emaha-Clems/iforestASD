import pandas as pd
import numpy as np
from typing import Dict, Any
from pysad.models.iforest_asd import IForestASD
from pysad.transform.probability_calibration import ConformalProbabilityCalibrator



class InferencePipeline:

    def __init__(self, config: Dict[str, Any]):
        self.config = config['iforestASD_params']
        self.model = IForestASD(window_size = self.config.get('window_size'))
        self.calibrator = ConformalProbabilityCalibrator(windowed=True, window_size=300)
        self._stream_idx = config['pipeline_runner'].get('first_point_index', 0)
        self.anomaly_status = {}

    def run_detection(self, x: pd.DataFrame) -> Dict[str, Any]:
        self._stream_idx += 1
        current_idx = self._stream_idx - 1
        X_point = x.iloc[0].to_numpy(dtype=float) 
        raw_score = self.model.fit_score_partial(X_point)
        raw_score = np.array([raw_score]) 
        calibrated_score = self.calibrator.fit_transform(raw_score)[0]
        is_anomaly = 1 if calibrated_score > self.config.get('decision_threshold', 0.99) else 0
        self.anomaly_status[current_idx] = is_anomaly

        result = {
            "status": "success",
            "stream_index": current_idx,
            "is_anomaly": is_anomaly,
            "final_score": calibrated_score,
            "removed_anomaly_indices": [],
            "anomaly_status": self.anomaly_status.copy()
        }
        return result

