import numpy as np
import sys
import argparse
import os
import json
import re
import pandas as pd


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
    feats[13] = len(re.findall(r"\b(\S*[A-Z]\S*){3,}\/", comment))
    feats[16] = len(re.findall(r"\n\b", comment))
    feats[14] = 0 if feats[16] == 0 else len(re.findall(r"\S\/\S", comment)) / feats[16]
    feats[15] = 0 if feats[14] - feats[7] <= 0 else len(re.findall(r"\w\S*\/", comment)) / feats[14] - feats[7]
    feats[17:23] = get_BGL(comment)
    feats[23:29] = get_warringer(comment)

    return feats

def get_BGL(comment):
    """ This function extracts all the information from BGL
    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        final_array: the 6 calculated values of BGL

    """

    df_bgl = pd.read_csv("/u/cs401/Wordlists/BristolNorms+GilhoolyLogie.csv")
    flag_check = False
    AoA = IMG = FAM = []
    tokens = re.sub(r"(\S+)\/(\S+)", r"\1", comment)
    tokens = tokens.split(" ")

    for word in tokens:
        if word in df_bgl['WORD']:
            flag_check = True
            index = df_bgl.loc[df_bgl['WORD']==word].index[0]
            AoA.append(df_bgl.iloc[index]["AoA (100-700)"])
            IMG.append(df_bgl.iloc[index]["IMG"])
            FAM.append(df_bgl.iloc[index]["FAM"])

    if flag_check == False:
        return np.zeros((6,))

    AoA = np.array(AoA).astype(np.float)
    IMG = np.array(IMG).astype(np.float)
    FAM = np.array(FAM).astype(np.float)

    final_array = [np.mean(AoA), np.mean(IMG), np.mean(FAM), np.std(AoA), np.std(IMG), np.std(FAM)]

    return final_array


def get_warringer(comment):
    """ This function extracts all the information from warringer
    Parameters:
        comment : string, the body of a comment (after preprocessing)

    Returns:
        final_array: the 6 calculated values of warringer

    """

    df_war = pd.read_csv("/u/cs401/Wordlists/Ratings_Warriner_et_al.csv")
    flag_check = False
    V = A = D = []
    tokens = re.sub(r"(\S+)\/(\S+)", r"\1", comment)
    tokens = tokens.split(" ")

    for word in tokens:
        if word in df_war['Word']:
            flag_check = True
            index = df_bgl.loc[df_bgl['Word']==word].index[0]
            AoA.append(df_bgl.iloc[index]["V.Mean.Sum"])
            IMG.append(df_bgl.iloc[index]["A.Mean.Sum"])
            FAM.append(df_bgl.iloc[index]["D.Mean.Sum"])

    if flag_check == False:
        return np.zeros((6,))

    V = np.array(V).astype(np.float)
    A = np.array(A).astype(np.float)
    D = np.array(D).astype(np.float)

    final_array = [np.mean(V), np.mean(A), np.mean(D), np.std(V), np.std(A), np.std(D)]

    return final_array

def gen_regex(file_name):
    """
    Parameters:
        file_name : string, filename where we would extract the list to count
    """

    with open(file_name) as file:
        regex_list = set(file.read().lower().splitlines())

    if ('' in regex_list):
        regex_list.remove('')

    return regex_list


def count_regex( file_name, comment ):
    """
    This function returns a regex given a list taken from a file

    Parameters:
        regex_list :
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

def get_liwc(comment_id, cat):
    filename = "/u/cs401/A1/feats/" + cat + "_IDs.txt"
    line_num = 0
    with open(filename) as myFile:
        for num, line in enumerate(myFile, 1):
            if comment_id in line:
                line_num = num
                break

    feats = np.load("/u/cs401/A1/feats/"+ cat +"_feats.dat.npy")
    return feats[line_num]


def main( args ):

    data = json.load(open(args.input))
    feats = np.zeros( (len(data), 173+1))
    features = np.zeros((174,))
    # TODO: your code here
    transform_cat = {"Left": 0, "Center": 1, "Right": 2, "Alt": 3}

    for i in range(len(data)):
        entry = data[i]
        data_body = entry["body"]
        data_class = entry["cat"]
        data_id = entry["id"]
        feats[i][0:29] = extract1(data_body)
        #one for liwc
        feats[i][29:173] = get_liwc(data_id, data_class)
        #one for cat to int
        feats[i][-1] = transform_cat[data_class]

    #print("save")
    np.savez_compressed( args.output, feats)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("-i", "--input", help="The input JSON file, preprocessed as in Task 1", required=True)
    args = parser.parse_args()


    main(args)

