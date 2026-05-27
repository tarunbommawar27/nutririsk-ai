from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./nutririsk.db"
    model_path: str = "../ml/models/nutririsk_model.joblib"
    feature_columns_path: str = "../ml/models/feature_columns.json"
    demo_data_path: str = "../data/demo/patient_day_features.csv"
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
