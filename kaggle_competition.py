# -*- coding: utf-8 -*-
"""Kaggle Competition

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ZX4em9vdhqkpOn5_JCz93LVaFa3p79o9
"""

#Phase 1, baseline logistic regression test to get a jumping off point
#Began by viewing the dataset to understand its structure, identify missing values, and prepare the data for modeling.
#Several columns contained missing values so categorical columns were filled using the mode, while numerical columns were filled with the median.
#Categorical variables were then encoded using Label Encoding, allowing them to be compatible with the machine learning models.
#To establish a baseline, I started with a simple Logistic Regression model.
#This initial model provided us with a log loss score of 0.46, serving as the starting point and orioviding context for further improvement.

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.preprocessing import LabelEncoder, StandardScaler

#Load data
train_df = pd.read_csv('/content/train.csv')
test_df = pd.read_csv('/content/test.csv')

#Fill missing values
categorical_cols = ['Drug', 'Ascites', 'Hepatomegaly', 'Spiders', 'Edema', 'Sex']
numerical_cols = ['Cholesterol', 'Copper', 'Alk_Phos', 'SGOT', 'Tryglicerides', 'Platelets', 'Prothrombin']

for col in categorical_cols:
    train_df[col] = train_df[col].fillna(train_df[col].mode()[0])
    test_df[col] = test_df[col].fillna(test_df[col].mode()[0])

for col in numerical_cols:
    train_df[col] = train_df[col].fillna(train_df[col].median())
    test_df[col] = test_df[col].fillna(test_df[col].median())

#set numerical values for categorical columns
label_encoder = LabelEncoder()
for col in categorical_cols:
    train_df[col] = label_encoder.fit_transform(train_df[col])
    test_df[col] = label_encoder.transform(test_df[col])

X_train = train_df.drop(['id', 'Status'], axis=1)
y_train = train_df['Status']
X_test = test_df.drop(['id'], axis=1)

#Logistic Regression model
model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=200)
model.fit(X_train, y_train)

y_pred = model.predict_proba(X_test)

#Log loss
val_log_loss = log_loss(y_test, y_pred)
print(f"Baseline Log Loss with Logistic Regression: {val_log_loss}")

#Phase 2, XGBoost, Final Submission Code
#After the logistic regression test, I ran basic tests with other methods such as Random Forests, SVM, and XGBoost
#These inital tests yielded XGBoost having the best score and this became the base model I continued to improve upon.
#After initially setting the parameters to learning_rate=0.1, max_depth=3, and n_estimators=300. This model yielded an improved log loss score of 0.375,
#This was a vast improvement showing that XGBoost was indeed effective for this dataset.

#Phase 3, hyperparameter tuning and Cross Validation
#Building on these initial results, I conducted hyperparameter tuning, experimenting with parameters such as reg_lambda, reg_alpha, max_depth, and learning_rate to better the model’s performance.
#I initially ran a seperate block of code utilizing Grid search in order to determine the best hyperparameters, but after an hour I realized I needed to reduce the run time and settled for a random search method
#The random search method is shown in the block of code below and was tweaked with different variations a few times before finally determining the best hyperparameters.
#Hyperparamter tuning brought my score down to about .369 which I was happy but not satisfied with.
#The next improvement I made was implementing K-Fold Cross validation in order to try and reduce my score but also prevent overfitting agaisnt the hidden 80% of test data
#Implementation of Cross-Validation whcih can be seen below brought my score down to 0.3633, which became my best score.

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import log_loss

train_df = pd.read_csv('/content/train.csv')
test_df = pd.read_csv('/content/test.csv')

categorical_cols = ['Drug', 'Ascites', 'Hepatomegaly', 'Spiders', 'Edema', 'Sex']
numerical_cols = ['Cholesterol', 'Copper', 'Alk_Phos', 'SGOT', 'Tryglicerides', 'Platelets', 'Prothrombin']

for col in categorical_cols:
    train_df[col] = train_df[col].fillna(train_df[col].mode()[0])
    test_df[col] = test_df[col].fillna(test_df[col].mode()[0])

