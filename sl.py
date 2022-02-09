import pandas as pd


def register_item(dir_name, results):
    if results:
        if results[0]['score'] > 0.6:
            logid = dir_name[5:-1]
            result = results[0]['keyword']
            df = pd.read_excel('answer.xlsx')
            df = df.appdend({'logid': logid, 'result': result})
