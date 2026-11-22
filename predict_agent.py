#!/usr/bin/env python3

import csv
import pickle
import numpy as np

FEATURES = [
    "Area",
    "Perimeter",
    "Major_Axis_Length",
    "Minor_Axis_Length",
    "Eccentricity",
    "Convex_Area",
    "Extent",
]

def load_model(filename):
    with open(filename, "rb") as file:
        return pickle.load(file)


def classify(model_data, input_file, output_file):
    X = []

    with open(input_file, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # Нормализуем названия столбцов
        reader.fieldnames = [
            name.strip().split()[0] for name in reader.fieldnames
        ]

        for column in FEATURES:
            if column not in reader.fieldnames:
                raise ValueError(f"Отсутствует столбец: {column}")

        for row in reader:
            X.append([float(row[col]) for col in FEATURES])

    if not X:
        print("Файл не содержит данных.")
        return

    # Извлекаем модель и кодировщик меток
    model = model_data["model"]
    label_encoder = model_data["label_encoder"]

    X = np.array(X, dtype=float)

    print("Тип модели:", type(model).__name__)

    # Классификация
    raw_predictions = model.predict(X)

    predictions = label_encoder.inverse_transform(
        raw_predictions.astype(int)
    )

    # Получаем вероятности принадлежности к классам
    probabilities = model.predict_proba(X)

    # Сохраняем результаты классификации
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["Class", "Confidence"])

        for prediction, probability in zip(predictions, probabilities):
            writer.writerow([
                prediction,
                round(float(max(probability)) * 100, 2)
            ])

    print(f"\nОбработано зёрен: {len(predictions)}")
    print(f"Результаты сохранены в {output_file}")


if __name__ == "__main__":
    model_data = load_model("rice_model.pkl")

    classify(
        model_data,
        "/home/madnessam/Code/hackathon/Rice_Cammeo_Osmancik_test_with_class.csv",
        "results.csv"
    )