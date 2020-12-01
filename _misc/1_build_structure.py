#import libraries
import yaml
import re
import os
import shutil
##########################################################################

#variable assignments
settingsFile = "Memex_config.yml"
settings = yaml.safe_load(open(settingsFile))
bibKeys = yaml.safe_load(open("zotero_biblatex_keys.yml"))
memexPath = settings["path_to_memex"]

def bibLoad(bibTexFile): #define funtion to load and process bibtex file

    bibDic = {} #create dictionary

    with open(bibTexFile, "r") as f1: #open file and reads in content as one string
        records = f1.read().split("\n@") #splits string into a list using \n@ as delimiter

        for record in records[1:]: 
            #process ONLY those records that have PDFs
            #had to change the search phrase from .pdf to part of pdf path, because in my Bibtex file sometimes the url contained .pdf
            #but there was no actual pdf attached 
            if "/home/lisnux" in record.lower(): #make lowercase

            	completeRecord = "\n@" + record #variable saves each record with delimiter

                record = record.strip().split("\n")[:-1] #drop last element of entry => }

                rType = record[0].split("{")[0].strip() #splits string by { and removes leading/trailing spaces
                rCite = record[0].split("{")[1].strip().replace(",", "") #splits string by {, removes leading/trailing spaces and replaces , 

                bibDic[rCite] = {} #create dictionary 
                bibDic[rCite]["rCite"] = rCite #add elemt to dic
                bibDic[rCite]["rType"] = rType #add elemt to dic
                bibDic[rCite]["complete"] = completeRecord #add elemt to dic
                print(bibDic[rCite])

                for r in record[1:]: # loop through strings in individual record
                    key = r.split("=")[0].strip() # #split r by "="; index position [0] => key and remove leading/trailing spaces
                    val = r.split("=")[1].strip() # #split r by "="; index position [1] => value and remove leading/trailing spaces
                    val = re.sub("^\{|\},?", "", val) #replace curly brackets 0 or 1 times

                    fixedKey = bibKeys[key] #assign variable (list of keys predefined in yml file)

                    bibDic[rCite][fixedKey] = val #add element to dic

                     # fix the path to PDF

                    #problem with exporting Bibtex e.g.:
                    #file = Grant_2019_Data visualization.pdf:/home/lisnux/Zotero/storage/EHS8IGYU/Grant_2019_Data visualization.pdf

                    if key == "file": #navigate to file key
                    	val = re.findall("(?<=:).+", val) #matches all instances of pdf path in value
                    	val = ''.join([str(elem) for elem in val]) #change list to string (necessary for input to pdfFileSRC)
                    	bibDic[rCite][key] = val #add element to dic
					
    return(bibDic)


#execute function to read in bibtex file and process it
bibData = bibLoad(settings["bib_all"])
print(bibData)

#generate path

def generatePublPath(pathToMemex, bibTexCode):
	temp = bibTexCode.lower() #make lowercase
	directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode) #make directories with predefined path to memex and the first two chars of rCite element
	return(directory)

#process unique bib records
def processBibRecord(pathToMemex, bibRecDict):
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"]) #assign variable tempPath

    print("="*80) #print output
    print("%s :: %s" % (bibRecDict["rCite"], tempPath)) #print output of individual records + generated path
    print("="*80)

    if not os.path.exists(tempPath): #make directory if it doesn't already exists
        os.makedirs(tempPath)

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"]) #path for bib file in folder
        with open(bibFilePath, "w") as f9:
            f9.write(bibRecDict["complete"]) #citationkey

        pdfFileSRC = bibRecDict["file"] #assign source path variable

        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"]) #path for pdf file in folder
        if not os.path.isfile(pdfFileDST): # this is to avoid copying that char-folders already in existence
            shutil.copyfile(pdfFileSRC, pdfFileDST) #copy pdf from source folder to new memex folder

#process all bib records
def processAllRecords(bibData): 
    for k,v in bibData.items():
        processBibRecord(memexPath, v)

#execute function to create folders and save pdfs
processAllRecords(bibData)

print("Done!")
