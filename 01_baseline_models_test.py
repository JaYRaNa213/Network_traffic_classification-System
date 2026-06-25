import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
data=pd.read_csv("log2.csv")
# print(data.describe())
X=data.drop('Action',axis=1)
Y=data['Action']
# print(data.describe())
from sklearn.model_selection import train_test_split
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.4,shuffle=False,random_state=0)

#-----------------------------------------Model apply ---------------------------
#-------------Random forest-------------
# from sklearn.ensemble import RandomForestClassifier
# classifier=RandomForestClassifier(n_estimators=5,criterion="gini")
# model=classifier.fit(X_train,Y_train)
#-----------------------------------------------------------------------------dicion tree----------
from sklearn.tree import DecisionTreeClassifier
dt=DecisionTreeClassifier(criterion='log_loss', min_samples_split= 2, splitter= 'best')
dt.fit(X_train,Y_train)
Y_pridict=dt.predict(X_test)
# print(Y_test)
# print(Y_pridict)
from sklearn.metrics import accuracy_score ,confusion_matrix,classification_report
print( "accuray of test model",accuracy_score(Y_test,Y_pridict)*100)
print( "accuray of train model",accuracy_score(Y_train,dt.predict(X_train))*100)

