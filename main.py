from fastapi.responses import FileResponse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import joblib
import pandas as pd
import numpy as np
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load your 3 saved files
model = joblib.load('model_assets/churn_logic_model.pkl')
scaler = joblib.load('model_assets/churn_scaler.pkl')
feature_names = joblib.load('model_assets/feature_columns.pkl')

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join('static', 'favicon.ico')) if os.path.exists('static/favicon.ico') else None

@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(data: dict):
    input_df = pd.DataFrame(0, index=[0], columns=feature_names)
    
    for key, value in data.items():
        if not value: continue
        if key in ['tenure', 'MonthlyCharges', 'TotalCharges']:
            val = float(value)
            input_df[key if key != 'TotalCharges' else 'TotalCharges_log'] = np.log1p(val) if key == 'TotalCharges' else val
        else:
            col = f"{key}_{value}"
            if col in input_df.columns: input_df[col] = 1

    X_scaled = scaler.transform(input_df)
    prob = model.predict_proba(X_scaled)[0][1]
    prediction = 1 if prob > 0.5 else 0

    # Logic for Insights
    if prediction == 1:
        status = "Churn Risk"
        # Custom logic for improvements
        suggestions = []
        if data.get('Contract') == 'Month-to-month':
            suggestions.append("Offer a 1-year contract discount to increase commitment.")
        if data.get('TechSupport') == 'No':
            suggestions.append("Provide a free 3-month trial of Premium Tech Support.")
        if float(data.get('MonthlyCharges', 0)) > 70:
            suggestions.append("Suggest a localized data plan to lower monthly costs.")
        
        reason = "The high monthly charges combined with a short-term contract are the primary drivers for this risk."
        improvement = " ".join(suggestions)
    else:
        status = "Loyal"
        reason = "The customer’s long-term contract and use of security services indicate high satisfaction."
        improvement = "N/A"

    return {
        "churn": prediction,
        "probability": f"{round(prob * 100, 2)}%",
        "reason": reason,
        "improvement": improvement
    }