import pandas as pd

# Step 1: Data exploration
# Loading dataset
df = pd.read_csv("data/Part 2.loan_data_final.csv")
print(df.info())
print(df.head())
print(df.isnull().sum())
print(df.describe())
print(df['loan_status'].value_counts())

# Step 2: Data preprocessing
# Handling missing values
df = df.dropna(subset=['loan_status'])
df['person_age'].fillna(df['person_age']).median(), in_place=True)
df['person_gender'].fillna(df['person_gender']).mode()[0], in_place=True)

# One-hot encoding for categorical columns with more than two categories
df = pd.get_dummies(df, columns=['person_gender', 'person_education', 'loan_intent', 'loan_type', drop_first=True])
# Label encoding for binary categorical features
from sklearn.preprocessing import LabelEncoder
df['loan_status'] = LabelEncoder().fit_transform(df['loan_status'])

# Step 3: Feature engineering
# We can create features for age group as well as credit score ranges, among others
bins = [0, 25, 40, 60, 100]
labels = ['young', 'middle-aged', 'old', 'senior']
df['age_group'] = pd.cut(df['person_age'], bins=bins, labels=labels)
df['credit_score_range'] = pd.cut(df['credit_score'], bins=[0, 600, 700, 800, 850], labels=['poor', 'fair', 'good', 'excellent'])

# Feature interaction can improve model performance
df['loan_income_interaction'] = df['loan_int_rate'] * df['loan_percent_income']

# Step 4: Model training
# Splitting data for training and testing
from sklearn.model_selection import train_test_split
X = df.drop(columns=['loan_status'])
y = df['loan_status']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# We can use Random Forest here
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
model = RandomForestClassifier(random_state = 42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print("Accuracy: ", accuracy_score(y_test, y_pred))
print("Classification Report: ")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Step 5: Model Evaluation
