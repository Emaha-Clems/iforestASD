import os
import sys
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
os.chdir(project_root)
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'app-ml' / 'src'))

from common.utils import read_config, make_prediction_figures
from pipelines.pipeline_runner import PipelineRunner
from common.data_manager import DataManager


if __name__ == "__main__":

    num_points = 200

    config_path = project_root / 'config' / 'config.yaml'
    config = read_config(config_path)

    data_manager = DataManager(config)
    data_manager.initialize_prod_database()

    pipeline_runner = PipelineRunner(config=config, data_manager=data_manager)

    df = data_manager.prod_df

    for i in range(num_points):
        print(f"Processing point {i+1}/{num_points} (index={i})")
        pipeline_runner.run_anomaly_detection(i)

    print("Inference completed for all points!")

    gt_labels = data_manager.load_label_data()
    det_labels = data_manager.anomaly_status

    make_prediction_figures(
        df_prod=df,
        df_labels=gt_labels,
        anomaly_status=det_labels,
        features= ["feature_1"]
    )

