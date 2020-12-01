#import libraries

import pdf2image
import pytesseract
import PyPDF2


#import pre-used functions
import functions

#test
pathToMemex = "/home/lisnux/Desktop/UniWien/WS2021/070172_UEMethodologicalCourse/hw070172/MEMEX_SANDBOX/data"
citationKey = "abbott_venice_nodate"

publPath = functions.generatePublPath(pathToMemex, citationKey)
print(publPath)

### define new functions for OCR

#clean PDF
def removeCommentsFromPDF(pathToPdf):
	with open(pathToPdf, 'rb') as pdf_obj: #open pdf path
		pdf = PyPDF2.PdfFileReader(pdf_obj) #use built-in funcions of PyPDF2
		out = PyPDF2.PdfFileWriter()
		...

#OCR PDF 

def ocrPublication(pathToMemex, citationKey, language):
	publPath = functions.generatePublPath(pathToMemex, citationKey)
	pdfFile = os.path.join(publPath, citationKey + ".pdf")
	jsonFile = os.path.join(publPath, citationKey + ".json")
	...

