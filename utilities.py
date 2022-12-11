from collections import defaultdict
import pandas as pd
from zipfile import ZipFile
import os
from datetime import datetime
from pathlib import Path
import pickle
import re

def get_datetime_now():
    return datetime.now()

def get_quiz_collection(zip_file_path, file_ext='csv'):
    zf = ZipFile(zip_file_path)
    quiz_collections  = []
    for i in zf.filelist:
        if i.filename.endswith(f'.{file_ext}'):
            quiz_collections.append(i.filename)

    return quiz_collections

def append_dict_to_df(df_x, dict_x):
    df_temp = pd.DataFrame(data=dict_x.values(), index=dict_x.keys()).T
    result = pd.concat([df_x, df_temp], ).reset_index(drop=True)
    return result


def update_json_file_with_dict(path_to_json, dict_x, save_file=True):
    '''Update json file with dict, if the file does not exist, create a new one'''
    js_file = Path(path_to_json)
    if js_file.is_file() == False:
        df_old = pd.DataFrame(data = {i:[] for i in dict_x.keys()})
    else:
        df_old = pd.read_json(path_to_json, encoding='utf-8')
        
    result = append_dict_to_df(df_old, dict_x).reset_index(drop=True)
    
    if save_file:
        result.to_json(path_to_json, orient='records', force_ascii = False)
    return result

def clean_name_01(x):
    '''
    input: x = 'quiz_repo/01_EN_NOUN_AV--16NOV2022.zip'
    Clean the name of the buttons on the home page
    '''
    result =  x.split('/')[-1].split('.zip')[0].split('--')
    result = ' '.join(result).strip()
    return result


def get_buttons_names():
    '''return clean names for the buttons used to select quiz name; populated by js'''
    quiz_repo = os.listdir('quiz_repo')
    quiz_repo_dict = {int(i.split('_')[0]):f'quiz_repo/{i}' for i in quiz_repo if i.endswith('.zip')}
    quiz_repo_dict = {k: clean_name_01(v) for k,v in quiz_repo_dict.items()}
    return quiz_repo_dict


def get_new_quiz(quiz_id):
    '''Given an integer idx; give a new quiz of that type; checking against a database'''
    try:
        list_tried_quizzes = pd.read_json('quizzes_result.json', encoding='utf-8')
        list_tried_quizzes = list(list_tried_quizzes['quiz_name'])
    except:
        list_tried_quizzes = []
        
    quiz_repo = os.listdir('quiz_repo') # potential troubles!!
    quiz_repo_dict = {int(i.split('_')[0]):f'quiz_repo/{i}' for i in quiz_repo if i.endswith('.zip')}
        
    quiz_path = quiz_repo_dict[quiz_id]
    zf = ZipFile(quiz_path)
    quiz_path = get_quiz_collection(quiz_path)
    quiz_path = list(set(quiz_path) - set(list_tried_quizzes))[0]
    quiz_set_from_flask =  pd.read_csv(zf.open(quiz_path), encoding='utf-8').to_dict(orient = 'records')
    language_from_flask = quiz_path.split('_')[0]
    quiz_name_from_flask = quiz_path

    result_dict = {'quiz_set_from_flask': quiz_set_from_flask,
                 'quiz_name_from_flask': quiz_name_from_flask, 
                 'language_from_flask': language_from_flask}
    return result_dict




def make_html_table(df_path):
    df = pd.read_json(df_path, encoding='utf-8')
    df['TIME'] = df['date_time'].apply(lambda x: str(pd.Timestamp.time(x)).split('.')[0])
    df['DATE'] = df['date_time'].apply(lambda x: str(pd.Timestamp.date(x)))
    df['QUIZ_COLLECTION'] = df['quiz_name'].apply(lambda x: x.split('/')[0])
    df['QUIZ_NAME'] = df['quiz_name'].apply(lambda x: x.split('/')[-1])
    df = df['TIME DATE QUIZ_COLLECTION QUIZ_NAME mistakes quiz_duration_minutes	number_of_wrong_answers' .split()]
    df['IDX'] = df.index + 1
    df_cols = df.columns.tolist()
    df_cols_rename = {i:i.title().replace('_', ' ') for i in df_cols if i not in 'IDX'.split()}
    df = df.rename(columns=df_cols_rename)
    df = df [['IDX', 'Time', 'Date', 'Quiz Collection', 'Quiz Name', 'Mistakes', 'Quiz Duration Minutes', 'Number Of Wrong Answers']]

    old_table_class = '<table border=.*? class=\"dataframe\">'
    new_table_class = '<table class="table table-bordered table-dark table-hover text-center">'
    old_tr_style = '<tr style=\"text-align: right;\">'
    new_tr_style = '<tr>'
    old_date = '<th>Date</th>'
    new_date = '<th>Date of Quiz</th>'

    
    html_code = df.to_html(index=False)
    html_code = re.sub(old_table_class, new_table_class, html_code)
    html_code = re.sub(old_tr_style, new_tr_style, html_code)
    html_code = re.sub(old_date, new_date, html_code)
    
    return html_code