#import functions

import os, yaml, json, random

#pre-defined functions
import functions

###############################
#VARIABLES#
##############################
settingsFile = "Memex_config.yml"
settings = yaml.safe_load(open(settingsFile))
bibKeys = yaml.safe_load(open("zotero_biblatex_keys.yml"))
memexPath = settings["path_to_memex"]
langKeys = yaml.safe_load(open(settings["language_keys"]))

#####################################################################
#FUNCTIONS#
#####################################################################

#function that merges page images+OCR-ed text+ bib info together
#into a HTML-based interface

# generate interface for the publication
def generatePublicationInterface(citeKey, pathToBibFile):
	print("="*80)
	print(citeKey)

######################
#SINGLE PUBLICATION#
######################
	jsonFile = pathToBibFile.replace(".bib", ".json") #get JSON files
	with open(jsonFile) as jsonData:
		ocred = json.load(jsonData) #open file
		pNums = ocred.keys() #get pages of publication

		pageDic = functions.generatePageLinks(pNums) #use pre-defined function
		
		# load page template
		with open(settings["template_page"], "r", encoding="utf8") as ft:
			template = ft.read()

		# load individual bib record
		bibFile = pathToBibFile
		bibDic = functions.loadBib(bibFile) #use pre-defined function
		print(bibDic)
		bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"]) #use pre-defined function

		orderedPages = list(pageDic.keys()) #make list of pages

		authorOrEditor = "[No data]"
		if "editor" in bibDic[citeKey]:
			authorOrEditor = bibDic[citeKey]["editor"]
		if "author" in bibDic[citeKey]:
			authorOrEditor = bibDic[citeKey]["author"]

		date = "unidentified"
		if "year" in bibDic[citeKey]:
			date = bibDic[citeKey]["year"]

		for o in range(0, len(orderedPages)): #loop through pages of individual bib file
			#print(o)
			k = orderedPages[o] #page number
			v = pageDic[orderedPages[o]] #page

			pageTemp = template 
			pageTemp = pageTemp.replace("@PAGELINKS@", v) #replace pattern with page
			pageTemp = pageTemp.replace("@PATHTOFILE@", "") #replace pattern with empty string
			pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey) #replace pattern with publication ID
			wCloud = '\n<img src="../@WCLOUD@" width="100%" alt="wordcloud">'.replace("@WCLOUD@", "%s.jpg" % citeKey)
			pageTemp = pageTemp.replace("@WORD_CLOUD@", wCloud)
			pageTemp = pageTemp.replace("@PUB_AUTHOR@", authorOrEditor)
			pageTemp = pageTemp.replace("@PUB_YEAR@", date)
			pageTemp = pageTemp.replace("@PUB_TITLE@", bibDic[citeKey]["title"].replace("{", "").replace("}", ""))


			if k != "DETAILS": #if not set to overview page
				mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k) #use ocred page as main element
				pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
				pageTemp = pageTemp.replace("@OCREDCONTENT@", ocred[k].replace("\n", "<br>"))
			else:
				mainElement = bibForHTML.replace("\n", "<br> ")
				mainElement = '<div class="bib">%s</div>' % mainElement
				#mainElement += '\n<img src="../@WCLOUD@" width="100%" alt="wordcloud">'.replace("@WCLOUD@", "%s.jpg" % citeKey)
				pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)
				pageTemp = pageTemp.replace("@OCREDCONTENT@", "")

			# @NEXTPAGEHTML@ and @PREVIOUSPAGEHTML@
			#set order of the page layout
			if k == "DETAILS":
				nextPage = "0001.html"
				prevPage = "" #no previous page
			elif k == "0001":
				nextPage = "0002.html"
				prevPage = "DETAILS.html" #set previous page because it is not a serial number
			elif o == len(orderedPages)-1: #take care of special case
				nextPage = ""
				prevPage = orderedPages[o-1] + ".html"
			else:
				nextPage = orderedPages[o+1] + ".html"
				prevPage = orderedPages[o-1] + ".html"

			pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage)
			pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage)

			pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k)
			with open(pagePath, "w", encoding="utf8") as f9: #set path for individual pages
				f9.write(pageTemp)

######################
#START PAGE#
######################

