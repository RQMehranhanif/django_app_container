import json
from tkinter import messagebox
from mysql.connector import Error
from datetime import datetime

from requests import HTTPError


from mainprogram.functions.arrange_data import arrange_data
from mainprogram.functions.related_words import insert_data_into_table
from mainprogram.helpers.db import db_connection
from mainprogram.helpers.get_word_ids import get_word_ids
from mainprogram.helpers.missing_log import other_log

def fetch_existing_data(cursor, table_morphemes, root_word_id):
    select_query = f"SELECT * FROM {table_morphemes} WHERE root_word_id = %s"
    cursor.execute(select_query, (root_word_id,))
    return cursor.fetchone()

def update_or_insert_data(cursor, table_name, root_word_id, entry, process_type):
    update_sql = f"UPDATE {table_name} SET sheet_words = %s, updated_at = %s WHERE root_word_id = %s AND morpheme_no = %s AND weight = %s"
    insert_sql = f"INSERT INTO {table_name} (sheet_words, created_at, root_word_id, morpheme_no, weight) VALUES (%s, %s, %s, %s, %s)"

    values = (
        json.dumps(entry["sheet_words"], ensure_ascii=False),
        datetime.now(),
        root_word_id[0],
        entry["morpheme_no"],
        entry["weight"]
    )
    sql = update_sql if root_word_id[1] == "update" else insert_sql

    cursor.execute(sql, values)

def save_json_data(file, dataset):
    json_output = json.dumps(dataset, ensure_ascii=False, indent=4)

    with open(f"sample_files/{file.split('/')[-1]}.json", "w", encoding="utf-8") as json_file:
        json_file.write(json_output)

    print(f"JSON data with key-value pairs has been written to 'sample_files/{file.split('/')[-1]}.json'")

def get_word_id(form, morpheme, group, sub_group, word_number, result):
    matching_words = result[0]
    references = result[1]

    for ref in references:
        _ = ref.split(':')
        _form       =  int( _[0] )
        _morf       =  int( _[1] )
        _group      =  int( _[2] )
        _sub_group  =  float( _[3] )
        _word_number=  _[4]

        if _form == int(form) and _morf == int(morpheme) and _group == int(group) and _sub_group == float(sub_group) and _word_number == word_number:
            if other_log( [i for i in matching_words[ref]], ref ):
                return False
            return sorted( [int(i) for i in matching_words[ref]] )

    return []


def create_dataset(forms, broken_plurals, headers, word_number_lines, result):
    dataset = []

    for form, form_data in enumerate(forms):
        for index, row in enumerate(form_data):
            word_number_index = 0
            row_data = []
            b = ''
            for i in range(0, len(row), 2):
                word_number = word_number_lines[word_number_index]
                word_number_index += 1
                key = row[i + 1]
                value = row[i]
                n = form * len(form_data) + index
                b = broken_plurals.get(word_number, b)

                word_ids = get_word_id((form + 1), (index + 1) if len(form_data) < len(forms[0]) else index, word_number.split('.')[0], '.'.join(word_number.split('.')[0:2]), word_number, result)
                if not word_ids and isinstance(word_ids, bool): 
                    return True
                
                row_data.append({
                    "morpheme_no": (index + 1) if len(form_data) < len(forms[0]) else index,
                    "weight": form + 1,
                    "word": value,
                    "word_id": word_ids,
                    "template": '' if (key == '-' or key is None) else key,
                    "group": word_number.split('.')[0],
                    "subgroup": '.'.join(word_number.split('.')[0:2]),
                    "word_number": word_number,
                    "ar": headers[word_number][0],
                    "en": headers[word_number][1],
                    "sub_ar": headers[word_number][2],
                    "sub_en": headers[word_number][3],
                    "isbroken": headers[word_number][4],
                    "broken_plurals": (b if headers[word_number][4] else '') if form == 0 and index == 0 else ''
                })
            dataset.append({
                "morpheme_no": (index + 1) if len(form_data) < len(forms[0]) else index,
                "weight": form + 1,
                "sheet_words": row_data
            })

    return dataset

def execute_sql(connection, cursor, table_name, root_word_id, dataset, process_type):
    for entry in dataset:
        update_or_insert_data(cursor, table_name, root_word_id, entry, process_type)

    connection.commit()
    print("Data inserted successfully!")

def process_file(file, process_type, db_type):
    # 'Local': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'morpheme_new_8_22_23',
    #     'USER': 'root',
    #     'PASSWORD': '',
    #     'HOST': '127.0.0.1',
    #     'PORT': '3306', 
    # }
    table_name = 'morpheme_details'
    table_morphemes = 'morphemes'
    if not arrange_data(file):
        return False
    forms, broken_plurals, headers, word_numbers, word_number_lines, data_frame_result = arrange_data(file)

    result = get_word_ids( data_frame_result )

    if not forms:
        return False

    if process_type == 'db':
        connection = db_connection(db_type)
        if not connection:
            messagebox.showerror("Error", f"Database settings are missings!")
            return False

    try:
        # if data is not None:
        #     print(data)
        dataset = create_dataset(forms, broken_plurals, headers, word_number_lines, result)

        if not dataset:
            return False
        
        if process_type == 'db' and connection:
            with connection.cursor() as cursor:

                existing_data = fetch_existing_data(cursor, table_morphemes, data_frame_result['root_word_id'].values[0])
                if existing_data:
                    confirm_update = messagebox.askyesno("Data Exists", f"Data against root word id {data_frame_result['root_word_id'].values[0]} already exists in the database. Do you want to update it?")
                    if not confirm_update:
                        exit()

                root_word_id = data_frame_result['root_word_id'].values[0]
                root_word_id = insert_data_into_table(connection, table_morphemes, data_frame_result, existing_data)

                execute_sql(connection, cursor, table_name, root_word_id, dataset, process_type)
        if process_type == "json":
            save_json_data(file, dataset)

    except Error as e:
        if process_type == "db" and connection:
            connection.rollback()
        print("Error:", e)

    finally:
        if process_type == "db" and connection.is_connected() and connection:
            connection.close()
            print("Database connection closed.")

    return True