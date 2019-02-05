import sys
import argparse
import os
import json
import spacy
import html
import re
import string

indir = '/u/cs401/A1/data/';

nlp = spacy.load('en', disable=['parser', 'ner'])

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
        with open("/u/cs401/Wordlists/abbrev.english") as file:
            abbreviation_list = set(file.read().lower().splitlines())
        abbreviation_list.add("i.e.")
        abbreviation_list.add("e.g.")

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
        #deal with common case given clitics list
        modComm = re.sub(r"(\w)('d|n't|'ve|'re|'ll|'m|'s)", r"\1 \2", modComm, flags=re.IGNORECASE)

        #deal with special cases
        modComm = re.sub(r"s' ", r"s ' ", modComm, flags=re.IGNORECASE)
        modComm = re.sub(r"(y|Y)'(\w)", r"y '\2", modComm, flags=re.IGNORECASE)

    if 6 in steps:
        utt = nlp(modComm)
        tokens_mod = []
        for word in utt:
            tagged_word = "{0}/{1}".format(word, word.tag_)
            tokens_mod.append(tagged_word)

        modComm = " ".join(tokens_mod)

    if 7 in steps:

        modComm = re.sub(r"(\S+)\/(\S+)", rm_stopwords, modComm)

    if 8 in steps:

        modComm = lemmatize(modComm)

    if 9 in steps:
        #using sentence boundary as described in 4.2.4
        tokens = re.split("\s+", modComm)
        tokens_mod = []
        ending_punctuation_list = {".", "!", "?"}

        for i in range(len(tokens)):
            index = tokens[i].rfind("/")
            token = tokens[i][:index].lower()
            if not token:
                continue

            if(i<len(tokens)-1):
                index_next = tokens[i+1].rfind("/")
                token_next = tokens[i+1][:index_next]
            #known abreviation not sentence
            if(token[-1] in ending_punctuation_list and token not in abbreviation_list):
                tokens_mod.append(tokens[i]+"\n")
            #end of punctuation, but next word isn't capitalized
            elif(i<len(tokens)-1 and token[-1] in ending_punctuation_list and token_next[0].islower()):
                tokens_mod.append(tokens[i]+"\n")
            else:
                tokens_mod.append(tokens[i])

        modComm = " ".join(tokens_mod)

    if 10 in steps:
        modComm = re.sub(r"(\S+)\/(\S+)", lambda pattern: pattern.group(1).lower() + "/" + pattern.group(2), modComm)

    return modComm

def rm_stopwords(p):
    with open("/u/cs401/Wordlists/StopWords") as file:
        stopword_list = set(file.read().lower().splitlines())

    if p.group(1).strip().lower() in stopword_list:
        return ""
    else:
        return p.group(0)

def lemmatize(l):
    l = re.sub(r"(\S+)\/(\S+)", r"\1", l)
    l = l.strip()
    l = re.sub(r"\s+", " ", l)
    doc = nlp(l)
    result = ""
    for word in doc:
        if(word.lemma_.startswith("-")):
            result = result+word.text+"/"+word.tag_+" "
        else:
            result = result+word.lemma_+"/"+word.tag_+" "

    return result


def main( args ):

    allOutput = []
    for subdir, dirs, files in os.walk(indir):
        for file in files:
            fullFile = os.path.join(subdir, file)
            print("Processing " + fullFile)

            data = json.load(open(fullFile))

            print("num lines: " + str(len(data)))
            #select appropriate args.max lines
            start = args.ID[0]%len(data)
            end = min(len(data), start+args.max)
            count = 0

            while count < args.max:

                print("starting point: "+str(start))
                print("ending point: " +str(end))
                #read those lines with something like `j = json.loads(line)`
                for i in range(start, end):
                    line = data[i]
                    j = json.loads(line)
                    #choose to retain fields from those lines that are relevant to you
                    j = {'id':j['id'], 'body':j['body']}
                    #add a field to each selected line called 'cat' with the value of 'file' (e.g., 'Alt', 'Right', ...)
                    j['cat'] = fullFile.split('/')[-1]
                    #process the body field (j['body']) with preproc1(...) using default for `steps` argument
                    #replace the 'body' field with the processed text
                    j['body'] = preproc1(j['body'])
                    #append the result to 'allOutput'
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
    #TODO:CHANGE BACK TO 10000
    parser.add_argument("--max", type=int, help="The maximum number of comments to read from each file", default=10000)
    args = parser.parse_args()

    if (args.max > 200272):
        print("Error: If you want to read more than 200,272 comments per file, you have to read them all.")
        sys.exit(1)

    main(args)
