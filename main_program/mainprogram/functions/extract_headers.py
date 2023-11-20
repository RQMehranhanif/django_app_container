from collections import OrderedDict

from mainprogram.helpers.missing_log import has_missing_hyphens_or_two_segment_value

def get_headers( data_frame, file_name ):

    data = data_frame.to_csv(index=False).split('\r\n')

    references = data[1].split(',')

    if has_missing_hyphens_or_two_segment_value( references, file_name ): return False

    ar_headers = data[2].split(',')
    en_headers = data[3].split(',')
    sub_ar_headers = data[4].split(',')
    sub_en_headers = data[5].split(',')

    check = data[6].split(',')
    
    ar_level_3 = data[8].split(',')
    en_level_3 = data[9].split(',')

    # print( en_level_3 )

    sub_ar = ''
    sub_en = ''
    temp = OrderedDict()
    for i, ref in enumerate(references):
        if not ref == '-':
            ar = ar_headers[i] if not ar_headers[i] == '-' else ar
            en = en_headers[i] if not en_headers[i] == '-' else en
            c = check[i] if not check[i] == '-' else c

            sub_ar = sub_ar_headers[i] if not sub_ar_headers[i] == '-' else sub_ar  # Assign ar when hyphen occurs
            sub_en = sub_en_headers[i] if not sub_en_headers[i] == '-' else sub_en  # Assign en when hyphen occurs


            if c.strip() == 'Broken':
                sub_ar = ar_level_3[i] if not ar_level_3[i] == '-' else sub_ar
                sub_en = en_level_3[i] if not en_level_3[i] == '-' else sub_en
  


            # sub_en = sub_en_headers[i] if not sub_en_headers[i] == '-' else sub_en

            temp.update({
                ref: [ar.strip(), en.strip(), sub_ar.strip(), sub_en.strip(), False if not c.strip() == 'Broken' else True]
            })

    
    # values_to_remove = ['-']

    # new_list = [x.strip() for x in data if x not in values_to_remove]

    return temp