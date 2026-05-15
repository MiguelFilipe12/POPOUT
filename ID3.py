import math
import matplotlib
matplotlib.use('Agg')  # Força o Matplotlib a não abrir janelas nem interagir com o ecrã
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network  # Necessário para a versão interativa

class Node:
    def __init__(self, max_depth=None):
        self.attribute = None
        self.max_depth = max_depth
        self.children = {}
        self.is_leaf = False
        self.label = None

    def entropy(self, examples):
        total = len(examples)
        if total == 0:
            return 0 
        count = {}
        for example in examples:
            label = example["label"]
            if label not in count:
                count[label] = 0
            count[label] += 1
 
        ent = 0                     
        for label in count:
            p = count[label] / total
            if p == 0:
                continue
            ent -= p * math.log2(p)
        return ent
    
    def information_gain(self, examples, attribute):
        entropy_before = self.entropy(examples)
        subsets = {}
        entropy_after = 0 
        for example in examples:
            value = example[attribute]
            if value not in subsets:
                subsets[value] = []
            subsets[value].append(example)

        for value in subsets:
            p = len(subsets[value]) / len(examples)
            entropy_after += p * self.entropy(subsets[value])
        return entropy_before - entropy_after           
    
    def best_attribute(self, examples, atributes):
        best_atribute = None
        best_gain = -1
        for attribute in atributes:
            gain = self.information_gain(examples, attribute)
            if gain > best_gain:
                best_gain = gain
                best_atribute = attribute
        return best_atribute
    
    def majority_label(self, examples):
        count = {}
        for example in examples:
            label = example["label"]
            if label not in count:
                count[label] = 0
            count[label] += 1
        majority_label = None
        majority_count = -1
        for label, c in count.items():
            if c > majority_count:
                majority_count = c
                majority_label = label
        return majority_label

    def build_tree(self, examples, atributes, depth):
        labels = set(example["label"] for example in examples)

        if len(labels) == 1:
            self.is_leaf = True
            self.label = labels.pop()
            return self
        
        if not atributes:
            self.is_leaf = True
            self.label = self.majority_label(examples)
            return self

        if self.max_depth is not None and depth >= self.max_depth:
            self.is_leaf = True
            self.label = self.majority_label(examples)
            return self
        
        best_atribute = self.best_attribute(examples, atributes)
        self.attribute = best_atribute
        subsets = {}
        for example in examples:
            value = example[best_atribute]
            if value not in subsets:
                subsets[value] = []
            subsets[value].append(example)
            
        self.label = self.majority_label(examples)
        for value, subset in subsets.items():
            child = Node(self.max_depth)
            child.build_tree(subset, [a for a in atributes if a != best_atribute], depth + 1)
            self.children[value] = child    

    def predict(self, example):
        if self.is_leaf:
            return self.label
        value = example[self.attribute]
        if value in self.children:
            return self.children[value].predict(example)
        else:
            return self.label
        
    def print_tree(self, depth=0):
        indent = "  " * depth
        if self.is_leaf:
            print(f"{indent}Leaf: {self.label}")
        else:
            print(f"{indent}Node: {self.attribute}")
            for value, child in self.children.items():
                print(f"{indent}  Value: {value}")
                child.print_tree(depth + 1)

    # --- Lógica de Grafo (Partilhada entre estático e interativo) ---

    def _add_nodes(self, G, labels, edge_labels, parent_id, edge_label, counter):
        node_id = counter[0]
        counter[0] += 1
        
        if self.is_leaf:
            labels[node_id] = f"FOLHA\n{self.label}"
        else:
            labels[node_id] = f"[{self.attribute}]"
        
        G.add_node(node_id)
        
        if parent_id is not None:
            G.add_edge(parent_id, node_id)
            edge_labels[(parent_id, node_id)] = edge_label
        
        for value, child in self.children.items():
            child._add_nodes(G, labels, edge_labels, node_id, str(value), counter)    

    # --- Visualização Estática (PNG) ---

    def plot_tree(self, save_path="decision_tree.png"):
        G = nx.DiGraph()
        labels = {}
        edge_labels = {}
        counter = [0]
        self._add_nodes(G, labels, edge_labels, None, None, counter)
        
        pos = self._hierarchy_pos(G, 0)
        
        plt.figure(figsize=(14, 8))
        nx.draw(G, pos, labels=labels, with_labels=True,
                node_color="lightblue", node_size=2000,
                font_size=8, arrows=True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        plt.title("Decision Tree (ID3)")
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            print(f"Árvore estática guardada em: {save_path}")
        plt.close()

    def _hierarchy_pos(self, G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5):
        pos = {root: (xcenter, vert_loc)}
        children = list(G.successors(root))
        if children:
            dx = width / len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos.update(self._hierarchy_pos(G, child, width=dx,
                            vert_gap=vert_gap, vert_loc=vert_loc-vert_gap,
                            xcenter=nextx))
        return pos

    # --- NOVO: Visualização Interativa (HTML) ---

    def plot_interactive(self, filename="tree_interativa.html"):
        """Gera um ficheiro HTML onde podes fazer zoom e mover os nós."""
        G = nx.DiGraph()
        labels = {}
        edge_labels = {}
        counter = [0]
        self._add_nodes(G, labels, edge_labels, None, None, counter)
        
        net = Network(height="750px", width="100%", notebook=False, directed=True)
        
        for node_id in G.nodes():
            label = labels[node_id]
            # Folhas ficam a vermelho claro, nós a azul
            color = "#ffcccb" if "FOLHA" in label else "#97c2fc"
            net.add_node(node_id, label=label, color=color, shape="box")
            
        for source, target in G.edges():
            edge_label = edge_labels.get((source, target), "")
            net.add_edge(source, target, label=edge_label)

        # Configuração para layout de árvore automática
        net.set_options("""
        {
          "layout": {
            "hierarchical": {
              "enabled": true,
              "levelSeparation": 150,
              "nodeSpacing": 200,
              "treeSpacing": 200,
              "direction": "UD",
              "sortMethod": "directed"
            }
          },
          "physics": {
            "enabled": false
          }
        }
        """)
        
        net.save_graph(filename)
        print(f"Árvore interativa guardada em: {filename}")