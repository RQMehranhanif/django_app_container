import pandas as pd
from mainprogram.functions.broken_plural_by_group_name import arrange_broken

from mainprogram.functions.extract_headers import get_headers
from mainprogram.helpers.message_box import show_popup_message


def arrange_data( file ):
    try:
        excel_file = file # "Word-Xforms-samawa-V-1.29.xlsx"
        file_name = excel_file.split('/')[-1]
        data_frame = pd.read_excel(excel_file, sheet_name='Main').fillna('-')

        # Remove extra columns 
        data_frame = data_frame.iloc[:, 4:-3]

        # headers = data_frame[3:12].to_csv(index=False).split('\r\n')[6]
        headers = get_headers(data_frame[3:12], file_name)
        if not headers:
            show_popup_message(f'There are missing hyphens or two-segment values. See "log_files/{file_name}_missing.log" for details.')
            return False


        data_frame_result = pd.read_excel(excel_file, sheet_name='Result').fillna('-')

        # Drop the first column
        data_frame_result = data_frame_result.drop( data_frame_result.iloc[:, 5:] , axis=1)

        # Assuming you have a DataFrame named "dataframe" and you want to rename columns
        data_frame_result.rename(columns={'Unnamed: 0': 'reference','Unnamed: 1': 'root_word_id', 'Unnamed: 2': 'root_word', 'Unnamed: 3': 'word', 'Unnamed: 4': 'word_ids'}, inplace=True)

        # word_numbers
        word_numbers = data_frame[3:4].to_csv(header=False).replace(",-", "")
        word_number_lines = word_numbers.strip().split(',')
        word_number_lines.pop(0)

        broken_plurals = arrange_broken( data_frame[3:12] )

        form1  = data_frame.iloc[13:28].values
        form2  = data_frame.iloc[31:46].values # plus 3 - rows, plus 15 - rows
        form3  = data_frame.iloc[49:64].values # plus 3 - rows, plus 15 - rows
        form4  = data_frame.iloc[67:82].values # plus 3 - rows, plus 15 - rows
        form5  = data_frame.iloc[85:100].values # plus 3 - rows, plus 15 - rows
        form6  = data_frame.iloc[103:118].values # plus 3 - rows, plus 15 - rows
        form7  = data_frame.iloc[121:136].values # plus 3 - rows, plus 15 - rows
        form8  = data_frame.iloc[139:154].values # plus 3 - rows, plus 15 - rows
        form9  = data_frame.iloc[157:172].values # plus 3 - rows, plus 15 - rows
        form10 = data_frame.iloc[175:190].values # plus 3 - rows, plus 15 - rows

        broken_plural = data_frame.iloc[12:13].values
        forms = [[*broken_plural, *form1], form2, form3, form4, form5, form6, form7, form8, form9, form10]

        return [ forms, broken_plurals, headers, word_numbers, word_number_lines, data_frame_result[31:] ]
    except:
        return False