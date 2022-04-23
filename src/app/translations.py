from openpyxl import load_workbook, Workbook
import sys
import json

texts = {
    "en": {
        "1": "Nature",
        "2": "Human Being",
        "3": "Society and Culture",
        "4": "Religion",
        "5": "Myths and Legends",
        "6": "History and Geography",
        "7": "Literary Works",
        "search": "Search",
        "help": "Help",
        "yourplists": "Your Personal Lists",
        "feedback": "Feedback",
        "typeheretostartsearch": "Type here to start searching",
        "changelang": "\u8bed\u8a00\u5207\u6362",
        "browse": "Browse",
        "termsused": "Terms Used:",
        "collection": "Collection",
        "resultsfound": "results found",
        "citableurl": "Citable URL",
        "clearsearch": "Clear Search",
        "searchresults": "Search Results",
        "saveditems": "Save",
        "imageurl": "Image URL",
        "originalsource": "Original Source",
        "insearchresults": "In Search Results",
        "nonotationsassign": "No notations have been assigned to this item yet. If you want, you can assign your own Iconclass notations.",
        "addcomment": "Add Comment",
        "metadata": "Metadata",
        "persistenturl": "Persistent URL",
        "allitems": "All Items",
        "addiconclass": "Add ICONCLASS",
        "null": "Alas, no example images found for",
        "about": "About",
        "contact": "Contact",
        "team": "Team",
        "howtouse": "How to Use",
        "sortedobjectid": "Sorted on Object ID",
        "sortedcollection": "Sorted by Collection",
        "sortedrandomly": "Sorted Randomly",
        "whatyousearchedfor": "This is what you searched for:",
        "filter_onhold": "- On Hold -",
        "filter_musthave": "Must have",
        "filter_include": "Include",
        "filter_exclude": "Exclude",
        "update_results_notice": "Note: These search results are for a different set of filters. Press the search button again if you want to search with the currently selected filters.",
        "firstofpleaserefine": "First 300 of ... items, please try to refine your search",
        "usefor": "Use for",
        "en_displayterm": "English Display Term",
        "relatedterm": "Related Term",
        "term": "Term",
        "homepage_text1": "The CIT brings together sinology, art history and information studies to create the first thesaurus of Chinese iconography.",
        "homepage_text2": "Traditionally considered a methodology rooted in European art history, iconography has been historically employed to index and access images related to Euro-American art. Because of the lack of alternative models for documenting non-western artefacts, Chinese art objects housed in European and North American collections have often been catalogued according to Eurocentric classifications. The CIT presents a unique opportunity to create an alternative classification scheme rooted in the specificity of Chinese visual culture and foster systematic comparison between Chinese and European art.",
        "homepage_text3": "Browse and Search the CIT Terms",
        "homepage_text4": "The classification system is a hierarchical system, with the following main categories:",
        "homepage_text5": "Browse and Search the CIT Image Archive",
        "homepage_text6": "CIT aims to create an indexing standard that facilitates access and inter-operability of Chinese digital images across collections. The archive contains images that illustrate the application of the CIT terms, and the images have links to the originating collections. The archive uploads regularly more collections and images.",
        "homepage_chord_diagram_title": "A Chord Diagram of the CIT Related Terms",
        "homepage_chord_diagram_text": "This chord diagram reveals otherwise the hidden pattern of symbolic relationships among related terms in the CIT hierarchy. The word colours represent top-level seven categories (Nature, etc.), and the wavy lines connect related terms. Mousing over a term will highlight the line(s) in blue and show a text box displaying the term and its related terms.",
        "lightbox": "Lightbox",
    },
    "zh_hant": {
        "1": "\u81ea\u7136\u754c",
        "2": " \u4eba\u985e",
        "3": " \u793e\u6703\u8207\u6587\u5316",
        "4": " \u5b97\u6559",
        "5": " \u795e\u8a71\u8207\u50b3\u8aaa",
        "6": " \u6b77\u53f2\u8207\u5730\u7406",
        "7": " \u6587\u5b78\u4f5c\u54c1",
        "search": "\u6aa2\u7d22",
        "help": "\u5e6b\u52a9",
        "yourplists": "\u6211\u7684\u5217\u8868",
        "feedback": "\u53cd\u994b",
        "typeheretostartsearch": "\u8f38\u5165\u95dc\u9375\u8a5e",
        "changelang": "Change Language",
        "browse": "\u700f\u89bd",
        "termsused": "\u6a19\u5f15\u8a5e",
        "collection": "\u6536\u85cf\u6a5f\u69cb",
        "resultsfound": "\u6aa2\u7d22\u7d50\u679c",
        "citableurl": "\u53c3\u8003\u93c8\u63a5",
        "clearsearch": "\u6e05\u7a7a\u7d50\u679c",
        "searchresults": "\u6aa2\u7d22\u7d50\u679c",
        "saveditems": "\u4fdd\u5b58",
        "imageurl": "\u5716\u7247\u93c8\u63a5",
        "originalsource": "\u539f\u59cb\u51fa\u8655",
        "insearchresults": "\u55ae\u4ef6\u95b1\u89bd",
        "nonotationsassign": "\u6b64\u4ef6\u5c1a\u672a\u88ab\u6a19\u5f15\uff0c\u8acb\u4f7f\u7528ICONCLASS\u4ee3\u78bc\u6a19\u5f15",
        "addcomment": "\u8a55\u8ad6",
        "metadata": "\u5143\u6578\u64da",
        "persistenturl": "\u6c38\u4e45\u93c8\u63a5",
        "allitems": "\u5168\u90e8\u85cf\u54c1",
        "addiconclass": "\u52a0\u5165ICONCLASS\u6a19\u5f15",
        "null": "\u62b1\u6b49\uff0c\u8a72\u8a5e\u66ab\u7121\u5716\u50cf",
        "about": "\u95dc\u65bc",
        "contact": "\u806f\u7d61",
        "team": "\u5718\u968a",
        "howtouse": "\u5982\u4f55\u4f7f\u7528",
        "sortedobjectid": "\u4ee5\u85cf\u54c1\u7de8\u865f\u6392\u5e8f",
        "sortedcollection": "\u4ee5\u6536\u85cf\u6a5f\u69cb\u6392\u5e8f",
        "sortedrandomly": "\u4ee5\u96a8\u6a5f\u65b9\u5f0f\u6392\u5e8f",
        "whatyousearchedfor": "\u6aa2\u7d22\u5167\u5bb9",
        "filter_onhold": "\u4fdd\u7559",
        "filter_musthave": "\u5fc5\u542b",
        "filter_include": "\u5305\u62ec",
        "filter_exclude": "\u9664\u53bb",
        "update_results_notice": "\u6ce8\u610f\uff1a\u9019\u4e9b\u6aa2\u7d22\u7d50\u679c\u662f\u51fa\u81ea\u65bc\u4e0d\u540c\u7684\u7be9\u9078\u7d44\u5408\u3002\u5982\u679c\u8981\u4f7f\u7528\u7576\u524d\u9078\u5b9a\u7684\u7be9\u9078\u689d\u4ef6\u9032\u884c\u6aa2\u7d22\u7684\u8a71\uff0c\u8acb\u518d\u6b21\u9ede\u9078\u6aa2\u7d22\u6309\u9215\u3002",
        "firstofpleaserefine": "300\u500b\u9805\u76ee\u4e2d\u7684\u524d...\u500b\uff0c\u8acb\u5617\u8a66\u512a\u5316\u6aa2\u7d22",
        "usefor": "\u7fa9\u985e\u8a5e",
        "en_displayterm": "\u82f1\u6587\u986f\u793a\u8a5e",
        "relatedterm": "\u95dc\u806f\u8a5e",
        "term": "\u8a5e\u5f59",
        "homepage_text1": "\u4e2d\u570b\u5716\u50cf\u8a8c\u7d22\u5f15\u5178\uff08\u4e2d\u5716\u5178\uff09\u65e8\u5728\u532f\u96c6\u6f22\u5b78\u3001\u85dd\u8853\u53f2\u548c\u4fe1\u606f\u7814\u7a76\uff0c\u5efa\u69cb\u4e00\u90e8\u4e2d\u570b\u5716\u50cf\u8a8c\u5206\u985e\u8a5e\u5178\u3002",
        "homepage_text2": "\u5716\u50cf\u8a8c\u662f\u4e00\u7a2e\u690d\u6839\u65bc\u6b50\u6d32\u85dd\u8853\u53f2\u7684\u7814\u7a76\u65b9\u6cd5\uff0c\u6b77\u4f86\u88ab\u7528\u4f86\u7d00\u9304\u548c\u6aa2\u7d22\u6b50\u7f8e\u85dd\u8853\u5716\u50cf\u3002\u7531\u65bc\u7f3a\u4e4f\u975e\u897f\u65b9\u85dd\u8853\u5716\u50cf\u7684\u7d00\u9304\u6a21\u578b\uff0c\u6b50\u6d32\u53ca\u5317\u7f8e\u6536\u85cf\u6a5f\u69cb\u4e2d\u7684\u4e2d\u570b\u85dd\u8853\u54c1\u901a\u5e38\u4ee5\u897f\u65b9\u70ba\u4e2d\u5fc3\u7684\u5206\u985e\u9ad4\u7cfb\u9032\u884c\u7de8\u76ee\u3002 CIT\u63d0\u4f9b\u4e86\u4e00\u500b\u7368\u7279\u7684\u6a5f\u6703\uff0c\u6839\u64da\u4e2d\u570b\u50b3\u7d71\u8996\u89ba\u6587\u5316\u7684\u7279\u6027, \u5275\u5efa\u4e00\u7a2e\u66ff\u4ee3\u5206\u985e\u65b9\u6848\uff0c\u4e26\u4f7f\u4e2d\u6b50\u85dd\u8853\u7cfb\u7d71\u6bd4\u8f03\u6210\u70ba\u53ef\u80fd\u3002",
        "homepage_text3": "\u700f\u89bd\u4e26\u6aa2\u7d22\u4e2d\u5716\u5178\u8a5e\u532f",
        "homepage_text4": "\u4e00\u500b\u5177\u6709\u5c64\u7d1a\u95dc\u4fc2\u7684\u5206\u985e\u7cfb\u7d71, \u5206\u70ba\u4ee5\u4e0b\u5927\u985e\uff1a",
        "homepage_text5": "\u641c\u7d22\u4e2d\u5716\u5178\u5716\u50cf\u6a94\u6848\u5eab",
        "homepage_text6": "\u4e2d\u5716\u5178\u65e8\u5728\u5275\u5efa\u4e00\u7a2e\u7d22\u5f15\u6a19\u6e96\uff0c\u4ee5\u4fc3\u9032\u4e2d\u570b\u6578\u5b57\u5716\u50cf\u8de8\u6a5f\u69cb\u85cf\u54c1\u6aa2\u7d22\u3002\u6a94\u6848\u5eab\u6240\u6536\u9304\u7684\u5716\u50cf\u7528\u4ee5\u5c55\u793a\u4e2d\u5716\u5178\u8853\u8a9e\u7684\u5177\u9ad4\u61c9\u7528\u3002\u6bcf\u5e45\u5716\u50cf\u5747\u8207\u85cf\u54c1\u6a5f\u69cb\u539f\u59cb\u6578\u64da\u5eab\u7db2\u7ad9\u93c8\u63a5\u3002\u6a94\u6848\u5eab\u5b9a\u671f\u589e\u52a0\u66f4\u591a\u6536\u85cf\u54c1\u6a5f\u69cb\u53ca\u85cf\u54c1\u3002",
        "homepage_chord_diagram_title": "\u4e2d\u5716\u5178\u95dc\u806f\u8a5e\u548c\u5f26\u5716",
        "homepage_chord_diagram_text": "\u6b64\u548c\u5f26\u5716\u5c55\u793a\u96b1\u85cf\u4e8e\u4e2d\u5716\u5178\u5c64\u4f4d\u7cfb\u7d71\u4e2d\u95dc\u806f\u8a5e\u4e4b\u9593\u8c61\u5fb5\u95dc\u4fc2\u7d50\u69cb\u3002\u6587\u5b57\u7684\u8272\u5f69\u8868\u793a\u4e03\u500b\u57fa\u672c\u985e\u76ee\uff08\u81ea\u7136\u754c\u7b49\uff09\uff0c\u800c\u6ce2\u72c0\u7dab\u662f\u95dc\u806f\u8a5e\u7684\u9023\u7dab\u3002\u7576\u9f20\u6a19\u89f8\u78b0\u4e00\u500b\u8a5e\u532f\u6642\uff0c\u9023\u7dab\u5c07\u6703\u8b8a\u6210\u85cd\u8272\uff0c\u540c\u6642\u5c07\u6703\u51fa\u73fe\u4e00\u500b\u6587\u672c\u6846\uff0c\u6846\u5185\u986f\u793a\u8a72\u8a5e\u53ca\u5176\u5c0d\u61c9\u7684\u95dc\u806f\u8a5e",
    },
    "zh_hans": {
        "1": "\u81ea\u7136\u754c",
        "2": " \u4eba\u985e",
        "3": " \u793e\u6703\u8207\u6587\u5316",
        "4": " \u5b97\u6559",
        "5": " \u795e\u8a71\u8207\u50b3\u8aaa",
        "6": " \u6b77\u53f2\u8207\u5730\u7406",
        "7": " \u6587\u5b78\u4f5c\u54c1",
        "search": "\u68c0\u7d22",
        "help": "\u5e2e\u52a9",
        "yourplists": "\u6211\u7684\u5217\u8868",
        "feedback": "\u53cd\u9988",
        "typeheretostartsearch": "\u8f93\u5165\u5173\u952e\u8bcd",
        "changelang": "Change Language",
        "browse": "\u6d4f\u89c8",
        "termsused": "\u6807\u5f15\u8bcd",
        "collection": "\u6536\u85cf\u673a\u6784",
        "resultsfound": "... \u68c0\u7d22\u7ed3\u679c",
        "citableurl": "\u53c2\u8003\u94fe\u63a5",
        "clearsearch": "\u6e05\u7a7a\u7ed3\u679c",
        "searchresults": "\u68c0\u7d22\u7ed3\u679c",
        "saveditems": "\u4fdd\u5b58",
        "imageurl": "\u56fe\u7247\u94fe\u63a5",
        "originalsource": "\u539f\u59cb\u51fa\u5904",
        "insearchresults": "\u5355\u4ef6\u9605\u89c8",
        "nonotationsassign": "\u6b64\u4ef6\u5c1a\u672a\u88ab\u6807\u5f15\uff0c\u8bf7\u4f7f\u7528ICONCLASS\u4ee3\u7801\u6807\u5f15",
        "addcomment": "\u8bc4\u8bba",
        "metadata": "\u5143\u6570\u636e",
        "persistenturl": "\u6c38\u4e45\u94fe\u63a5",
        "allitems": "\u5168\u90e8\u85cf\u54c1",
        "addiconclass": "\u52a0\u5165ICONCLASS\u6807\u5f15",
        "null": "\u62b1\u6b49\uff0c\u8be5\u8bcd\u6682\u65e0\u56fe\u50cf",
        "about": "\u5173\u4e8e",
        "contact": "\u8054\u7edc",
        "team": "\u56e2\u961f",
        "howtouse": "\u5982\u4f55\u4f7f\u7528",
        "sortedobjectid": "\u4ee5\u85cf\u54c1\u7f16\u53f7\u6392\u5e8f",
        "sortedcollection": "\u4ee5\u6536\u85cf\u673a\u6784\u6392\u5e8f",
        "sortedrandomly": "\u4ee5\u968f\u673a\u65b9\u5f0f\u6392\u5e8f",
        "whatyousearchedfor": "\u68c0\u7d22\u5185\u5bb9",
        "filter_onhold": "\u4fdd\u7559",
        "filter_musthave": "\u5fc5\u542b",
        "filter_include": "\u5305\u62ec",
        "filter_exclude": "\u9664\u53bb",
        "update_results_notice": "\u6ce8\u610f\uff1a\u8fd9\u4e9b\u68c0\u7d22\u7ed3\u679c\u662f\u51fa\u81ea\u4e8e\u4e0d\u540c\u7684\u7b5b\u9009\u7ec4\u5408\u3002\u5982\u679c\u8981\u4f7f\u7528\u5f53\u524d\u9009\u5b9a\u7684\u7b5b\u9009\u6761\u4ef6\u8fdb\u884c\u68c0\u7d22\u7684\u8bdd\uff0c\u8bf7\u518d\u6b21\u70b9\u9009\u68c0\u7d22\u6309\u94ae\u3002",
        "firstofpleaserefine": "...\u4e2a\u9879\u76ee\u4e2d\u7684\u524d...\u4e2a\uff0c\u8bf7\u5c1d\u8bd5\u4f18\u5316\u68c0\u7d22",
        "usefor": "\u4e49\u7c7b\u8bcd",
        "en_displayterm": "\u82f1\u6587\u663e\u793a\u8bcd",
        "relatedterm": "\u5173\u8054\u8bcd",
        "term": "\u8bcd\u6c47",
        "homepage_text1": "\u4e2d\u56fd\u56fe\u50cf\u5fd7\u7d22\u5f15\u5178\uff08\u4e2d\u56fe\u5178\uff09\u65e8\u5728\u6c47\u96c6\u6c49\u5b66\u3001\u827a\u672f\u53f2\u548c\u4fe1\u606f\u7814\u7a76\uff0c\u5efa\u6784\u4e00\u90e8\u4e2d\u56fd\u56fe\u50cf\u5fd7\u5206\u7c7b\u8bcd\u5178\u3002",
        "homepage_text2": "\u56fe\u50cf\u5fd7\u662f\u4e00\u79cd\u690d\u6839\u4e8e\u6b27\u6d32\u827a\u672f\u53f2\u7684\u7814\u7a76\u65b9\u6cd5\uff0c\u5386\u6765\u88ab\u7528\u6765\u7eaa\u5f55\u548c\u68c0\u7d22\u6b27\u7f8e\u827a\u672f\u56fe\u50cf\u3002\u7531\u4e8e\u7f3a\u4e4f\u975e\u897f\u65b9\u827a\u672f\u56fe\u50cf\u7684\u7eaa\u5f55\u6a21\u578b\uff0c\u6b27\u6d32\u53ca\u5317\u7f8e\u6536\u85cf\u673a\u6784\u4e2d\u7684\u4e2d\u56fd\u827a\u672f\u54c1\u901a\u5e38\u4ee5\u897f\u65b9\u4e3a\u4e2d\u5fc3\u7684\u5206\u7c7b\u4f53\u7cfb\u8fdb\u884c\u7f16\u76ee\u3002 CIT\u63d0\u4f9b\u4e86\u4e00\u4e2a\u72ec\u7279\u7684\u673a\u4f1a\uff0c\u6839\u636e\u4e2d\u56fd\u4f20\u7edf\u89c6\u89c9\u6587\u5316\u7684\u7279\u6027, \u521b\u5efa\u4e00\u79cd\u66ff\u4ee3\u5206\u7c7b\u65b9\u6848\uff0c\u5e76\u4f7f\u4e2d\u6b27\u827a\u672f\u7cfb\u7edf\u6bd4\u8f83\u6210\u4e3a\u53ef\u80fd\u3002",
        "homepage_text3": "\u6d4f\u89c8\u5e76\u68c0\u7d22\u4e2d\u56fe\u5178\u8bcd\u6c47",
        "homepage_text4": "\u4e00\u4e2a\u5177\u6709\u5c42\u7ea7\u5173\u7cfb\u7684\u5206\u7c7b\u7cfb\u7edf, \u5206\u4e3a\u4ee5\u4e0b\u5927\u7c7b\uff1a",
        "homepage_text5": "\u641c\u7d22\u4e2d\u56fe\u5178\u56fe\u50cf\u6863\u6848\u5e93",
        "homepage_text6": "\u4e2d\u56fe\u5178\u65e8\u5728\u521b\u5efa\u4e00\u79cd\u7d22\u5f15\u6807\u51c6\uff0c\u4ee5\u4fc3\u8fdb\u4e2d\u56fd\u6570\u5b57\u56fe\u50cf\u8de8\u673a\u6784\u85cf\u54c1\u68c0\u7d22\u3002\u6863\u6848\u5e93\u6240\u6536\u5f55\u7684\u56fe\u50cf\u7528\u4ee5\u5c55\u793a\u4e2d\u56fe\u5178\u672f\u8bed\u7684\u5177\u4f53\u5e94\u7528\u3002\u6bcf\u5e45\u56fe\u50cf\u5747\u4e0e\u85cf\u54c1\u673a\u6784\u539f\u59cb\u6570\u636e\u5e93\u7f51\u7ad9\u94fe\u63a5\u3002\u6863\u6848\u5e93\u5b9a\u671f\u589e\u52a0\u66f4\u591a\u6536\u85cf\u54c1\u673a\u6784\u53ca\u85cf\u54c1\u3002",
        "homepage_chord_diagram_title": "\u4e2d\u56fe\u5178\u5173\u8054\u8bcd\u548c\u5f26\u56fe",
        "homepage_chord_diagram_text": "\u6b64\u548c\u5f26\u56fe\u5c55\u793a\u9690\u85cf\u4e8e\u4e2d\u56fe\u5178\u5c42\u4f4d\u7cfb\u7edf\u4e2d\u5173\u8054\u8bcd\u4e4b\u95f4\u8c61\u5f81\u5173\u7cfb\u7ed3\u6784\u3002\u6587\u5b57\u7684\u8272\u5f69\u8868\u793a\u4e03\u4e2a\u57fa\u672c\u7c7b\u76ee\uff08\u81ea\u7136\u754c\u7b49\uff09\uff0c\u800c\u6ce2\u72b6\u7ebf\u662f\u5173\u8054\u8bcd\u7684\u8fde\u7ebf\u3002\u5f53\u9f20\u6807\u89e6\u78b0\u4e00\u4e2a\u8bcd\u6c47\u65f6\uff0c\u8fde\u7ebf\u5c06\u4f1a\u53d8\u6210\u84dd\u8272\uff0c\u540c\u65f6\u5c06\u4f1a\u51fa\u73b0\u4e00\u4e2a\u6587\u672c\u6846\uff0c\u6846\u5185\u663e\u793a\u8be5\u8bcd\u53ca\u5176\u5bf9\u5e94\u5173\u8054\u8bcd",
    },
}

