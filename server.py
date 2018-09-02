"""Filename: server.py
"""

import os 
import json
import pandas as pd
from sklearn.externals import joblib
from flask import Flask, jsonify, request
from utils import PreProcessing
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestClassifier

from sklearn.pipeline import make_pipeline

import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def apicall():
    #API Call: Pandas df (sent as a payload) from API Call
    try:
        test_json = request.get_json()
        test = pd.read_json(test_json, orient='records')

        #To resolve the issue of TypeError: Cannot compare types 'ndarray(dtype=int64)' and 'str'
        test['Dependents'] = [str(x) for x in list(test['Dependents'])]

        #Getting the Loan_IDs separated out
        loan_ids = test['Loan_ID']

    except Exception as e:
        raise e

    clf = 'model_v1.pk'

    if test.empty:
        return(bad_request())
    else:
        #Load the saved model
        print("Loading the model...")
        loaded_model = joblib.load("C:/Users/datta/Desktop/flask_api/notebooks/finalized_model.pkl")

        print("The model has been loaded...doing predictions now...")
        predictions = loaded_model.predict(test)

        prediction_series = list(pd.Series(predictions))

        final_predictions = pd.DataFrame(list(zip(loan_ids, prediction_series)))

        responses = jsonify(predictions=final_predictions.to_json(orient="records"))
        responses.status_code = 200

        return (responses)

@app.route("/retrain", methods=['POST'])
def retrain():
    if request.method == 'POST':
        data = request.get_json()

        try:
            training_set = joblib.load("C:/Users/datta/Desktop/flask_api/notebooks/training_data.pkl")
            training_labels = joblib.load("C:/Users/datta/Desktop/flask_api/notebooks/training_labels.pkl")

            df = pd.read_json(data)

            df_training_set = df.drop(["Loan_Status"], axis=1)
            df_training_labels = df["Loan_Status"]

            df_training_set = pd.concat([training_set, df_training_set])
            df_training_labels = pd.concat([training_labels, df_training_labels])


            pipe = make_pipeline(PreProcessing(),RandomForestClassifier())

            new_param_grid = {"randomforestclassifier__n_estimators" : [10, 20, 30],\
                 "randomforestclassifier__max_depth" : [None, 6, 8, 10],\
                 "randomforestclassifier__max_leaf_nodes": [None, 5, 10, 20], \
                 "randomforestclassifier__min_impurity_split": [0.1, 0.2, 0.3]}

            new_grid = GridSearchCV(pipe, param_grid=new_param_grid, cv=3)

            new_grid.fit(df_training_set, df_training_labels)

            os.remove("C:/Users/datta/Desktop/flask_api/notebooks/finalized_model.pkl")
            os.remove("C:/Users/datta/Desktop/flask_api/notebooks/training_data.pkl")
            os.remove("C:/Users/datta/Desktop/flask_api/notebooks/training_labels.pkl")

            joblib.dump(new_grid, "C:/Users/datta/Desktop/flask_api/notebooks/finalized_model.pkl")
            joblib.dump(df_training_set, "C:/Users/datta/Desktop/flask_api/notebooks/training_data.pkl")
            joblib.dump(df_training_labels, "C:/Users/datta/Desktop/flask_api/notebooks/training_labels.pkl")

            rf_model = joblib.load("C:/Users/datta/Desktop/flask_api/notebooks/finalized_model.pkl")
        except ValueError as e:
            return jsonify("Error when retraining - {}".format(e))

        return jsonify("Retrained model successfully.")


@app.route("/currentDetails", methods=['GET'])
def current_details():
    if request.method == 'GET':
        try:
            rf_model = joblib.load("C:/Users/datta/Desktop/flask_api/notebooks/finalized_model.pkl")
            training_set = joblib.load("C:/Users/datta/Desktop/flask_api/notebooks/training_data.pkl")
            labels = joblib.load("C:/Users/datta/Desktop/flask_api/notebooks/training_labels.pkl")

            return jsonify({"score": rf_model.score(training_set, labels)})
        except (ValueError, TypeError) as e:
            return jsonify("Error when getting details - {}".format(e))

@app.errorhandler(400)
def bad_request(error=None):
	message = {
			'status': 400,
			'message': 'Bad Request: ' + request.url + '--> Please check your data payload...',
	}
	resp = jsonify(message)
	resp.status_code = 400

	return resp

if(__name__=='__main__'):
    app.run(host='0.0.0.0', port=5001, debug=True)