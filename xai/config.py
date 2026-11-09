import os
from dotenv import load_dotenv
load_dotenv()
MODEL_ID = os.getenv(
    "MODEL_ID",
    "yanami3/agri-plant-disease-resnet50"
)
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

CONFIDENCE_THRESHOLD = float(
    os.getenv(
        "CONFIDENCE_THRESHOLD",
        "0.70"
    )
)
MAX_UPLOAD_MB = int(
    os.getenv(
        "MAX_UPLOAD_MB",
        "5"
    )
)


MAX_UPLOAD_BYTES = (
    MAX_UPLOAD_MB * 1024 * 1024
)




