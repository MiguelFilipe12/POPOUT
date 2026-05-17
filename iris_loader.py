import csv
from ID3 import Node as ID3Node
import random

def discretize(examples, attributes, n_bins=3):
    thresholds_dict = {}
    for attribute in attributes:
        values = [float(example[attribute]) for example in examples]
        
        min_v = min(values)
        max_v = max(values)
        step = (max_v - min_v) / n_bins
        thresholds = [min_v + step * i for i in range(1, n_bins)]
        thresholds_dict[attribute] = thresholds  # ← guardar os thresholds
        
        for example in examples:
            v = float(example[attribute])
            # label mais legível em vez de bin0/bin1/bin2
            if v <= thresholds[0]:
                bin_label = f"<= {thresholds[0]:.2f}"
            elif len(thresholds) > 1 and v <= thresholds[1]:
                bin_label = f"{thresholds[0]:.2f}-{thresholds[1]:.2f}"
            else:
                bin_label = f"> {thresholds[-1]:.2f}"
            example[attribute] = bin_label
    
    return examples, thresholds_dict


def load_iris(filepath):
    examples = []
    with open(filepath, newline='') as f:
        reader = csv.DictReader(f)  # lê o CSV como lista de dicts automaticamente
        for row in reader:
            examples.append({
                "sepallength": row["sepallength"],
                "sepalwidth":  row["sepalwidth"],
                "petallength": row["petallength"],
                "petalwidth":  row["petalwidth"],
                "label":        row["class"]  # coluna target
            })
    
    # Atributos contínuos que precisam de discretização
    attributes = ["sepallength", "sepalwidth", "petallength", "petalwidth"]
    examples, thresholds_dict = discretize(examples, attributes, n_bins=3)
    
    return examples

def split_dataset(examples, test_ratio=0.2):
    examples_copy = examples[:]
    random.shuffle(examples_copy)  # baralhar para garantir aleatoriedade
    split_index = int(len(examples_copy) * (1 - test_ratio))
    train = examples_copy[:split_index]  # 80% para treino
    test  = examples_copy[split_index:]  # 20% para teste
    return train, test

def evaluate(tree, test_examples):
    correct = 0
    for example in test_examples:
        prediction = tree.predict(example)
        if prediction == example["label"]:  # compara previsão com label real
            correct += 1
    return correct / len(test_examples)  # accuracy entre 0 e 1



# 1. Carregar e discretizar
examples = load_iris("iris.csv")
    
# 2. Baralhar e dividir
random.shuffle(examples)
split = int(len(examples) * 0.8)
train = examples[:split]
test  = examples[split:]
print(f"Treino: {len(train)} | Teste: {len(test)}")
    
# 3. Treinar
attributes = ["sepallength", "sepalwidth", "petallength", "petalwidth"]
tree = ID3Node(max_depth=5)
tree.build_tree(train, attributes, depth=0)
    
# 4. Avaliar
correct = sum(1 for ex in test if tree.predict(ex) == ex["label"])
accuracy = correct / len(test)
print(f"Accuracy: {accuracy * 100:.2f}%")
    
# 5. Visualizar
tree.print_tree()
tree.plot_tree()