if __name__ == "__main__":
    TRANS_XLS_FILEPATH = "translations.xlsx"
    TRANS_JSON_FILEPATH = "translations.json"
    if sys.argv[1] == "write":
        by_id = json.load(open(TRANS_JSON_FILEPATH))

        workbook = Workbook()
        ws = workbook.active
        ws.cell(row=1, column=2, value="en")
        ws.cell(row=1, column=3, value="zh_hant")
        ws.cell(row=1, column=4, value="zh_hans")
        row = 2
        for id, by_lang in by_id.items():
            ws.cell(row=row, column=1, value=id)
            col = 2
            for lang in ("en", "zh_hant", "zh_hans"):
                ws.cell(row=row, column=col, value=by_lang.get(lang, ""))
                col += 1
            row += 1
        workbook.save(filename=TRANS_XLS_FILEPATH)
    if sys.argv[1] == "read":
        by_id = {}
        wb = load_workbook(filename=TRANS_XLS_FILEPATH)
        sheet = wb.worksheets[0]
        for i, row in enumerate(sheet.rows):
            if i == 0:
                continue
            idx = row[0].value
            en = row[1].value
            if en:
                by_id.setdefault(idx, {})["en"] = en
            zh_hant = row[2].value
            if zh_hant:
                by_id.setdefault(idx, {})["zh_hant"] = zh_hant
            zh_hans = row[3].value
            if zh_hans:
                by_id.setdefault(idx, {})["zh_hans"] = zh_hans
        open(TRANS_JSON_FILEPATH, "w").write(json.dumps(by_id, indent=2))