for col in numerical_cols:
    train_df[col] = train_df[col].fillna(train_df[col].median())
    test_df[col] = test_df[col].fillna(test_df[col].median())

label_encoder = LabelEncoder()
for col in categorical_cols:
    train_df[col] = label_encoder.fit_transform(train_df[col])
    test_df[col] = label_encoder.transform(test_df[col])

train_df['Status'] = label_encoder.fit_transform(train_df['Status'])

X = train_df.drop(['id', 'Status'], axis=1)
y = train_df['Status']

#Parameters for initial XGBoost model
params = {
    'objective': 'multi:softprob',
    'eval_metric': 'mlogloss',
    'num_class': 3,
    'learning_rate': 0.1,
    'max_depth': 3,
    'n_estimators': 300,
    'reg_lambda': 2,
    'reg_alpha': 0.1
}

xgb_model = xgb.XGBClassifier(**params)
xgb_model.fit(X, y)

#K-Fold Cross-Validation to get the average log loss
skf = StratifiedKFold(n_splits=5)
fold_log_losses = []

for train_index, val_index in skf.split(X, y):
    X_train_fold, X_val_fold = X.iloc[train_index], X.iloc[val_index]
    y_train_fold, y_val_fold = y.iloc[train_index], y.iloc[val_index]

    xgb_model.fit(X_train_fold, y_train_fold)

    y_pred = xgb_model.predict_proba(X_val_fold)

    fold_log_loss = log_loss(y_val_fold, y_pred)
    fold_log_losses.append(fold_log_loss)
    print(f"Fold Log Loss: {fold_log_loss}")

#average log loss
avg_log_loss = np.mean(fold_log_losses)
print(f"Average Log Loss: {avg_log_loss}")

y_test_pred = xgb_model.predict_proba(test_df.drop(['id'], axis=1))

submission = pd.DataFrame(y_test_pred, columns=['Status_C', 'Status_CL', 'Status_D'])
submission['id'] = test_df['id']
submission = submission[['id', 'Status_C', 'Status_CL', 'Status_D']]

submission.to_csv('submission.csv', index=False)
print("Submission file created!")

#Random Search to find the best parameters for our hyperparameter tuning
param_distributions = {
    'learning_rate': [0.01, 0.05, 0.1, 0.15],
    'max_depth': [3, 4, 5, 6],
    'n_estimators': [100, 200, 300, 400],
    'reg_lambda': [1, 2, 3, 4],
    'reg_alpha': [0, 0.1, 0.2, 0.3],
    'min_child_weight': [1, 3, 5],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.6, 0.8, 1.0]
}

random_search = RandomizedSearchCV(
    estimator=xgb_model,
    param_distributions=param_distributions,
    n_iter=50,
    scoring='neg_log_loss',
    cv=StratifiedKFold(n_splits=5),
    verbose=1,
    random_state=42,
    n_jobs=-1
)

random_search.fit(X, y)

best_params = random_search.best_params_
best_score = -random_search.best_score_
print(f"Best parameters: {best_params}")
print(f"Best Cross-Validation Log Loss: {best_score}")

#Phase 4, evaluation of other methods
#After tuning XGBoost to get its best possible score, I decided to try and combine different methods
#I Attempted to implement Gradient Boosting and ensemble methods to combine the XGBoost with methods like R.F.s and Logistic Regression
#Below is just one example of an ensemble method I ran to try and boost our model even further, yielding log loss of 3.8
#It became aparrent that every ciombination of models I tried yielded a lower score than my XGBoost alone
#After tuning different ensemble combinations and adding cross validation and gradient boosting, I was able to get the score down to 3.71
#While this was an improvement, it seemed that using just XGBoost was the best method for this case.
import pandas as pd
import numpy as np
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

train_df = pd.read_csv('/content/train.csv')
test_df = pd.read_csv('/content/test.csv')

