#import functions

import os, yaml, json, random, unicodedata

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

###########################################################
# MINI TEMPLATES ##########################################
###########################################################

connectionsTemplate = """
<button class="collapsible">Similar Texts (<i>tf-idf</i> + cosine similarity)</button>
  <div class="content">
	Note: 
	<br>
	<b>Sim*</b>: <i>cosine similarity</i>; 1 is a complete match, 0 — nothing similar;
	cosine similarity is calculated using <i>tf-idf</i> values of top keywords.
	<br>
  </div>
<table id="publications" class="mainList">
<thead>
	<tr>
		<th>link</th>
		<th>Sim*</th>
		<th>Author(s), Year, Title, Pages</th>
	</tr>
</thead>
<tbody>
@CONNECTEDTEXTSTEMP@
</tbody>
</table>
"""

ocrTemplate = """
<button class="collapsible">OCREDTEXT</button>
<div class="content">
  <div class="bib">
  @OCREDCONTENTTEMP@
  </div>
</div>
"""

generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">
@ELEMENTCONTENT@
</div>
"""

###########################################################
# MINI FUNCTIONS ##########################################
###########################################################

import math
# a function for grouping pages into clusters of y number of pages
# x = number to round up; y = a multiple of the round-up-to number
def roundUp(x, y):
	result = int(math.ceil(x / y)) * y
	return(result)

# formats individual references to publications
def generateDoclLink(bibTexCode, pageVal, distance):
	print(bibTexCode)
	pathToPubl = functions.generatePublPath(settings["path_to_memex"], bibTexCode)
	bib = functions.loadBib(os.path.join(pathToPubl, "%s.bib" % bibTexCode))
	bib = bib[bibTexCode]

	author = "N.d."
	if "editor" in bib:
		author = bib["editor"]
	if "author" in bib:
		author = bib["author"]

	date = "nodate"
	if "year" in bib:
		date = bib["year"][:4]

	reference = "%s (%s). <i>%s</i>" % (author, date, bib["title"])
	search = unicodedata.normalize('NFKD', reference).encode('ascii','ignore')
	search = " <div class='hidden'>%s</div>" % search

	if pageVal == 0: # link to the start of the publication
		htmlLink = os.path.join(pathToPubl.replace(settings["path_to_memex"], "../../../../"), "pages", "DETAILS.html")
		htmlLink = "<a href='%s'><i>read</i></a>" % (htmlLink)
		page = ""
		startPage = 0
	else:
		startPage = pageVal - 5
		endPage   = pageVal
		if startPage == 0:
			startPage += 1
		htmlLink = os.path.join(pathToPubl.replace(settings["path_to_memex"], "../../../../"), "pages", "%04d.html" % startPage)
		htmlLink = "<a href='%s'><i>read</i></a>" % (htmlLink)
		page = ", pdfPp. %d-%d</i></a>" % (startPage, endPage)

	publicationInfo = reference + page + search
	publicationInfo = publicationInfo.replace("{", "").replace("}", "")
	singleItemTemplate = '<tr><td>%s</td><td>%f</td><td data-order="%s%05d">%s</td></tr>' % (htmlLink, distance, bibTexCode, startPage, publicationInfo)

	return(singleItemTemplate)

def generateReferenceSimple(bibTexCode):
	pathToPubl = functions.generatePublPath(settings["path_to_memex"], bibTexCode)
	bib = functions.loadBib(os.path.join(pathToPubl, "%s.bib" % bibTexCode))
	bib = bib[bibTexCode]

	author = "N.d."
	if "editor" in bib:
		author = bib["editor"]
	if "author" in bib:
		author = bib["author"]

	date = "nodate"
	if "year" in bib:
		date = bib["year"][:4]

	reference = "%s (%s). <i>%s</i>" % (author, date, bib["title"])
	reference = reference.replace("{", "").replace("}", "")
	return(reference)

# convert json dictionary of connections into HTML format
def formatDistConnections(pathToMemex, distanceFile):
	print("Formatting distances data from `%s`..." % distanceFile)
	distanceFile = os.path.join(pathToMemex, distanceFile)
	distanceDict = json.load(open(distanceFile))

	formattedHTML = {}

	for doc1, doc1Dic in distanceDict.items():
		formattedHTML[doc1] = []

		for doc2, distance in doc1Dic.items():
			doc2 = doc2.split("__")
			if len(doc2) == 1:
				tempVar = generateDoclLink(doc2[0], 0, distance)
			else:
				tempVar = generateDoclLink(doc2[0], int(doc2[1]), distance)

			formattedHTML[doc1].append(tempVar)
			#input(formattedHTML)
	print("\tdone!")
	return(formattedHTML)

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

publConnData = formatDistConnections(settings["path_to_memex"], settings["publ_cosDist"])

pageConnData = formatDistConnections(settings["path_to_memex"], settings["page_cosDist"])
#print("pageConnData ...")
#print(pageConnData)

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
		bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"]) #use pre-defined function

		orderedPages = list(pageDic.keys()) #make list of pages

		authorOrEditor = "[No data]"
		if "editor" in bibDic[citeKey]:
			authorOrEditor = bibDic[citeKey]["editor"]
		if "author" in bibDic[citeKey]:
			authorOrEditor = bibDic[citeKey]["author"]

		date = "nodate"
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

			emptyResults = '<tr><td><i>%s</i></td><td><i>%s</i></td><td><i>%s</i></td></tr>'


			if k != "DETAILS": #if not set to overview page
				mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k) #use ocred page as main element

				pageKey = citeKey+"__%04d" % roundUp(int(k), 4)
				#print("pagekey: ", pageKey)
				if pageKey in pageConnData:
					print("pagekey found: ", pageKey)
					formattedResults = "\n".join(pageConnData[pageKey])
					print(formattedResults)
				else:
					formattedResults = emptyResults % ("no data", "no data", "no data")

				mainElement += connectionsTemplate.replace("@CONNECTEDTEXTSTEMP@", formattedResults)
				mainElement += ocrTemplate.replace("@OCREDCONTENTTEMP@", ocred[k].replace("\n", "<br>"))
				pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)

			else:
				#reference = generateReferenceSimple(citeKey)
				reference = "OVERVIEW"
				mainElement = "<h4><font color=#8baad1><center>%s</center></font></h4>\n\n" % reference

				bibElement = '<div class="bib">%s</div>' % bibForHTML.replace("\n", "<br> ")
				bibElement = generalTemplate.replace("@ELEMENTCONTENT@", bibElement)
				bibElement = bibElement.replace("@ELEMENTHEADER@", "BibTeX Bibliographical Record")
				mainElement += bibElement + "\n\n"

				wordCloud = '\n<img src="../' + citeKey + '.jpg" width="100%" alt="wordcloud">'
				wordCloud = generalTemplate.replace("@ELEMENTCONTENT@", wordCloud)
				wordCloud = wordCloud.replace("@ELEMENTHEADER@", "WordCloud of Keywords (<i>tf-idf</i>)")
				mainElement += wordCloud + "\n\n"
				
				if citeKey in publConnData:
					formattedResults = "\n".join(publConnData[citeKey])
					#input(formattedResults)
				else:
					formattedResults = emptyResults % ("no data", "no data", "no data")

				mainElement += connectionsTemplate.replace("@CONNECTEDTEXTSTEMP@", formattedResults)


				pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement)

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

		date = "nodate"
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
exec(open("6_IndexPage.py").read())
