import pandas as pd
import numpy as np
import random
from datetime import datetime
from collections import Counter
import sys

# ==========================================
# 1. Загрузка датасета
# ==========================================

FEATURES = [
  "Area",
  "Perimeter",
  "Major_Axis_Length",
  "Minor_Axis_Length",
  "Eccentricity",
  "Convex_Area",
  "Extent"
]

data = pd.read_pickle('src\\data.pickle')

X = data[FEATURES].to_numpy(dtype=float)
y = data['Class'].to_numpy()

print("Количество образцов:", len(X))
print("Количество признаков:", len(FEATURES))
print("Классы:", np.unique(y))

# ==========================================
# 2. Разделение на обучающую и тестовую выборки
# ==========================================

def split_dataset(X, y, test_size=0.2):
  random.seed(42)

  train_indices = []
  test_indices = []
  for class_name in np.unique(y):
    indices = np.where(y == class_name)[0].tolist()
    random.shuffle(indices)
    split_idx = int(len(indices) * (1 - test_size))
    train_indices.extend(indices[:split_idx])
    test_indices.extend(indices[split_idx:])

  random.shuffle(train_indices)
  random.shuffle(test_indices)

  return (
    X[train_indices],
    X[test_indices],
    y[train_indices],
    y[test_indices],
  )


X_train, X_test, y_train, y_test = split_dataset(X, y, test_size=0.2)

# ==========================================
# 3. Нормализация данных
# ==========================================

# Средние значения и стандартные отклонения
# вычисляются только на обучающей выборке.

mean = np.mean(X_train, axis=0)
std = np.std(X_train, axis=0)

# Защита от деления на ноль
std[std == 0] = 1

X_train = (X_train - mean) / std
X_test = (X_test - mean) / std


# ==========================================
# 4. Реализация алгоритма KNN
# ==========================================

class KNN:
  def __init__(self, k=5):
    self.k = k
    self.X_train = None
    self.y_train = None

  # Обучение модели
  def fit(self, X, y):
    self.X_train = X
    self.y_train = y

  # Вычисление евклидова расстояния
  def euclidean_distance(self, x1, x2):
    return np.sqrt(np.sum((x1 - x2) ** 2))

  # Классификация одного объекта
  def predict_one(self, x):
    distances = []

    for i in range(len(self.X_train)):
      distance = self.euclidean_distance(
        x, self.X_train[i]
      )

      distances.append((distance, self.y_train[i]))

    # Сортировка по расстоянию
    distances.sort(key=lambda item: item[0])

    # Выбираем k ближайших соседей
    neighbors = distances[:self.k]

    # Подсчёт голосов каждого класса
    votes = Counter(
      neighbor[1] for neighbor in neighbors
    )

    # Определяем наиболее частый класс
    return votes.most_common(1)[0][0]

  # Классификация набора объектов
  def predict(self, X):
    predictions = []

    for x in X:
      predictions.append(self.predict_one(x))

    return np.array(predictions)

# ==========================================
# 5. Обучение и классификация
# ==========================================

model = KNN(k=5)
model.fit(X, y)

def classify(params):
    x = [float(params[key]) for key in FEATURES]
    y_pred = model.predict(x)

# ==========================================
# 6. Оценка качества классификации
# ==========================================

def calculate_metrics(y_true, y_pred):
  classes = np.unique(y_true)

  correct = np.sum(y_true == y_pred)
  accuracy = correct / len(y_true)

  print("\nРЕЗУЛЬТАТЫ КЛАССИФИКАЦИИ")
  print("-" * 45)

  print(f"Точность (%): {accuracy * 100:.2f}%")
  print("Метрики по классам:")

  for cls in classes:
    tp = np.sum((y_true == cls) & (y_pred == cls))
    fp = np.sum((y_true != cls) & (y_pred == cls))
    fn = np.sum((y_true == cls) & (y_pred != cls))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if (precision + recall) > 0:
      f1 = 2 * (precision * recall) / (precision + recall)
    else:
      f1 = 0.0

    print(f'  Сорт:', cls)
    print(f'    Определено правильно:', tp)
    print(f'    Сорт другой, но определен этот:', fp)
    print(f'    Сорт этот, но определен другой:', fn)
    print(f'    Precision:', round(precision, 2))
    print(f'    Recall:', round(recall, 2))
    print(f'    F1-score:', round(f1, 2))

  return accuracy

# ==========================================
# 7. Определение значимости признаков
#    методом перестановочной важности
# ==========================================

def permutation_importance(model, X_test, y_test, feature_names):
  print("\nВАЖНОСТЬ ПРИЗНАКОВ")
  print("-" * 45)

  np.random.seed(42)
  for i, name in enumerate(feature_names):
    X_permuted = X_test.copy().T
    np.random.shuffle(X_permuted[i])
    X_permuted = X_permuted.T

    new_accuracy = np.sum(model.predict(X_permuted) == y_test) / len(y_test)
    print(f'{name}: {accuracy * 100:.2f} -> {new_accuracy * 100:.2f}')