categorical_cols = ['Drug', 'Ascites', 'Hepatomegaly', 'Spiders', 'Edema', 'Sex']
numerical_cols = ['Cholesterol', 'Copper', 'Alk_Phos', 'SGOT', 'Tryglicerides', 'Platelets', 'Prothrombin']

for col in categorical_cols:
    train_df[col] = train_df[col].fillna(train_df[col].mode()[0])
    test_df[col] = test_df[col].fillna(test_df[col].mode()[0])

for col in numerical_cols:
    train_df[col] = train_df[col].fillna(train_df[col].median())
    test_df[col] = test_df[col].fillna(test_df[col].median())

label_encoder = LabelEncoder()
for col in categorical_cols:
    train_df[col] = label_encoder.fit_transform(train_df[col])
    test_df[col] = label_encoder.transform(test_df[col])

train_df['Status'] = label_encoder.fit_transform(train_df['Status'])

X = train_df.drop(['id', 'Status'], axis=1)
y = train_df['Status']

#individual models
xgb_model = xgb.XGBClassifier(objective='multi:softprob', eval_metric='mlogloss', n_estimators=300, learning_rate=0.1, max_depth=3)
rf_model = RandomForestClassifier(n_estimators=300, random_state=42)
lr_model = LogisticRegression(max_iter=500, multi_class='multinomial', solver='lbfgs')

#ensemble model
ensemble_model = VotingClassifier(
    estimators=[('xgb', xgb_model), ('rf', rf_model), ('lr', lr_model)],
    voting='soft'
)

#K-Fold Cross-Validation
skf = StratifiedKFold(n_splits=5)
fold_log_losses = []

for train_index, val_index in skf.split(X, y):
    X_train_fold, X_val_fold = X.iloc[train_index], X.iloc[val_index]
    y_train_fold, y_val_fold = y.iloc[train_index], y.iloc[val_index]

    #Train the ensemble model
    ensemble_model.fit(X_train_fold, y_train_fold)

    y_pred = ensemble_model.predict_proba(X_val_fold)

    fold_log_loss = log_loss(y_val_fold, y_pred)
    fold_log_losses.append(fold_log_loss)
    print(f"Fold Log Loss: {fold_log_loss}")

#average log loss across all folds
avg_log_loss = np.mean(fold_log_losses)
print(f"Average Log Loss across all folds: {avg_log_loss}")

y_test_pred = ensemble_model.predict_proba(test_df.drop(['id'], axis=1))

submission = pd.DataFrame(y_test_pred, columns=['Status_C', 'Status_CL', 'Status_D'])
submission['id'] = test_df['id']
submission = submission[['id', 'Status_C', 'Status_CL', 'Status_D']]

submission.to_csv('submission.csv', index=False)
print("Submission file created!")

#Conclusion
# Throughout this project, I took an iterative approach to build and refine an optimal model for predicting the multi-class outcomes
# Starting with  data analysis, I handled missing values, encoded categorical features, and tested several baseline models.
# The first model, a Logistic Regression, provided a baseline log loss of 0.46, which helped to gauge the complexity of the task and the data.
# As I progressed further, I explored a range of models and methods, including RandomForest, Gradient Boosting, and Support Vector Machines, but these either underperformed or required additional complexity without significant gains.
# Moving to XGBoost, I observed an immediate improvement, with an initial log loss around 0.375.
# With this improvement, I refined this model by applying hyperparameter tuning using RandomizedSearchCV.
# After many iterations, this tuning, combined with Stratified K-Fold Cross-Validation and basic feature engineering such as logarithmic transformations, helped us achieve our best log loss score of 0.3633.
# To further attemot to enhance performance, I attempted ensemble methods, combining XGBoost with RandomForest and Logistic Regression.
# Again with many iterations of different ensemble methods, our model yielded a log loss of 0.38, which did not surpass our best XGBoost score
#Ultimately, my process taught me the importance of structed model testing, parameter tuning, and feature engineering.
#Our final model, a fine tuned XGBoost classifier, yielded a log loss score of 0.3633, demonstrating that in my case, model tuning and validation were the most influential to optimizing predictive performance.

