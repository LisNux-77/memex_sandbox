#import libraries

import pdf2image
import pytesseract
import PyPDF2

import os, yaml, json, random

#import pre-defined functions
import functions

###############################
#VARIABLES#
##############################
settingsFile = "Memex_config.yml"
settings = yaml.safe_load(open(settingsFile))
bibKeys = yaml.safe_load(open("zotero_biblatex_keys.yml"))
memexPath = settings["path_to_memex"]
langKeys = yaml.safe_load(open(settings["language_keys"]))

#############################

#test
#pathToMemex = "/home/lisnux/Desktop/UniWien/WS2021/070172_UEMethodologicalCourse/hw070172/MEMEX_SANDBOX/data"
#citationKey = "noack_modularity_2009"

#############################
#FUNCTIONS#
#############################

### define new functions for OCR

#clean PDF
#def removeCommentsFromPDF(pathToPdf):
#	with open(pathToPdf, 'rb') as pdf_obj: #open pdf path
#		pdf = PyPDF2.PdfFileReader(pdf_obj) #use built-in funcions of PyPDF2
#		out = PyPDF2.PdfFileWriter()
#		...

##############################################

def ocrPublication(pathToMemex, citationKey, language):
    publPath = functions.generatePublPath(pathToMemex, citationKey)
    pdfFile  = os.path.join(publPath, citationKey + ".pdf")
    jsonFile = os.path.join(publPath, citationKey + ".json")
    saveToPath = os.path.join(publPath, "pages")

    if not os.path.isfile(jsonFile):
        if not os.path.exists(saveToPath):
            os.makedirs(saveToPath)
        
        print("\t>>> OCR-ing: %s" % citationKey)

        textResults = {}
        images = pdf2image.convert_from_path(pdfFile)
        pageTotal = len(images)
        pageCount = 1
        for image in images:
            text = pytesseract.image_to_string(image, lang=language)
            textResults["%04d" % pageCount] = text

            image = image.convert('1') # binarizes image, reducing its size
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount)
            image.save(finalPath, optimize=True, quality=10)

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal))
            pageCount += 1

        with open(jsonFile, 'w', encoding='utf8') as f9:
            json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)
    
    else:
        print("\t>>> %s has already been OCR-ed..." % citationKey)

def identifyLanguage(bibRecDict, fallBackLanguage):
    if "language" in bibRecDict:
        try:
            language = langKeys[bibRecDict["language"]]
            message = "\t>> Language has been successfuly identified: %s" % language
        except:
            message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["language"]
            message += "\t>> For now, trying `%s`..." % fallBackLanguage
            language = fallBackLanguage
    else:
        message = "\t>> No data on the language of the publication"
        message += "\t>> For now, trying `%s`..." % fallBackLanguage
        language = fallBackLanguage
    print(message)
    return(language)

def processAllRecords(bibData):
    keys = list(bibData.keys())
    random.shuffle(keys)

    for key in keys:
        bibRecord = bibData[key]

        functions.processBibRecord(memexPath, bibRecord)

        language = identifyLanguage(bibRecord, "eng")
        ocrPublication(memexPath, bibRecord["rCite"], language)


bibData = functions.loadBib(settings["bib_all"])
processAllRecords(bibData)

