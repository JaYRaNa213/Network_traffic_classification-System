from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import mutual_info_score
import numpy as np
from sklearn.utils.validation import check_X_y, check_array
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder

class HybridDecisionTree:
    def __init__(self, max_depth=None, min_samples_split=2, random_state=None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.random_state = random_state
        self.tree = None  # Placeholder for tree structure
        self.feature_importances_ = None

    def _calculate_split_score(self, X, y, feature_index):
        """Custom splitting criterion: Mutual information + Gini impurity."""
        mutual_info = mutual_info_score(y, X[:, feature_index])
        gini_impurity = 1.0 - sum((np.bincount(y) / len(y)) ** 2)
        return mutual_info - 0.1 * gini_impurity  # Weighted combination

    def fit(self, X, y):
        X, y = check_X_y(X, y)  # Input validation
        self.tree = DecisionTreeClassifier(
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            random_state=self.random_state
        )
        self.tree.fit(X, y)
        self.feature_importances_ = self.tree.feature_importances_

    def predict(self, X):
        X = check_array(X)  # Input validation
        return self.tree.predict(X)


class AdaptiveDecisionTreeForest(BaseEstimator, ClassifierMixin):
    def __init__(self, n_estimators=10, max_depth=None, tree_dropout=0.2, 
                 max_features='sqrt', bootstrap=True, random_state=None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.tree_dropout = tree_dropout
        self.max_features = max_features  # New parameter for max_features
        self.bootstrap = bootstrap  # New parameter for bootstrapping
        self.random_state = random_state
        self.trees = []
        self.feature_weights = None

    def _calculate_feature_weights(self, X, y):
        from sklearn.feature_selection import mutual_info_classif
        return mutual_info_classif(X, y, random_state=self.random_state)

    def fit(self, X, y):
        X, y = check_X_y(X, y)
        self.feature_weights = self._calculate_feature_weights(X, y)
        self.feature_weights /= self.feature_weights.sum()

        rng = np.random.default_rng(self.random_state)

        # Determine max_features value
        if self.max_features == 'sqrt':
            max_features = int(np.sqrt(X.shape[1]))  # Default 'sqrt' behavior
        elif self.max_features == 'log2':
            max_features = int(np.log2(X.shape[1]))  # Log2 behavior
        else:
            max_features = self.max_features  # If it's an integer, use as-is

        for _ in range(self.n_estimators):
            tree = HybridDecisionTree(
                max_depth=self.max_depth,
                random_state=rng.integers(0, 1000)
            )

            # Use bootstrap sampling if required
            if self.bootstrap:
                # Sample with replacement for bootstrapping
                sample_indices = rng.choice(X.shape[0], size=X.shape[0], replace=True)
                X_bootstrap = X[sample_indices]
                y_bootstrap = y[sample_indices]
            else:
                X_bootstrap = X
                y_bootstrap = y

            feature_subset = rng.choice(
                X.shape[1],
                size=max_features,  # Use max_features to limit feature subset size
                replace=False,
                p=self.feature_weights
            )
            tree.fit(X_bootstrap[:, feature_subset], y_bootstrap)
            self.trees.append((tree, feature_subset))

    def predict(self, X):
        X = check_array(X)
        predictions = np.zeros((X.shape[0], len(np.unique(self.feature_weights))))
        n_active_trees = int((1 - self.tree_dropout) * len(self.trees))
        rng = np.random.default_rng(self.random_state)
        active_trees = rng.choice(len(self.trees), size=n_active_trees, replace=False)

        for i in active_trees:
            tree, features = self.trees[i]
            preds = tree.predict(X[:, features])
            predictions += np.eye(len(predictions[0]))[preds]

        return np.argmax(predictions, axis=1)

    def score(self, X, y):
        return accuracy_score(y, self.predict(X))


if __name__ == "__main__":
    # Load dataset (replace with actual dataset)
    data = pd.read_csv('log2.csv')

    X = data.drop(columns=data.columns[4]).values
    y = data.iloc[:, 4].values


    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
#-----------------------Training and spliting----------------------------------------------------------------
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.3, random_state=42)

    # Initialize and train the model with max_features and bootstrapping
    hybrid_model = AdaptiveDecisionTreeForest(
        n_estimators=300,   # Increased number of trees for stability
        max_depth=10,       # Slightly deeper trees for capturing more complexity
        tree_dropout=0.2,   # Low dropout for ensemble contributions
        max_features='sqrt',  # Choose sqrt of the number of features
        bootstrap=True,  # Enable bootstrapping
        random_state=42
    )
    hybrid_model.fit(X_train, y_train)   
    # # Evaluate the model
    print("Train Accuracy:", hybrid_model.score(X_train, y_train))
    print("Test Accuracy:", hybrid_model.score(X_test, y_test))
    cm = confusion_matrix(y_test, hybrid_model.predict(X_test))
    print(classification_report(y_test,hybrid_model.predict(X_test)))
    print(hybrid_model.predict([[50049,443,21285,443,7912,3269,4643,23,96,12,11]]))


    #-----------Export the model-------------------------------------------------------------
    import dill

    # Save the model
    with open('hybrid_model.pkl', 'wb') as file:
        dill.dump(hybrid_model, file)
