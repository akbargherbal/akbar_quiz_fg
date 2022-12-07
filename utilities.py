from collections import defaultdict
import pandas as pd
from zipfile import ZipFile
import os
from datetime import datetime
from pathlib import Path

def get_datetime_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

