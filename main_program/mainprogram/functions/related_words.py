import json
from datetime import datetime
from mysql.connector import Error

def insert_data_into_table(connection, table_name, df, existing_data):

    try:
        df['reference'] = df['reference'].astype(str).str.split('/').str.join(',')

        # Extract the first value from "word_ids" and store it in a new column "word_id"
        df['word_id'] = df['word_ids'].astype(str).str.split(',').str[0].astype(int)
        
        # Remove the first value from "word_ids" column
        df['matching_word_ids'] = df['word_ids'].astype(str).str.split(',').str[1:].str.join(',')
        df.drop(columns=['word_ids'], inplace=True)

        # print(df)
        # exit()

        cursor = connection.cursor()

        placeholders = ', '.join(['%s'] * 8)
        insert_query = f"INSERT INTO {table_name} ( sheet_reference, root_word_id, root_word, word, word_id, matching_words, created_at, word_reference) VALUES ({placeholders})"
        for index, row in df.iterrows():

            values = [row[col] for col in df.columns]

            word_id = values[4]

            # Convert the number to a string to manipulate it
            number_str = str( word_id )[1:]  # Remove the first digit
            part1 = int( number_str[:3] )
            part2 = int( number_str[3:6] )
            part3 = int( number_str[6:] )

            word_reference = f'{part1}:{part2}:{part3}'

            last_item = values[-1]

            # Split the last item by commas and remove spaces from each element
            references = [item.strip() for item in values[0].split(',')]
            split_values = [item.strip() for item in last_item.split(',')]

            values[0] = json.dumps( references )
            values[-1] = json.dumps( split_values )
            values.append( datetime.now() ) # Current timestamp
            values.append( word_reference )

            # return values

            if existing_data:
                # Data exists, update it
                update_query = f"UPDATE {table_name} SET sheet_reference = %s, updated_at = %s WHERE root_word_id = %s and word_id = %s"
                cursor.execute(update_query, (values[0], datetime.now(), values[1], values[4]))
            else:
                cursor.execute(insert_query, values)
        connection.commit()
        cursor.close()

        action = "update" if existing_data else "insert"
        return [df['root_word_id'].values[0], action]
    
    except Error as e:
        print("Error:", e)
        return False
