import requests as r
import json

S = r.Session()
URL = "https://wikileopardi.altervista.org/wiki_leopardi/api.php"  #keeping the session opened helps with the dowload

def get_all_titles():
  titles = []
  PARAMS = {
      "action": "query",
      "list": "allpages",
      "apprefix": "F31", #just selecting the canti from 1831(Firenze)
      "format": "json"
  }

  while True: #to avoid errors
    api_request = S.get(url=URL, params=PARAMS)
    data = api_request.json()

    for page in data["query"]["allpages"]:
        titles.append(page["title"])
    if "continue" in data:
      #"Very often you will not get all the data you want in one API query. When this happens,
      #the API will append an additional element (titled continue) to the results to indicate there is more data."
      #Usually the server has a page limit for the request, this just assures the download of all requests.
        PARAMS["apcontinue"] = data["continue"]["apcontinue"]
    else:
        break

  print(f"The operation was successful! {len(titles)} were found.") #just to check the code
  return titles

def text_extraction(titles):
  corpus = {}

  for title in titles:
      PARAMS = {
          "action": "parse",
          "page": title,
          "prop": "wikitext", #fondamental to retrieve just the the pain text rather than the whole html page
          "format": "json"
      }

      api_request= S.get(url=URL, params=PARAMS)
      data = api_request.json()

      if "parse" in data:
        corpus[title] = data["parse"]["wikitext"]["*"]

  #saving
  with open("corpus_F31.json", "w", encoding="utf-8") as f:
    json.dump(corpus, f, ensure_ascii=False, indent=4)

  print(f"The operation was successful! The files are saved")

titles = get_all_titles()
text_extraction(titles)
