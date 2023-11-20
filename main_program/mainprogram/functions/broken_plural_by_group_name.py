from collections import OrderedDict
import pprint

def arrange_broken(dataset):
    dataset = dataset.to_csv(index=False).split('\r\n')
    data = dataset[7].split(',')
    check_list = dataset[6].split(',')
    ref = dataset[1].split(',')

    check = []
    for i, ba in enumerate( check_list ):
        c = ba if not ba == '-' else c
    
        check.append( c )

    data_list = []  # To store the extracted data'
    ref_list = []
    temp = []
    current_heading = None  # To keep track of the current heading

    for i, word in enumerate( data ):  # Replace "your_dataset" with your actual list
        if word != '-':  # Check if the word is not a hyphen
            if current_heading is None:
                current_heading = word  # Set the current heading
                temp = []
                temp.append( ref[i] )
                ref_list.append( temp )

            else:
                data_list.append((current_heading, word))  # Append (heading, data) pair
                temp.append( ref[i] )
                current_heading = None  # Reset the current heading
        else: 
            if check[i] == "Broken":
                temp.append( ref[i] )

    broken = OrderedDict()
    for i, data in enumerate( data_list ):
        broken.update({
            ref_list[i][0]: {
                "word" : data[0] if not data[0].strip() == "no" and not data[0].strip() == "none" else '',
                "template": data[1],
                "references": [_ for _ in ref_list[i] if not _ == '-'] 
        }})
    
    return broken
