import sys
import os
from flask import Flask, jsonify
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))
sys.path.append(os.path.join(project_root, 'src'))
sys.path.append(os.path.join(project_root, 'app-ml', 'src'))
os.chdir(project_root)

from common.utils import read_config
from common.data_manager import DataManager
from pipelines.pipeline_runner import PipelineRunner



app = Flask(__name__)

@app.route('/run-inference', methods=['POST'])
def run_inference():
    try:
        idx = data_manager.current_stream_index
        result = pipeline_runner.run_anomaly_detection(idx)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    
    config_path = project_root / 'config' / 'config.yaml'
    config = read_config(config_path)
    data_manager = DataManager(config)
    data_manager.initialize_prod_database()
    pipeline_runner = PipelineRunner(config, data_manager)
    app.run(host="0.0.0.0", port=5001) 
