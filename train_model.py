import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Load the dataset
# Make sure blood.csv is in the same directory or provide the correct path
df = pd.read_csv('blood.csv')

# Rename columns to remove spaces/newlines if any, and make them easier to work with
df.columns = ['Recency', 'Frequency', 'Monetary', 'Time', 'Target']

# 2. Define Features (X) and Target (y)
X = df[['Recency', 'Frequency', 'Monetary', 'Time']]
y = df['Target']

# 3. Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize and train the Random Forest Classifier
print("Training the model...")
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)

# 5. Evaluate the model
y_pred = model.predict(X_test)
print("\n--- Model Evaluation ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
print(classification_report(y_test, y_pred))

# 6. Save the trained model so Django can use it
model_filename = 'donor_prediction_model.pkl'
joblib.dump(model, model_filename)
print(f"\nModel saved successfully as {model_filename}")