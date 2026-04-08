import json
import numpy as np
import joblib
from sqlalchemy.orm import Session
from models import Sequence
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def load_features(db: Session):
    sequences = db.query(Sequence).filter(Sequence.gc_content != None).all()
    gc_values = [seq.gc_content for seq in sequences]
    median_gc = sorted(gc_values)[len(gc_values) // 2]
    seq_list, labels_list = [], []
    for seq in sequences:
        seq_list.append(seq)
        labels_list.append("healthy" if seq.gc_content >= median_gc else "disease")
    return seq_list, labels_list

def build_feature_matrix(seq_list):
    vocab = set()
    for seq in seq_list:
        kmer_dict = json.loads(seq.kmer_json)
        for key in kmer_dict.keys():
            vocab.add(key)
    vocab = sorted(vocab)
    joblib.dump(vocab, "vocab.pkl")  
    
    rows = []
    for seq in seq_list:
        kmer_dict = json.loads(seq.kmer_json)
        kmer_row = [kmer_dict.get(kmer, 0) for kmer in vocab]
        row = [seq.gc_content, seq.seq_length] + kmer_row
        rows.append(row)
    
    return np.array(rows)

def train_sklearn_models(x,y):
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    rf_clf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_clf.fit(X_train, y_train)
    print("Logistic Regression:\n", classification_report(y_test, model.predict(X_test)))
    print("Random Forest:\n", classification_report(y_test, rf_clf.predict(X_test)))
    joblib.dump(model, 'logistic_regression.pkl')
    joblib.dump(rf_clf, 'random_forest.pkl')
    return (model, rf_clf)

class GenomicClassifier(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.relu = nn.ReLU()  # ADD THIS
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 2)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)
    
def train_pytorch_model(X, y, epochs=50):
    joblib.dump(X.shape[1], "pytorch_input_size.pkl")
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.LongTensor(y_encoded)

    X_train, X_test, y_train, y_test = train_test_split(
        X_tensor, y_tensor, test_size=0.2, random_state=42
    )

    model = GenomicClassifier(input_size=X.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")

    # Evaluate
    model.eval()
    with torch.no_grad():
        preds = model(X_test).argmax(dim=1).numpy()
    print("PyTorch NN:\n", classification_report(y_test.numpy(), preds))

    torch.save(model.state_dict(), "genomic_classifier.pt")
    joblib.dump(le, "pytorch_label_encoder.pkl")
    return model, le

def predict(features: dict):
    kmer_dict = json.loads(features["kmer_json"]) if isinstance(features["kmer_json"], str) else features["kmer_json"]
    
    vocab = joblib.load("vocab.pkl")
    kmer_row = [kmer_dict.get(k, 0) for k in vocab]
    row = np.array([[features["gc_content"], features["seq_length"]] + kmer_row])

    results = {}

    for name, fname in [("logistic_regression", "logistic_regression.pkl"),
                        ("random_forest", "random_forest.pkl")]:
        clf = joblib.load(fname)
        label = clf.predict(row)[0]
        confidence = clf.predict_proba(row).max()
        results[name] = {"label": label, "confidence": round(confidence, 4)}

    le = joblib.load("pytorch_label_encoder.pkl")
    input_size = joblib.load("pytorch_input_size.pkl")
    model = GenomicClassifier(input_size=input_size)
    model.load_state_dict(torch.load("genomic_classifier.pt"))
    model.eval()
    with torch.no_grad():
        tensor = torch.FloatTensor(row)
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)
        idx = probs.argmax(dim=1).item()
        label = le.inverse_transform([idx])[0]
        confidence = probs[0][idx].item()
    results["pytorch"] = {"label": label, "confidence": round(confidence, 4)}

    return results
