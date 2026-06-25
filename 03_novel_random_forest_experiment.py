import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
data=pd.read_csv("log2.csv")
X=data.drop('Action',axis=1)
Y=data['Action']
from sklearn.model_selection import train_test_split
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.2,shuffle=True,random_state=1)
# Import required libraries
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score, classification_report
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
# model 3 --------------------------------------------------------------

# Step 3: Define a custom Random Forest model class (novelty: feature weighting)
class NovelRandomForest(RandomForestClassifier):
    def __init__(self, feature_importance_weight=None, **kwargs):
        super().__init__(**kwargs)
        self.feature_importance_weight = feature_importance_weight

    def fit(self, X, y):
        # Apply feature importance weights if provided
        if self.feature_importance_weight is not None:
            X = X * self.feature_importance_weight
        super().fit(X, y)

# Step 4: Generate random feature weights for novelty
feature_importance_weight = np.random.uniform(0.8, 1.2, X.shape[1])

# Instantiate the custom Random Forest model
novel_rf_model = NovelRandomForest(
    n_estimators=300,
    max_depth=25,
    min_samples_split=2,
    min_samples_leaf=5,
    class_weight='balanced',
    feature_importance_weight=feature_importance_weight,
    random_state=42

)
novel_rf_model.fit(X_train, Y_train) 
y_pred = novel_rf_model.predict(X_test)


#3---------------------------------------------------------------------------------------
print("\nClassification Report (Voting):\n", classification_report(Y_test, y_pred))
print( "accuray of test model",accuracy_score(Y_test,y_pred)*100)
print( "accuray of train model",accuracy_score(Y_train,novel_rf_model.predict(X_train))*100)


