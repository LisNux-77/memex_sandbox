# NEW LIBRARIES
import pandas as pd
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.metrics.pairwise import cosine_similarity

import os, json, re, sys

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #load yaml file with important, constant settings

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

def filterTfidfDictionary(dictionary, threshold, lessOrMore): #function with 3 parameters
    dictionaryFilt = {} #create dictionary
    for item1, citeKeyDist in dictionary.items(): #loop through dictionary layer 1
        dictionaryFilt[item1] = {} #dictionary for filtered items
        for item2, value in citeKeyDist.items(): #loop through dictionary layer 2
            if lessOrMore == "less": #if condition "less" for threshold value
                if value <= threshold: #if value smaller than set threshold, then
                    if item1 != item2: 
                        dictionaryFilt[item1][item2] = value #add value to filtered dic
            elif lessOrMore == "more": #if condition "more" for threshold value
                if value >= threshold: #if value bigger than set threshold, then
                    if item1 != item2:
                        dictionaryFilt[item1][item2] = value #add value to filtered dic
            else:
                sys.exit("`lessOrMore` parameter must be `less` or `more`") #set error message if given parameter is faulty

        if dictionaryFilt[item1] == {}: #if empty dic, then 
            dictionaryFilt.pop(item1) #delete item
    return(dictionaryFilt) #give back filtered dic


def tfidfPublications(pathToMemex): # define function with 1 parameter
    # PART 1: loading OCR files into a corpus
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, ".json") #use pre-defined function -> dic of .json files in memex
    citeKeys = list(ocrFiles.keys()) #list of all keys in dic

    print("\taggregating texts into documents...")
    docList   = [] #empty list to be filled with texts
    docIdList = [] #empty list to be filled with citekeys

    for citeKey in citeKeys: #initiate for-loop through citekey list
        docData = json.load(open(ocrFiles[citeKey])) #reads in the data of the respective citekey 

        docId = citeKey #sets variable docID to the respective citekey of each loop run
        doc   = " ".join(docData.values()) #connects docData values with whitespace

        # clean doc
        doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc) #replaces pattern of "alphanumeric character - alphanumeric characters" 
        doc = re.sub('\W+', ' ', doc) #replaces non-word characters with whitespace 
        doc = re.sub('\d+', ' ', doc) #replaces digits with whitespace
        doc = re.sub(' +', ' ', doc) #replaces multiple whitespaces with single whitespace

        # update lists
        docList.append(doc) #add doc to list
        docIdList.append(docId) #add docId to list

    print("\t%d documents generated..." % len(docList))

    # PART 2: calculate tfidf for all loaded publications and distances
    print("\tgenerating tfidf matrix & distances...")
    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=5, max_df=0.5) #create vectorizer (only unigrams, threshold: 0.5 < df_word > 5)
    countVectorized = vectorizer.fit_transform(docList) #built-in function
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True) #built-in function
    vectorized = tfidfTransformer.fit_transform(countVectorized) #matrix with calculated tf-idf
    cosineMatrix = cosine_similarity(vectorized) #matrix with calculated cosine similarity

    # PART 3: saving TFIDF
    print("\tsaving tfidf data...")
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names()) #create pandas dataframe, index=citekey, columns=words 
    tfidfTable = tfidfTable.transpose() #writing rows as columns and vice-versa
    print("\ttfidfTable Shape: ", tfidfTable.shape)
    tfidfTableDic = tfidfTable.to_dict() #make dictionary

    tfidfTableDicFilt = filterTfidfDictionary(tfidfTableDic, 0.05, "more") #use filter-function
    pathToSave = os.path.join(pathToMemex, "results_tfidf.dataJson") #set individual path for saving
    with open(pathToSave, 'w', encoding='utf8') as f9:
        json.dump(tfidfTableDicFilt, f9, sort_keys=True, indent=4, ensure_ascii=False) #saving

    # PART 3: saving cosine distances
    print("\tsaving cosine distances data...")
    cosineTable = pd.DataFrame(cosineMatrix) #create pandas Dataframe
    print("\tcosineTable Shape: ", cosineTable.shape)
    cosineTable.columns = docIdList #set columns as citekeys
    cosineTable.index = docIdList #set index as citekeys
    cosineTableDic = cosineTable.to_dict() #make dictionary

    tfidfTableDicFilt = filterTfidfDictionary(cosineTableDic, 0.25, "more") #use filter function
    pathToSave = os.path.join(pathToMemex, "results_cosineDist.dataJson") #set individual path for saving
    with open(pathToSave, 'w', encoding='utf8') as f9:
        json.dump(tfidfTableDicFilt, f9, sort_keys=True, indent=4, ensure_ascii=False) #saving

tfidfPublications(settings["path_to_memex"]) #use tfidf function