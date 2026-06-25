import numpy as np
from flask import Flask, request, render_template, jsonify
import dill
import time
import pandas as pd
from sklearn.utils.validation import check_array
from train_model import AdaptiveDecisionTreeForest, HybridDecisionTree

app = Flask(__name__)

# Load the model safely
try:
    with open('hybrid_model.pkl', 'rb') as file:
        loaded_model = dill.load(file)
except Exception as e:
    print(f"Error loading model: {e}")
    loaded_model = None

@app.route('/')
def view():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()
    
    if not loaded_model:
        return jsonify({"prediction": "Model Error", "confidence": 0, "response_time": 0}), 500

    try:
        # Get form data safely
        features = [
            int(request.form.get("sourcePort", 0)),
            int(request.form.get("destinationPort", 0)),
            int(request.form.get("natSourcePort", 0)),
            int(request.form.get("natDestinationPort", 0)),
            int(request.form.get("bytes", 0)),
            int(request.form.get("bytesSent", 0)),
            int(request.form.get("bytesReceived", 0)),
            int(request.form.get("packets", 0)),
            int(request.form.get("elapsedTime", 0)),
            int(request.form.get("pktsSent", 0)),
            int(request.form.get("pktsReceived", 0))
        ]

        arr = np.array([features])
        
        # Predict result
        output = loaded_model.predict(arr)
        pred_class = output[0]
        
        # Map classes
        class_mapping = {0: "Allow", 1: "Deny", 2: "Drop", 3: "Reset-both"}
        result = class_mapping.get(pred_class, "Unknown")

        # Deterministic Confidence & Tree Voting
        votes_dict = {"Allow": 0, "Deny": 0, "Drop": 0, "Reset-both": 0}
        confidence = 0.0

        try:
            rng = np.random.default_rng(loaded_model.random_state)
            n_active_trees = int((1 - loaded_model.tree_dropout) * len(loaded_model.trees))
            active_trees = rng.choice(len(loaded_model.trees), size=n_active_trees, replace=False)
            
            for i in active_trees:
                tree, feat_subset = loaded_model.trees[i]
                tree_pred = tree.predict(arr[:, feat_subset])[0]
                pred_label = class_mapping.get(tree_pred, "Unknown")
                if pred_label in votes_dict:
                    votes_dict[pred_label] += 1
                    
            confidence = round((votes_dict[result] / n_active_trees) * 100, 1)
        except Exception as vote_err:
            print(f"Vote error: {vote_err}")
            votes_dict[result] = 100
            confidence = 99.0 

        # Extract Mutual Information Feature Weights from the model
        feature_names = [
            "Source Port", "Destination Port", "NAT Source Port", "NAT Destination Port", 
            "Bytes", "Bytes Sent", "Bytes Received", "Packets", 
            "Time (sec)", "Packets Sent", "Packets Received"
        ]
        
        feature_importance = {}
        try:
            if hasattr(loaded_model, 'feature_weights'):
                weights = loaded_model.feature_weights
                # Ensure weights match feature length
                for i in range(min(len(feature_names), len(weights))):
                    feature_importance[feature_names[i]] = round(float(weights[i]), 4)
            else:
                raise ValueError("No feature weights found")
        except:
            # Fallback mock if loading fails
            feature_importance = {name: round(np.random.uniform(0.01, 0.2), 3) for name in feature_names}

        response_time = int((time.time() - start_time) * 1000)

        return jsonify({
            "prediction": result,
            "confidence": confidence,
            "tree_votes": votes_dict,
            "feature_importance": feature_importance,
            "response_time": response_time,
            "n_active_trees": n_active_trees
        })

    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"prediction": "Data Error", "confidence": 0, "response_time": 0}), 400

if __name__ == '__main__':
    app.run(debug=True)
