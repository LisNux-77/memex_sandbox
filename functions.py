import os, re, shutil

###########################################################
# FUNCTIONS ###############################################
###########################################################

# load bibTex Data into a dictionary
def loadBib(bibTexFile):

    bibDic = {}
    recordsNeedFixing = []

    with open(bibTexFile, "r", encoding="utf8") as f1:
        records = f1.read().split("\n@")

        for record in records[1:]:
            #process ONLY those records that have PDFs (special case)

            #had to change the search phrase from .pdf to part of pdf path, because in my Bibtex file sometimes the url contained .pdf
            #but there was no actual pdf attached 
            if "/home/lisnux" in record.lower():
                completeRecord = "\n@" + record

                record = record.strip().split("\n")[:-1]

                rType = record[0].split("{")[0].strip()
                rCite = record[0].split("{")[1].strip().replace(",", "")

                bibDic[rCite] = {}
                bibDic[rCite]["rCite"] = rCite
                bibDic[rCite]["rType"] = rType
                bibDic[rCite]["complete"] = completeRecord

                for r in record[1:]:
                    key = r.split("=")[0].strip()
                    val = r.split("=")[1].strip()
                    val = re.sub("^\{|\},?", "", val)

                    bibDic[rCite][key] = val

                    # fix the path to PDF (special case)

                    #problem with exporting Bibtex e.g.:
                    #file = Grant_2019_Data visualization.pdf:/home/lisnux/Zotero/storage/EHS8IGYU/Grant_2019_Data visualization.pdf

                    if key == "file": #navigate to file key
                    	val = re.findall("(?<=:).+", val) #matches all instances of pdf path in value
                    	val = ''.join([str(elem) for elem in val]) #change list to string (necessary for input to pdfFileSRC)
                    	bibDic[rCite][key] = val #add element to dic

    print("="*80)
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic))
    print("="*80)
    return(bibDic)

# generate path from bibtex citation key; for example, if the key is `SavantMuslims2017`,
# the path will be pathToMemex+`/s/sa/SavantMuslims2017/`
def generatePublPath(pathToMemex, bibTexCode):
    temp = bibTexCode.lower()
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode)
    return(directory)

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file 
def processBibRecord(pathToMemex, bibRecDict):
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"])

    print("="*80)
    print("%s :: %s" % (bibRecDict["rCite"], tempPath))
    print("="*80)

    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"])
        with open(bibFilePath, "w", encoding="utf8") as f9:
            f9.write(bibRecDict["complete"])

        pdfFileSRC = bibRecDict["file"]
        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"])
        if not os.path.isfile(pdfFileDST): # this is to avoid copying that had been already copied.
            shutil.copyfile(pdfFileSRC, pdfFileDST)

# creates a dictionary of citationKey:Path pairs for a relevant type of files
def dicOfRelevantFiles(pathToMemex, extension):
    dic = {}
    for subdir, dirs, files in os.walk(pathToMemex):
        for file in files:
            # process publication tf data
            if file.endswith(extension):
                key = file.replace(extension, "")
                value = os.path.join(subdir, file)
                dic[key] = value
    return(dic)
