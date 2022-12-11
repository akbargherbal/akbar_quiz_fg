from flask import Flask, render_template, request, redirect, url_for, jsonify

import firebase_admin
from firebase_admin import credentials, firestore

import pandas as pd
import sys, os, random
from io import StringIO

#For Production Hosting
from whitenoise import WhiteNoise
from waitress import serve

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root="static/")

#Initialize Firebase
cred = credentials.Certificate('firebase-account.json')
firebase_app = firebase_admin.initialize_app(cred)
db = firestore.client()

#Reference to quizes collection
quizs_collection = db.collection(u'quizes')
#Reference to history document
history_document = db.collection(u'history').document(u'history')

#Quizes Data [title {min, max}] -> to get random quiz from chosen collection
quizz_data = {
    'AR_GENERAL_VOCABULARY_':{'min':1, 'max':100},
    'NOUN_QUIZ_':{'min':1, 'max':100},
    'VERB_QUIZ_':{'min':1, 'max':100}
}

#Just used one time to send files to the database
def setup_db(folder):
    dir = 'quiz_repo/%s' % folder
    files = [path for path in os.listdir(dir) if os.path.isfile(os.path.join(dir, path))]
    paths = [os.path.join(dir, path) for path in files if path.find('.csv') > 0]
    for i,path in enumerate(paths):
        file = open(path, 'r').read()
        data = {
            u'data': u'%s' % file
        }
        quizs_collection.document(u'%s' % files[i].replace('.csv', '')).set(data)

#Allow Cross_origin without extensions
@app.after_request
def after_request_func(response):
	origin = request.headers.get('Origin')
	if request.method == 'OPTIONS':
		response = make_response()
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
		response.headers.add('Access-Control-Allow-Origin', origin)
		response.headers.add('Access-Control-Allow-Methods',
                                'GET, POST, OPTIONS, PUT, PATCH, DELETE')
	else:
		response.headers.add('Access-Control-Allow-Origin', origin)
	return response

@app.route('/home')
@app.route('/')
def home():
    return render_template('index.html')

#POST -> Save History | GET -> Get History
@app.route('/history', methods=['POST', 'GET'])
def save_history():
    h = history_document.get()
    if request.method == 'GET':
        if h.exists:
            return jsonify(h.to_dict())
        else:
            return jsonify({})
    else:
        if h.exists:
            h = h.to_dict()
            for k in h.keys():
                h[k].insert(0, u'%s' % request.json[k])
        else:
            h = {
                u'score': [ u'%s' % request.json['score'] ],
                u'correct': [ u'%s' % request.json['correct'] ],
                u'wrong': [ u'%s' % request.json['wrong'] ]
            }
        history_document.set(h)
        return jsonify(h)

#Get random quiz from the database
@app.route('/quiz/<collection>', methods=['GET'])
def get_random_quiz(collection):
    if collection is None or not collection in quizz_data:
        return jsonify({})
    else:
        r = random.randint(quizz_data[collection]['min'], quizz_data[collection]['max'])
        doc = quizs_collection.document(f'{collection}{r:03d}').get()
        if doc.exists:
            csvStringIO = StringIO(doc.to_dict()['data'])
            return jsonify(pd.read_csv(csvStringIO).to_dict())
        else:
            return jsonify({})

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(quizz_data)

#Serving with waitress
if __name__ == '__main__':
    print('Serving on http://localhost:8000/')
    serve(app, host='0.0.0.0', port=8000)
