import sys
import argparse
import os
import json
import spacy
import html
import re
import string

indir = '/u/cs401/A1/data/';

with open("/u/cs401/Wordlists/abbrev.english") as file:
    abbreviation_list = set(file.read().lower().splitlines())
abbreviation_list.add("i.e.")
abbreviation_list.add("e.g.")

clitics_list = {"'d", "'n", "'ve", "'re", "'ll", "'m", "'re", "'s", "'t"}

def preproc1( comment , steps=range(1,11)):
    ''' This function pre-processes a single comment

    Parameters:
        comment : string, the body of a comment
        steps   : list of ints, each entry in this list corresponds to a preprocessing step

    Returns:
        modComm : string, the modified comment
    '''

    modComm = ''
    if 1 in steps:
        #remove new line characters
        modComm = comment.replace("\n", " ").replace("\r", " ")
    if 2 in steps:
        #should convert all according to reference: https://docs.python.org/3/library/html.html
        modComm = html.unescape(modComm)
    if 3 in steps:
        #matches http(s):// or www as required
        modComm = re.sub(r"((http[s]?:\/\/)|(www\.))+\S*","",modComm)
    if 4 in steps:
        tokens = re.split("\s+", modComm)
        tokens_mod = []

        for word in tokens:

            #case 2: keeping the periods in abbreviations
            if(word.lower() in abbreviation_list):
                tokens_mod.append(word)
            elif(re.search(r"[\!\"\#\$\%\&\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}~]+", word) is not None):
                #case 1, 3, 4: not matching apostrophes, keeping multiple punctuation together, and splitting hyphens (my choice)
                match = re.search(r"[\!\"\#\$\%\&\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}~]+", word)
                if(match is not None):
                    part1 = word[:match.start()]
                    part2 = word[match.start():match.end()]
                    part3 = word[match.end():]

                    if (part1 != ""):
                        tokens_mod.append(part1)

                    tokens_mod.append(part2)

                    if(part3 != ""):
                        tokens_mod.append(part3)
            else:
                tokens_mod.append(word)

        modComm = " ".join(tokens_mod)
    if 5 in steps:
        tokens = re.split("\s+", modComm)
        tokens_mod = []

        #deal with common case given clitics list
        for i in clitics_list:
            count = modComm.count(i)
            curr_index = 0

            #avoid finding the same clitic multiple times
            while count > 0:
                ind = modComm.find(i, curr_index)
                modComm = modComm[:ind] + " " + modComm[ind:]
                curr_index = ind + len(i)
                count -= 1

        #deal with the plural possessive case (s')
        for word in tokens:
            if(word.find("s'") != -1):
                ind = word.find("s'")
                tokens_mod.append(word[:ind+1])
                tokens_mod.append(word[ind+1:])
            else:
                tokens_mod.append(word)

        modComm = " ".join(tokens_mod)

    if 6 in steps:
        modComm = modComm

    if 7 in steps:
        modComm = modComm

    if 8 in steps:
        modComm = modComm

    if 9 in steps:
        modComm = modComm

    if 10 in steps:
       modComm = modComm.lower()

    return modComm

def main( args ):

    allOutput = []
    for subdir, dirs, files in os.walk(indir):
        for file in files:
            fullFile = os.path.join(subdir, file)
            print("Processing " + fullFile)

            data = json.load(open(fullFile))

            # TODO: select appropriate args.max lines
            # TODO: read those lines with something like `j = json.loads(line)`
            # TODO: choose to retain fields from those lines that are relevant to you
            # TODO: add a field to each selected line called 'cat' with the value of 'file' (e.g., 'Alt', 'Right', ...)
            # TODO: process the body field (j['body']) with preproc1(...) using default for `steps` argument
            # TODO: replace the 'body' field with the processed text
            # TODO: append the result to 'allOutput'
            print("num lines: " + str(len(data)))
            start = args.ID[0]%len(data)
            end = min(len(data), start+args.max)
            count = 0

            while count < args.max:

                print("starting point: "+str(start))
                print("ending point: " +str(end))
                for i in range(start, end):
                    line = data[i]
                    j = json.loads(line)
                    j = {'id':j['id'], 'body':j['body']}
                    j['cat'] = fullFile.split('/')[-1]
                    j['body'] = preproc1(j['body'])
                    allOutput.append(j)
                    count+=1

                if count<args.max:
                    start = 0
                    end = args.max - count
                    print("WRAPPED")

            print("total records: " +str(len(allOutput)))

    fout = open(args.output, 'w')
    fout.write(json.dumps(allOutput))
    fout.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process each .')
    parser.add_argument('ID', metavar='N', type=int, nargs=1,
                        help='your student ID')
    parser.add_argument("-o", "--output", help="Directs the output to a filename of your choice", required=True)
    parser.add_argument("--max", help="The maximum number of comments to read from each file", default=10000)
    args = parser.parse_args()

    if (args.max > 200272):
        print("Error: If you want to read more than 200,272 comments per file, you have to read them all.")
        sys.exit(1)

    main(args)