def generateStartPages(pathToMemex):

	#load templates for INDEX page

	with open(settings["template_index"], "r", encoding="utf8") as ti:
		template_i = ti.read()

	with open(settings["content_index"], "r", encoding="utf8") as ci:
		content_i = ci.read()

	pageTemp_i = template_i
	pageTemp_i = pageTemp_i.replace("@MAINCONTENT@", content_i) #use content.html to create index content by replacing the string @MAINCONTENT@ 

	#set path for index page of Memex
	pagePath_i = settings["path_to_index"]
	with open(pagePath_i, "w", encoding="utf8") as f1:
		f1.write(pageTemp_i)

#CONTENT
#hint: <li><a href="@PATHTOPUBL@/pages/DETAILS.html">[@CITEKEY@]</a> @AUTHOR@ (@DATE@) - <i>@TITLE@</i></li>
	
	# load bibliographical data for processing
	publicationDic = {} # key = citationKey; value = recordDic

	for subdir, dirs, files in os.walk(pathToMemex):
		for file in files:
			if file.endswith(".bib"): #look for files with .bib extension in Memex
				pathWhereBibIs = os.path.join(subdir, file) #generate path to bib file
				tempDic = functions.loadBib(pathWhereBibIs) #use pre-defined function
				publicationDic.update(tempDic) #add key:value pairs to dic

# generate data for the main CONTENTS
	singleItemTemplate = '<li><a href="@RELATIVEPATH@/pages/DETAILS.html">[@CITATIONKEY@]</a> @AUTHOROREDITOR@ (@DATE@) - <i>@TITLE@</i></li>'
	contentsList = []

	for citeKey,bibRecord in publicationDic.items():
		relativePath = functions.generatePublPath(pathToMemex, citeKey).replace(pathToMemex, "") #use pre-defined function

		#take care of missing data or unclear data
		authorOrEditor = "[No data]"
		if "editor" in bibRecord:
			authorOrEditor = bibRecord["editor"]
		if "author" in bibRecord:
			authorOrEditor = bibRecord["author"]

		date = "unidentified"
		if "year" in bibRecord:
			date = bibRecord["year"][:4]

		title = bibRecord["title"]

		# forming a record with respective data of single publication
		recordToAdd = singleItemTemplate
		recordToAdd = recordToAdd.replace("@RELATIVEPATH@", relativePath)
		recordToAdd = recordToAdd.replace("@CITATIONKEY@", citeKey)
		recordToAdd = recordToAdd.replace("@AUTHOROREDITOR@", authorOrEditor)
		recordToAdd = recordToAdd.replace("@DATE@", date)
		recordToAdd = recordToAdd.replace("@TITLE@", title)

		recordToAdd = recordToAdd.replace("{", "").replace("}", "")

		contentsList.append(recordToAdd) #add single publication info to content list

	contents = "\n<ul>\n%s\n</ul>" % "\n".join(sorted(contentsList)) #list of all publications
	mainContent = "<h1>CONTENTS of MEMEX</h1>\n\n" + contents #headline

	# save the CONTENTS page
	with open(os.path.join(pathToMemex, "contents.html"), "w", encoding="utf8") as f2:
		f2.write(template_i.replace("@MAINCONTENT@", mainContent))

'''
	pageTemp_c = pageTemp_i.replace("@CITEKEY@", citeKey)
	pageTemp_c = pageTemp_i.replace("@PATHTOPUBL@", detailPage)

	#set path for content page of Memex
	pagePath_c = settings["path_to_content"]
	with open(pagePath_c, "w", encoding="utf8") as f2:
		f2.write(pageTemp_c)
'''
######################
#PROCESS ALL#
######################

def processAllRecords(bibData):
	keys = list(bibData.keys())
	random.shuffle(keys) #to go through records in random order

	for key in keys: #loop through publications
		bibRecord = bibData[key]
		citationKey = bibRecord["rCite"]

		publPath = functions.generatePublPath(memexPath, citationKey)
		pathToBibFile  = os.path.join(publPath, citationKey + ".bib")
		print(pathToBibFile)

		generatePublicationInterface(citationKey, pathToBibFile)

	generateStartPages(memexPath)


bibData = functions.loadBib(settings["bib_all"])
processAllRecords(bibData)