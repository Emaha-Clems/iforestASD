from typing import Dict, Any
from common.data_manager import DataManager
from pipelines.preprocessing import PreprocessingPipeline
from pipelines.training import TrainingPipeline
from pipelines.inference import InferencePipeline

class PipelineRunner:

    def __init__(self, config: Dict[str, Any], data_manager: DataManager):
        """
        Initialize the pipeline runner and its pipeline components.

        Args:
            config (Dict[str, Any]): Dictionary containing all pipeline configurations.
            data_manager (DataManager): Instance for managing I/O operations on data.
        """

        self.config = config
        self.data_manager = data_manager

        # Initialize individual pipeline components
        self.preprocessing_pipeline = PreprocessingPipeline(config)
        self.training_pipeline = TrainingPipeline(config)  
        self.inference_pipeline = InferencePipeline(config)

        # Load existing production database
        df = self.data_manager.prod_df
        df_pre = self.preprocessing_pipeline.run(df)
        self.training_pipeline.run(df_pre)
        self.inference_pipeline.model = self.training_pipeline.model


    
    def run_training(self):
   
        df = self.data_manager.prod_df
        df_pre = self.preprocessing_pipeline.run(df)
        self.training_pipeline.run(df_pre)
        return
    

    def run_anomaly_detection(self, idx: int) -> Dict[str, Any]:      
        df_point = self.data_manager.prod_df.iloc[[idx]]
        df_pre = self.preprocessing_pipeline.run(df_point)
        result = self.inference_pipeline.run_detection(df_pre)
        self.data_manager.anomaly_status = result["anomaly_status"]
        self.data_manager.current_stream_index += 1

        return result