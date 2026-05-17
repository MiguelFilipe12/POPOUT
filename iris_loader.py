import csv
import math
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
            
            if v <= thresholds[0]:
                bin_label = f"<= {thresholds[0]:.2f}"
            elif len(thresholds) > 1 and v <= thresholds[1]:
                bin_label = f"{thresholds[0]:.2f}-{thresholds[1]:.2f}"
            else:
                bin_label = f"> {thresholds[-1]:.2f}"
            example[attribute] = bin_label
    
    return examples, thresholds_dict

def entropy(subset):
    n = len(subset)
    if n == 0: return 0
    c = {}
    for e in subset: c[e["label"]] = c.get(e["label"], 0) + 1
    return -sum((v/n) * math.log2(v/n) for v in c.values() if v > 0)

def find_best_split(examples, attribute):
    values = sorted(set(float(e[attribute]) for e in examples))
    
    if len(values) == 1:
        return None, 0
    
    best_thresh = None
    best_gain   = -1
    
    # calcular entropia antes do corte
    labels = [e["label"] for e in examples]
    total  = len(labels)
    count  = {}
    for l in labels:
        count[l] = count.get(l, 0) + 1
    entropy_before = -sum((c/total) * math.log2(c/total) for c in count.values() if c > 0)
    
    # testar cada ponto de SPLIT entre valores consecutivos
    for i in range(len(values) - 1):
        thresh = (values[i] + values[i+1]) / 2
        left  = [e for e in examples if float(e[attribute]) <= thresh]
        right = [e for e in examples if float(e[attribute]) >  thresh]
        

        
        gain = entropy_before - (len(left)/total * entropy(left) + len(right)/total * entropy(right))
        
        if gain > best_gain:
            best_gain   = gain
            best_thresh = thresh
    
    return best_thresh, best_gain

def discretize_by_entropy(examples, attributes):
    thresholds_dict = {}
    
    for attribute in attributes:
        # Encontra o melhor ponto de SPLIT para este atributo específico
        best_thresh, gain = find_best_split(examples, attribute)
        
        if best_thresh is None:
            # Fallback caso não consiga fazer split 
            best_thresh = float(examples[0][attribute])
            
        thresholds_dict[attribute] = [best_thresh]
        
        
        for example in examples:
            v = float(example[attribute])
            if v <= best_thresh:
                example[attribute] = f"<= {best_thresh:.2f}"
            else:
                example[attribute] = f"> {best_thresh:.2f}"
                
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



attributes = ["sepallength", "sepalwidth", "petallength", "petalwidth"]

# ── Versão 1: Discretização por intervalos iguais ───────────────────────────────
print("\n=== Discretização por Intervalos Iguais ===")
examples1 = []
with open("iris.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        examples1.append({"sepallength": row["sepallength"], "sepalwidth": row["sepalwidth"],
                          "petallength": row["petallength"], "petalwidth": row["petalwidth"],
                          "label": row["class"]})
examples1, _ = discretize(examples1, attributes, n_bins=3)
random.seed(42)
random.shuffle(examples1)
split = int(len(examples1) * 0.8)
train1, test1 = examples1[:split], examples1[split:]
tree1 = ID3Node(max_depth=5)
tree1.build_tree(train1, attributes, depth=0)
correct1 = sum(1 for ex in test1 if tree1.predict(ex) == ex["label"])
print(f"Treino: {len(train1)} | Teste: {len(test1)}")
print(f"Accuracy: {correct1/len(test1)*100:.2f}%")
tree1.print_tree()
tree1.plot_tree("decision_tree_intervals.png")

# ── Versão 2: Discretização por entropia ────────────────────────────────────────
print("\n=== Discretização por Entropia ===")
examples2 = []
with open("iris.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        examples2.append({"sepallength": row["sepallength"], "sepalwidth": row["sepalwidth"],
                          "petallength": row["petallength"], "petalwidth": row["petalwidth"],
                          "label": row["class"]})
examples2, _ = discretize_by_entropy(examples2, attributes)
random.seed(42)
random.shuffle(examples2)
split = int(len(examples2) * 0.8)
train2, test2 = examples2[:split], examples2[split:]
tree2 = ID3Node(max_depth=5)
tree2.build_tree(train2, attributes, depth=0)
correct2 = sum(1 for ex in test2 if tree2.predict(ex) == ex["label"])
print(f"Treino: {len(train2)} | Teste: {len(test2)}")
print(f"Accuracy: {correct2/len(test2)*100:.2f}%")
tree2.print_tree()
tree2.plot_tree("decision_tree_entropy.png")
