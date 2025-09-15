import os
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ENV = PROJECT_ROOT / '.env'
load_dotenv(ENV, override=True)


# Environment variables configuration
class Config:
    PROJECT_ROOT = Path(__file__).parent.parent
    MODEL_PATH = PROJECT_ROOT / 'models' / 'model.pt'

    ALERT_COOLDOWN = 45  # Seconds between alerts

    @classmethod
    def validate(cls):
        missing_vars = []
        for var in cls.__dict__:
            if not var.startswith('__') and getattr(cls, var) is None:
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(
                f"Missing environment variables: {', '.join(missing_vars)}"
            )

        cls.DETECTED_FIRES_DIR.mkdir(exist_ok=True)
