import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    # Project paths - adjusted for Vercel
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    OUTPUT_DIR: Path = PROJECT_ROOT / "outputs"
    
    # API Configuration - Gemini
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    MODEL_NAME: str = 'gemini-2.5-flash'
    MAX_TOKENS: int = 200
    TEMPERATURE: float = 0.7
    
    # Dataset files
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    COMBINED_DATASET: Path = PROCESSED_DATA_DIR / "combined_prompts.csv"
    
    # Rate limiting
    REQUEST_DELAY: float = 1.0
    
    def __post_init__(self):
        # Create directories if they don't exist
        for directory in [self.OUTPUT_DIR, self.PROCESSED_DATA_DIR, self.RAW_DATA_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
