import re, os, yaml, json, random
from datetime import datetime

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("Memex_config.yml") #load yaml file and process settings with pre-defined functions

###########################################################
# FUNCTIONS ###############################################
###########################################################

def searchOCRresults(pathToMemex, searchString): #function to search Memex for specific keyword(s)
    print("SEARCHING FOR: `%s`" % searchString) #print statement for convenience
    files = functions.dicOfRelevantFiles(pathToMemex, ".json") #use pre-defined function to build a dictionary from all the ocred files
    results = {} #empty dic

    for citationKey, pathToJSON in files.items(): #loop through the ocred files individually by citekey
        data = json.load(open(pathToJSON)) #save path to ocred file
        #print(citationKey)
        count = 0 #count variable

        for pageNumber, pageText in data.items(): #loop through saved ocred files by page and text
            if re.search(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE): #search for the searchstring in the text of the page; \b matches the empty string at the beginning or end of a word
                if citationKey not in results: #create new entry in results dic if not already present
                    results[citationKey] = {}

                # relative path
                a = citationKey.lower() #make citekey lowercase
                relPath = os.path.join(a[:1], a[:2], citationKey, "pages", "%s.html" % pageNumber) #create path to publication's html files 
                countM = len(re.findall(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE)) #count variable for findings on age
                pageWithHighlights = re.sub(r"\b(%s)\b" % searchString, r"<span class='searchResult'>\1</span>", pageText, flags=re.IGNORECASE) #change hmtl to highlight searchword(s)

                results[citationKey][pageNumber] = {}
                results[citationKey][pageNumber]["pathToPage"] = relPath #add path to html page with found search to results dic
                results[citationKey][pageNumber]["matches"] = countM #save count of findings on page
                results[citationKey][pageNumber]["result"] = pageWithHighlights.replace("\n", "<br>") #change html

                count  += 1 #add 1 to first count variable

        if count > 0: #if at least 1 occurrence of the searchword(s) is found
            print("\t", citationKey, " : ", count) #give print statement with citekey + number of total findings in this publication
            newKey = "%09d::::%s" % (count, citationKey) #new variable defined with count and citekey
            results[newKey] = results.pop(citationKey) #replace citekey with the newKey variable

            # add time stamp
            currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #get current timestamp
            results["timestamp"] = currentTime #add time to results dic
            results["searchString"] = searchString # add search string (as submitted)

    saveWith = re.sub("\W+", "", searchString) #replace replace non-word character (1+) with empty string in searchword
    saveTo = os.path.join(pathToMemex, "searches", "%s.searchResults" % saveWith) #create path to folder in which the searches are saved
    with open(saveTo, 'w', encoding='utf8') as f9c:
        json.dump(results, f9c, sort_keys=True, indent=4, ensure_ascii=False) #save sorted search results in new file 

###########################################################
# RUN THE MAIN CODE #######################################
###########################################################

#search word examples
searchPhrase  = r"digital"
#searchPhrase  = r"corpus\W*based"
#searchPhrase  = r"corpus\W*driven"
#searchPhrase  = r"multi\W*verse"
#searchPhrase  = r"text does ?n[o\W]t exist"
#searchPhrase  = r"corpus-?based"

searchOCRresults(settings["path_to_memex"], searchPhrase) #run above-defined function; the function takes two arguments: path to memex + regex for searchphrase
#exec(open("9_Interface_IndexPage.py").read())
