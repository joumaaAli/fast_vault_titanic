from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import joblib  # To load the model
from app.database import get_db
from app.auth.utils import get_current_user
from app.common.models import User, PredictionInput

router = APIRouter()

# Load the trained model at the start
model = joblib.load("model.joblib")

@router.post("/predict/")
async def predict(input_data: PredictionInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Convert the input data to a DataFrame
    input_df = pd.DataFrame([input_data.model_dump()])

    # Use the loaded model to make predictions
    prediction = model.predict(input_df)

    # Assuming binary classification, return a meaningful label
    prediction_label = "Survived" if prediction[0] == 1 else "Did not survive"

    return {"prediction": prediction_label}

