#!/usr/bin/env python3
import csv
import pickle

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

    # Предсказываем сорт риса и считаем точность
    raw_predictions = model.predict(X)
    predictions = label_encoder.inverse_transform(raw_predictions)
    probabilities = model.predict_proba(X)

    # Сохраняем результаты
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["Class", "Confidence"])

        for prediction, probability in zip(predictions, probabilities):
            writer.writerow([prediction, round(max(probability) * 100, 2)])

    print(f"Обработано зёрен: {len(predictions)}")
    print(f"Результаты сохранены в {output_file}")


if __name__ == "__main__":
    model = load_model("rice_model.pkl")

    classify(model, "Rice_Cammeo_Osmancik_test.csv", "results.csv")