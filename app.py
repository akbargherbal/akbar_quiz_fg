from flask import Flask, render_template, request, redirect, url_for, session
from flask_cors import cross_origin

import utilities as ut
import pandas as pd
from zipfile import ZipFile
import os

bucket =  'akbar-quiz-app-april-2023'
blob_path = 'RESULTS/quizzes_result.json'
file_results = 'quizzes_result.json'

if os.path.isfile(file_results):
    pass
else:
    ut.download_from_gcp_storage(bucket=bucket, blob_path=blob_path, file=file_results)
    print('Downloaded from GCP Storage')

app = Flask(__name__)
app.secret_key = 'secret_key'
app.static_folder = 'static'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def home():
    if request.method == 'GET':
        quiz_repo = ut.get_buttons_names()
        return render_template('home.html', quiz_repo= quiz_repo)
    
    else:
        print(f'Form: {request.form}', flush=True)
        quiz_id = int(request.form.get('request_quiz_name'))
        print(f'Quiz_ID: {quiz_id}', flush=True)
        session['quiz_id'] = quiz_id

        return redirect(url_for('quiz')) # we want to redirect user to quiz page; passing quiz data through session.


@app.route('/quiz' , methods=['POST', 'GET'])
@cross_origin()
def quiz():
    if request.method == 'GET':
        new_quiz = ut.get_new_quiz(session['quiz_id'])
        kwargs = {
            'quiz_set_from_flask': new_quiz['quiz_set_from_flask'],
            'quiz_name_from_flask': new_quiz['quiz_name_from_flask'],
            'language_from_flask': new_quiz['language_from_flask']
        }

        return render_template('quiz.html', **kwargs)
    
    else:
        quiz_date = ut.get_datetime_now()
        q_results = request.form.to_dict()

        mistakes = [v for k,v in q_results.items() if k.startswith('wrong_answer')]

        quiz_result = {}

        print(f'Mistakes: {mistakes}, {type(mistakes)}', flush=True)

        quiz_result = {k:v for k,v in q_results.items() if ((k != 'quiz_result')  and (k.startswith('wrong_answer') == False))}
        print(f'Quiz Result: {quiz_result}', flush=True)
        quiz_result['date_time'] = quiz_date
        quiz_result['mistakes'] = mistakes

        if os.path.isfile(file_results):
                pass
        else:
            ut.download_from_gcp_storage(bucket=bucket, blob_path=blob_path, file=file_results)
            print('Downloaded from GCP Storage')

        ut.update_json_file_with_dict(file_results, quiz_result)
        ut.upload_to_gcp_storage(bucket=bucket, blob_path=blob_path, file=file_results)

        return redirect(url_for('home'))

@app.route('/quizzes_history')
@cross_origin()
def quizzes_history():
    try:
        ut.download_from_gcp_storage(bucket=bucket, blob_path=blob_path, file=file_results)
        table_from_flask = ut.make_html_table(file_results)
        return render_template('quizzes_history.html', table_from_flask=table_from_flask)

    except:
        return render_template ('quizzes_history.html')



if __name__ == '__main__':
    app.run(debug=True)
