#import functions

import os, yaml, json, re

#pre-defined functions
import functions

#################################################
#set variables

settingsFile = "Memex_config.yml"
settings = yaml.safe_load(open(settingsFile))
pathToMemex = settings["path_to_memex"]

#general template
generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">

@ELEMENTCONTENT@

</div>
"""

#searches template
searchesTemplate = """
<button class="collapsible">SAVED SEARCHES</button>
<div class="content">
<table id="" class="display" width="100%">
<thead>
    <tr>
        <th><i>link</i></th>
        <th>search string</th>
        <th># of publications with matches</th>
        <th>time stamp</th>
    </tr>
</thead>

<tbody>
@TABLECONTENTS@
</tbody>

</table>
</div>
"""

# generate search pages and TOC
def formatSearches(pathToMemex):
    with open(settings["template_search"], "r") as f1:
        indexTmpl = f1.read()
    dof = functions.dicOfRelevantFiles(pathToMemex, ".searchResults")
    print(dof)

    toc = []
    for file, pathToFile in dof.items():
        searchResults = []
        data = json.load(open(pathToFile))
        
        # collect toc
        template = "<tr> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td></tr>"

        linkToSearch = os.path.join("searches", file+".html")
        pathToPage = '<a href="%s"><i>read</i></a>' % linkToSearch
        searchString = '<div class="searchString">%s</div>' % data.pop("searchString")
        timeStamp = data.pop("timestamp")
        tocItem = template % (pathToPage, searchString, len(data), timeStamp)
        toc.append(tocItem)

        # generate the results page
        keys = sorted(data.keys(), reverse=True)
        for k in keys:
            searchResSingle = []
            results = data[k]
            temp = k.split("::::")
            header = "%s (pages with results: %d)" % (temp[1], int(temp[0]))
            for page, excerpt in results.items():
                pdfPage = int(page)
                linkToPage = '<a href="../%s"><i>go to the original page...</i></a>' % excerpt["pathToPage"]
                searchResSingle.append("<li><b><hr>(pdfPage: %d)</b><hr> %s <hr> %s </li>" % (pdfPage, excerpt["result"], linkToPage))
            searchResSingle = "<ul>\n%s\n</ul>" % "\n".join(searchResSingle)
            searchResSingle = generalTemplate.replace("@ELEMENTHEADER@", header).replace("@ELEMENTCONTENT@", searchResSingle)
            searchResults.append(searchResSingle)
        
        searchResults = "<h2>SEARCH RESULTS FOR: <i>%s</i></h2>\n\n" % searchString + "\n\n".join(searchResults)
        with open(pathToFile.replace(".searchResults", ".html"), "w") as f9:
            f9.write(indexTmpl.replace("@MAINCONTENT@", searchResults))

    toc = searchesTemplate.replace("@TABLECONTENTS@", "\n".join(toc))
    print(toc)
    return(toc)

	
def newIndexPage(searches):
	with open(settings["template_index"], "r", encoding="utf8") as ti:
		template_i = ti.read()

	with open(settings["content_index"], "r", encoding="utf8") as ci:
		content_i = ci.read()

	pageTemp_i = template_i
	pageTemp_i = pageTemp_i.replace("@MAINCONTENT@", content_i)
	pageTemp_i = pageTemp_i.replace("@SEARCHRESULTS@", searches)

	#set path for index page of Memex
	pagePath_i = settings["path_to_index"]
	with open(pagePath_i, "w", encoding="utf8") as f1:
		f1.write(pageTemp_i)


searches = formatSearches(pathToMemex)
newIndexPage(searches)


