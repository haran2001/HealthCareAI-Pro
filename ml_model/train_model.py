# ml_model/train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

# Sample data
data = {
    "age": [25, 30, 45, 35, 50, 23, 40, 60, 55, 38],
    "gender": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],  # 1: Male, 0: Female
    "risk": [0, 0, 1, 0, 1, 0, 1, 1, 1, 0],  # 1: High Risk, 0: Low Risk
}

df = pd.DataFrame(data)

X = df[["age", "gender"]]
y = df["risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LogisticRegression()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, "ml_model/model.pkl")

print("Model trained and saved as model.pkl")
