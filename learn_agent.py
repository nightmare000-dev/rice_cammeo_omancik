#!/usr/bin/env python3
import csv
import pickle

from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier


FEATURES = [
    "Area",
    "Perimeter",
    "Major_Axis_Length",
    "Minor_Axis_Length",
    "Eccentricity",
    "Convex_Area",
    "Extent",
]


def load_data(filename):
    X = []
    y = []

    with open(filename, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # Очищаем названия столбцов от пробелов и типов данных
        reader.fieldnames = [
            name.strip().split()[0] for name in reader.fieldnames
        ]

        # Проверяем наличие необходимых столбцов
        required_columns = FEATURES + ["Class"]

        for column in required_columns:
            if column not in reader.fieldnames:
                raise ValueError(f"Отсутствует столбец: {column}")

        for row in reader:
            X.append([float(row[col]) for col in FEATURES])

            y.append(row["Class"].strip())

    return X, y


# Загружаем данные
X, y = load_data("/home/madnessam/Code/hackathon/Rice_Cammeo_Osmancik.csv")

# Кодируем строковые метки классов в числа (0 и 1) для XGBoost
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Разделяем данные на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Создаём модель
model = XGBClassifier(
    n_estimators=150,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss",
)

# Обучаем модель
model.fit(X_train, y_train)

# Проверяем качество
predictions = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, predictions))
print("\nClassification report:")
print(
    classification_report(
        y_test, predictions, target_names=label_encoder.classes_
    )
)

# Сохраняем обученную модель и кодировщик меток
with open("rice_model.pkl", "wb") as file:
    pickle.dump({"model": model, "label_encoder": label_encoder}, file)

print("\nМодель успешно сохранена!")