import pprint


def get_word_ids( data_frame ):

    original_list = []
    ref_list = []

    for index, row in data_frame.iterrows():
        values = [row[col] for col in data_frame.columns]
        split_values = [item.strip() for item in str(values[-1]).split(',')]
        original_list.append( split_values )
        ref_list.append( values[0] )

    # return [original_list, ref_list]
    
    # Initialize an empty dictionary
    result_dict = {}

    # Iterate through the original list and create dictionary entries
    for _, inner_list in enumerate( original_list ):
        # key = str(inner_list[0])  # Use the first element as the key (converted to a string)
        value = inner_list  # The entire inner list is the value
        # result_dict[key] = value
        # result_dict[ref_list[_]] = value

        if ref_list[_] in result_dict:
            # If the key already exists, merge the values
            result_dict[ref_list[_]] += value
        else:
            # If the key doesn't exist, create a new entry
            result_dict[ref_list[_]] = value

    # Print the resulting dictionary
    return [result_dict, ref_list]
