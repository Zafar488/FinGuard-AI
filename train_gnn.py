import os
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
import pandas as pd
import numpy as np
import random

print("🕸️ Starting GNN Fraud Ring Detection Training...")

# 1. Define the Graph Neural Network (GCN)
class FraudGNN(torch.nn.Module):
    def __init__(self, num_features):
        super(FraudGNN, self).__init__()
        # Two Graph Convolutional Layers
        self.conv1 = GCNConv(num_features, 16)
        self.conv2 = GCNConv(16, 2) # Output: 2 classes (Safe vs Fraud)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        
        # Message Passing Layer 1
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.5, training=self.training)
        
        # Message Passing Layer 2
        x = self.conv2(x, edge_index)
        
        return F.log_softmax(x, dim=1)

# 2. Simulate the Fraud Graph Network
def create_synthetic_graph(num_nodes=1000, fraud_ratio=0.1):
    print(f"🔗 Simulating Financial Network Graph with {num_nodes} transactions...")
    
    # Simulate features (V1 to V28 + Amount + Time = 30 features)
    num_features = 30
    x = torch.randn((num_nodes, num_features), dtype=torch.float)
    
    # Create Labels (0 = Safe, 1 = Fraud)
    y = torch.zeros(num_nodes, dtype=torch.long)
    num_fraud = int(num_nodes * fraud_ratio)
    fraud_indices = random.sample(range(num_nodes), num_fraud)
    y[fraud_indices] = 1
    
    # Create Edges (Simulating Transactions sharing the same IP / Device)
    edge_sources = []
    edge_targets = []
    
    # 1. Connect Safe Nodes randomly (Normal behavior)
    for i in range(num_nodes):
        if y[i] == 0:
            targets = random.sample(range(num_nodes), k=random.randint(1, 3))
            for t in targets:
                edge_sources.append(i)
                edge_targets.append(t)
                
    # 2. FRAUD RING SYNTHESIS: Connect Fraud nodes heavily to each other
    # Simulates a coordinated botnet or money laundering ring
    for i in fraud_indices:
        # Fraudsters share devices with other fraudsters
        targets = random.sample(fraud_indices, k=random.randint(5, 10))
        for t in targets:
            edge_sources.append(i)
            edge_targets.append(t)
            # Add reverse edge to make it undirected
            edge_sources.append(t)
            edge_targets.append(i)

    edge_index = torch.tensor([edge_sources, edge_targets], dtype=torch.long)
    
    return Data(x=x, edge_index=edge_index, y=y)

# 3. Train the Model
def train_gnn():
    # Generate Graph
    data = create_synthetic_graph(num_nodes=2000, fraud_ratio=0.05)
    
    # Initialize Model & Optimizer
    model = FraudGNN(num_features=data.num_node_features)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
    
    # Create masks for training and testing
    indices = torch.randperm(data.num_nodes)
    train_mask = torch.zeros(data.num_nodes, dtype=torch.bool)
    test_mask = torch.zeros(data.num_nodes, dtype=torch.bool)
    train_mask[indices[:1600]] = True
    test_mask[indices[1600:]] = True

    print("🚀 Training Graph Convolutional Network (GCN)...")
    model.train()
    for epoch in range(1, 201):
        optimizer.zero_grad()
        out = model(data)
        # Loss calculated only on training nodes
        loss = F.nll_loss(out[train_mask], data.y[train_mask])
        loss.backward()
        optimizer.step()
        
        if epoch % 20 == 0:
            print(f'Epoch: {epoch:03d}, Loss: {loss:.4f}')

    # 4. Evaluate
    model.eval()
    pred = model(data).argmax(dim=1)
    correct = (pred[test_mask] == data.y[test_mask]).sum()
    acc = int(correct) / int(test_mask.sum())
    print(f'✅ GNN Test Accuracy: {acc:.4f}')

    # 5. Save the Model
    models_dir = os.path.join(os.path.dirname(__file__), 'Models')
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, 'gnn_fraud_model.pth')
    torch.save(model.state_dict(), model_path)
    print(f"💾 GNN Model saved to: {model_path}")

if __name__ == "__main__":
    train_gnn()