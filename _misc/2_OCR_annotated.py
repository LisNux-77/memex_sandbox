# NEW LIBRARIES
import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs

import os, yaml, json, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "settings.yml" 
settings = yaml.load(open(settingsFile))

memexPath = settings["path_to_memex"] # set path 
langKeys = yaml.load(open(settings["language_keys"])) #define languages of documents

###########################################################
# TRICKY FUNCTIONS ########################################
###########################################################

# the function creates a temporary copy of a PDF file
# with comments and highlights removed from it; it creates
# a clean copy of a PDF suitable for OCR-nig 
def removeCommentsFromPDF(pathToPdf): #define function, 1 parameter
    with open(pathToPdf, 'rb') as pdf_obj: #open individual pdf path
        pdf = PyPDF2.PdfFileReader(pdf_obj) #use built-in funcions of PyPDF2
        out = PyPDF2.PdfFileWriter()
        for page in pdf.pages: #process single pages of pdf
            out.addPage(page)
            out.removeLinks()
        tempPDF = pathToPdf.replace(".pdf", "_TEMP.pdf") #save new pdf with affix _TEMP
        with open(tempPDF, 'wb') as f:  #open new pdf
            out.write(f)
    return(tempPDF) # return new pdf

# function OCR a PDF, saving each page as an image and
# saving OCR results into a JSON file
def ocrPublication(pathToMemex, citationKey, language): # define function, 3 parameters
    # generate and create necessary paths
    publPath = functions.generatePublPath(pathToMemex, citationKey) #pre-defined function in functions.py
    pdfFile  = os.path.join(publPath, citationKey + ".pdf") 
    jsonFile = os.path.join(publPath, citationKey + ".json") # OCR results will be saved here
    saveToPath = os.path.join(publPath, "pages") # we will save processed images here

    # generate CLEAN pdf (necessary if you added highlights and comments to your PDFs)
    pdfFileTemp = removeCommentsFromPDF(pdfFile)

    # first we need to check whether this publication has been already processed
    if not os.path.isfile(jsonFile):
        # let's make sure that saveToPath also exists
        if not os.path.exists(saveToPath):
            os.makedirs(saveToPath) #create new diretory when if not == True
        
        # start process images and extract text
        print("\t>>> OCR-ing: %s" % citationKey) #print statement to check status of program

        textResults = {} #create empty dictionary
        images = pdf2image.convert_from_path(pdfFileTemp) #built-in function
        pageTotal = len(images) #sum of pages of pdf
        pageCount = 1 #set page counter to 1
        for image in images: #start looping through every image
            image = image.convert('1') # binarizes image, reducing its size
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount) #saving image with page number in filename
            image.save(finalPath, optimize=True, quality=10)

            text = pytesseract.image_to_string(image, lang=language) #built-in function processing image to get text (language input necessary!)
            textResults["%04d" % pageCount] = text #save result under new variable textResults

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal)) #print statement to show how many pages have been processed
            pageCount += 1 #increase page counter by 1 

        with open(jsonFile, 'w', encoding='utf8') as f9: #open new json file
            json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False) #converts python object into json object
    
    else: # in case JSON file already exists
        print("\t>>> %s has already been OCR-ed..." % citationKey)

    os.remove(pdfFileTemp) #delete temporary file path

def identifyLanguage(bibRecDict, fallBackLanguage): #define function, 2 parameters
    if "langid" in bibRecDict: #search for "langid" in bib record
        try:
            language = langKeys[bibRecDict["langid"]]
            message = "\t>> Language has been successfuly identified: %s" % language #print message if language of pdf is saved in bib record
        except:
            message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["langid"]
            message += "\t>> For now, trying `%s`..." % fallBackLanguage #if language is not well defined in bib record, determine a default language
            language = fallBackLanguage
    else:
        message = "\t>> No data on the language of the publication" #if no language is defined in bib record, determine a default language
        message += "\t>> For now, trying `%s`..." % fallBackLanguage
        language = fallBackLanguage
    print(message)
    return(language) #return value => either found language or default

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

#ocrPublication("AbdurasulovMaking2020", "eng")

###########################################################
# PROCESS ALL RECORDS: APPROACH 1 #########################
###########################################################

"""
def processAllRecords(bibData):
    for k,v in bibData.items():
        # 1. create folders, copy files
        functions.processBibRecord(memexPath, v)
        # 2. OCR the file
        language = identifyLanguage(v, "eng")
        ocrPublication(memexPath, v["rCite"], language)
bibData = functions.loadBib(settings["bib_all"])
processAllRecords(bibData)
"""

###########################################################
# PROCESS ALL RECORDS: APPROACH 2 #########################
###########################################################

# Why this way? Our computers are now quite powerful; they
# often have multiple cores and we can take advantage of this;
# if we process our data in the manner coded below --- we shuffle
# our publications and process them in random order --- we can
# run multiple instances fo the same script and data will
# be produced in parallel. You can run as many instances as
# your machine allows (you need to check how many cores
# your machine has). Even running two scripts will cut
# processing time roughly in half.

def processAllRecords(bibData): #define function, 1 parameter
    keys = list(bibData.keys()) # define variable bib keys
    random.shuffle(keys) #allows multiprocessing; every time the function is executed it starts with a different pdf

    for key in keys: #loop through every individual bib key
        bibRecord = bibData[key] #store inormation in new variable

        # 1. create folders, copy files
        functions.processBibRecord(memexPath, bibRecord) #pre-defined function in functions.py

        # 2. OCR the file
        language = identifyLanguage(bibRecord, "eng") #use pre-defined function to determine pdf's language
        ocrPublication(memexPath, bibRecord["rCite"], language) #use pre-defined function to extract text from images


bibData = functions.loadBib(settings["bib_all"]) #pre-defined function in fucntions.py loading bibliography data
processAllRecords(bibData) #use pre-defined function to produce and store text images of all pdfs in the bibliography
