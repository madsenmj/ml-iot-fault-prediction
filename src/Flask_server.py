import numpy as np
import xgboost as xgb
from flask import Flask, abort, jsonify, request
import pandas as pd
import json

bst = xgb.Booster() #init model
bst.load_model("../0002.model") # load data

app = Flask(__name__)

@app.route('/api',methods=['POST'])
def make_predict():
    dataobject = request.get_json(force=True)
    #print(dataobject)
    predict_input = list(dataobject['data'].values())
    predict_request = np.array(predict_input[1:-1], dtype='f')
    if len(predict_request.shape) == 1:
        
        times = np.array(predict_input[0], dtype='f')
        inputdata=xgb.DMatrix(predict_request[np.newaxis,:],feature_names=bst.feature_names)
    else:
        times = np.array(predict_input[:,0], dtype='f')
        inputdata=xgb.DMatrix(predict_request,feature_names=bst.feature_names)

    preds = bst.predict(inputdata)
    #print(preds)
    output = preds[:,0].tolist()
    
    outputdf = pd.DataFrame({'Time':times,'Prediction':output}).to_json(orient='records')
    
    returnmsg = jsonify(deviceId = dataobject['deviceId'],
                        datetime = dataobject['datetime'],
                        protocol = dataobject['protocol'],
                        batchID = dataobject['data']['batchID'],
                        results=json.loads(outputdf))
    
    return returnmsg

@app.route("/")
def Flask_server():
    return "Python Flask POST endpoint."


# Running app from command line:

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, app)


