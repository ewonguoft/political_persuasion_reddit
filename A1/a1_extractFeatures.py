import numpy as np
import sys
import argparse
import os
import json
import re

def extract1( comment ):
    ''' This function extracts features from a single comment

    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        feats : numpy Array, a 173-length vector of floating point features (only the first 29 are expected to be filled, here)
    '''

    feats = np.zeros((29,))
    feats[0] = count_regex("/u/cs401/Wordlists/First-person", comment)
    feats[1] = count_regex("/u/cs401/Wordlists/Second-person", comment)
    feats[2] = count_regex("/u/cs401/Wordlists/Third-person", comment)
    feats[3] = len(re.findall(r"\/CC\b", comment))
    feats[4] = len(re.findall(r"\/VBD\b", comment))
    feats[5] = len(re.findall(r"\b('ll|will|gonna)\/", comment)) + len(re.findall(r"\bgoing\/\S+ to\/\S+ \S+\/VB\b", comment))
    feats[6] = len(re.findall(r"\b,\/,\b", comment))
    feats[7] = len(re.findall(r"\b[\!\"\#\$\%\&\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}~]+\/", comment))
    feats[8] = len(re.findall(r"\/NNS?\b", comment))
    feats[9] = len(re.findall(r"\/NNPS?\b", comment))
    feats[10] = len(re.findall(r"\/RB(R|S)?\b", comment))
    feats[11] = len(re.findall(r"\/(WDT|WP|WP\$|WRB)\b", comment))
    feats[12] = count_regex("/u/cs401/Wordlists/Slang", comment)
    feats[13] = len(re.findall(r"\b(\S*[A-Z]){3}\/", comment ))
    #print(feats[13])


    return feats

def count_regex( file_name, comment ):
    """
    This function returns a regex given a list taken from a file

    Parameters:
        file_name : string, filename where we would extract the list to count
        comment : string, the body of a comment (after preprocessing)
    Returns:
        count: num of ocurrences of the words in file_name
    """
    with open(file_name) as file:
        regex_list = set(file.read().lower().splitlines())

    if ('' in regex_list):
        regex_list.remove('')

    regex = re.findall(r'\b(%s)\/' % '|'.join(regex_list), comment)

    return len(regex)

def main( args ):

    data = json.load(open(args.input))
    feats = np.zeros( (len(data), 173+1))
    features = np.zeros((174,))
    # TODO: your code here


    for i in range(5):
        entry = data[i]
        data_body = entry["body"]
        data_class = entry["cat"]
        data_id = entry["id"]
        feats[i][0:29] = extract1(data_body)
        #one for liwc
        #one for cat to int
        #add to feats

    np.savez_compressed( args.output, feats)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()


    main(args)

