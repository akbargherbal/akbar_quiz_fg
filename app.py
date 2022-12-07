from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import cross_origin

import utilities as ut
import pandas as pd
from zipfile import ZipFile
import os

try:
    list_tried_quizzes = pd.read_json('quizzes_result.json', encoding='utf-8')
    list_tried_quizzes = list(list_tried_quizzes['quiz_name'])
except:
    list_tried_quizzes = []

quiz_repo = os.listdir('quiz_repo')
quiz_repo_dict = {int(i.split('_')[0]):f'quiz_repo/{i}' for i in quiz_repo if i.endswith('.zip')}


app = Flask(__name__)
app.static_folder = 'static'

def clean_name_01(x):
    result =  x.split('/')[-1].split('.zip')[0].split('--')
    result = ' '.join(result)
    return result

quiz_repo = {k:clean_name_01(v) for k,v in quiz_repo_dict.items()}

@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def home():
    if request.method == 'GET':
        return render_template('home.html', quiz_repo= quiz_repo)
    else:
        try:
            print(f'{request.form.to_dict()}', flush=True)
            if 'request_quiz_name' in request.form.to_dict():
                quiz_id = int(request.form.get('request_quiz_name'))
                quiz_path = quiz_repo_dict[quiz_id]
                zf = ZipFile(quiz_path)
                quiz_path = ut.get_quiz_collection(quiz_path)
                #quiz_path = quiz_path[0] # Add condition to read only untried quizzes.
                quiz_path = list(set(quiz_path) - set(list_tried_quizzes))[0]

                print(f'Quiz_Path: {quiz_path}', quiz_path, flush=True)
        
                quiz_set_from_flask =  pd.read_csv(zf.open(quiz_path), encoding='utf-8').to_dict(orient = 'records')
                quiz_name_from_flask = quiz_path

                print(f'Quiz_Path: {quiz_path}', quiz_path, flush=True)
                language_from_flask = quiz_path.split('/')[0].split('_')[0]
                print(f'Language Code: {language_from_flask}', flush=True)

                kwargs = {'quiz_set_from_flask':quiz_set_from_flask, 
                        'quiz_name_from_flask':quiz_name_from_flask,
                        'language_from_flask': language_from_flask}

                return render_template('quiz.html', **kwargs)
            else:
                print(f'ELSE STATEMENT IN HOME PAGE:', flush=True)
                print('_'*100, flush=True)
                return render_template('home.html', quiz_repo= quiz_repo)

        except Exception as e:
            print(f'Error: {e}', flush=True)
            print(f'Exception Occured! Redirecting to Home Page:', flush=True)
            print('#'*100, flush=True)
            return render_template('home.html', quiz_repo= quiz_repo)





@app.route('/quiz' , methods=['POST', 'GET'])
@cross_origin()
def quiz():
    print('Entering QUIZ PAGE!!!', flush=True)
    if request.method == 'GET':
        return render_template('quiz.html')
    
    else:
        try:
            if 'quiz_result' in request.form.to_dict():
                print(f'''
    Quiz Result in Request Form Are Being Printed:
    {request.form.to_dict()}
    ''', flush=True)
                quiz_date = ut.get_datetime_now()
                q_results = request.form.to_dict()

                mistakes = [v for k,v in q_results.items() if k.startswith('wrong_answer')]
                
                quiz_result = {}
            
                print(f'Mistakes: {mistakes}, {type(mistakes)}', flush=True)

                quiz_result = {k:v for k,v in q_results.items() if ((k != 'quiz_result')  and (k.startswith('wrong_answer') == False))}
                print(f'Quiz Result: {quiz_result}', flush=True)
                quiz_result['date_time'] = quiz_date
                quiz_result['mistakes'] = mistakes

                ut.update_json_file_with_dict('quizzes_result.json', quiz_result)

                return render_template('home.html', quiz_repo= quiz_repo)

            else:
                print(f'ELSE STATEMENT IN QUIZ PAGE:', flush=True)
                print('_'*100, flush=True)
                return render_template('home.html', quiz_repo= quiz_repo)

        except Exception as e:
            print(f'Error: {e}', flush=True)
            print(f'Exception Occured in Quiz Page! Redirecting to Home Page:', flush=True)
            print('#'*100, flush=True)
            return render_template('home.html', quiz_repo= quiz_repo)




if __name__ == '__main__':
    app.run(debug=True)
