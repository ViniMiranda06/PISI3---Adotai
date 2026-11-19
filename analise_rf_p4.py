import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from imblearn.over_sampling import SMOTE

arquivo = (
    r"C:\Users\Júlio Gabriel\.cache\kagglehub\datasets"
    r"\aaronschlegel\austin-animal-center-shelter-intakes-and-outcomes"
    r"\versions\1\aac_intakes_outcomes.csv"
)

df = pd.read_csv(arquivo)

def categorizar_stay(dias):
    if pd.isna(dias) or dias < 0:
        return "Desconhecido"
    elif dias <= 14:
        return "Curta"
    elif dias <= 45:
        return "Média"
    return "Longa"

df["stay_category"] = df["time_in_shelter_days"].apply(categorizar_stay)

features = [
    "animal_type", "age_upon_intake_(days)", "sex_upon_intake",
    "intake_condition", "intake_type", "intake_month",
    "intake_year", "intake_weekday", "intake_hour"
]

X = df[features].copy()
y = df["stay_category"].copy()

valid_mask = ~y.isna()
X, y = X[valid_mask], y[valid_mask]

X["age_upon_intake_(days)"] = X["age_upon_intake_(days)"].fillna(
    X["age_upon_intake_(days)"].median()
)
X["intake_weekday"] = X["intake_weekday"].fillna("Unknown")
X["intake_hour"] = X["intake_hour"].fillna(X["intake_hour"].median())

categorical_cols = [
    "animal_type", "sex_upon_intake", "intake_condition",
    "intake_type", "intake_weekday"
]
X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)

numeric_features = [
    "age_upon_intake_(days)", "intake_month", "intake_year", "intake_hour"
]
scaler = StandardScaler()
X_encoded[numeric_features] = scaler.fit_transform(X_encoded[numeric_features])

X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=42, stratify=y
)

classes = ["Curta", "Média", "Longa"]

def avaliar(nome, X_tr, y_tr):
    modelo = RandomForestClassifier(
        n_estimators=50, random_state=42, n_jobs=-1
    )
    modelo.fit(X_tr, y_tr)
    pred = modelo.predict(X_test)

    print(f"\n{'=' * 55}")
    print(nome)
    print("Acurácia:", round(accuracy_score(y_test, pred), 6))
    print("\nRelatório por classe:")
    print(classification_report(
        y_test, pred, labels=classes, target_names=classes,
        digits=6, zero_division=0
    ))
    print("Matriz de confusão (linhas = real; colunas = previsto):")
    print(confusion_matrix(y_test, pred, labels=classes))

avaliar("RANDOM FOREST — SEM SMOTE", X_train, y_train)

print("\nAplicando SMOTE ao conjunto de treino...")
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

avaliar("RANDOM FOREST — COM SMOTE", X_train_smote, y_train_smote)
