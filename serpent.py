import os
import sys
import json
from pathlib import Path
import uuid
import tldextract
from serpapi import GoogleSearch
import requests
from termcolor import colored
requests.packages.urllib3.disable_warnings() 
secret_api_key = ""#put serpapi key here

links_extracted = []
html_reports = []
sub_domains = []

flagged_boards = []
google_dorks = {}


google_dorks['trello_dork'] = "site:http://trello.com   intext:{}"
google_dorks['subdomain_dork'] = "site:{}"



keywords = ['password','username','pass','api_key','api','@gmail.com','@yahoo.com','@outlook.com','American Express','MasterCard','Discover','Visa','credit/debit','login',
'/v1','/v2','webhook']

def board_parser_trello(board):
   response  = requests.get(board +".json",timeout=3,verify=False)
   if response:
      try:
         tmp_actions = json.loads(response.text)
         for k in tmp_actions['actions']:
               for item in k.items():
                     if item:
                        for _ in item:
                           is_dict = isinstance(_, dict)
                           if is_dict:
                              for dminor,dmajor in _.items():
                                    if "text" in dminor:
                                         for keyword in keywords:
                                            if keyword in dmajor:
                                              flagged_info = {}
                                              flagged_info['is_violator'] = True
                                              flagged_info['board_url'] = board
                                              flagged_info['flagged_data'] = dmajor
                                              flagged_boards.append(json.dumps(flagged_info))
                                              print(colored(json.dumps(flagged_info), 'red'))

      except Exception as ex3:
          print(ex3)
          pass
                                        
           

def run_dorks(query_in):
    params = {
    "engine": "google",
    "q": query_in,
    "api_key": secret_api_key,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    print("Raw HTML of Request")
    print("*"*50)
    print(results['search_metadata']['raw_html_file'])
    print("*"*50)
    if results['search_metadata']['raw_html_file']:
       html_reports.append(results['search_metadata']['raw_html_file'])

    print(f"Current page: {results['serpapi_pagination']['current']}")

    for dork_result in results["organic_results"]:
        print(f"Title: {dork_result['title']}\nLink: {dork_result['link']}\n")

    while 'next' in results['serpapi_pagination']:
        search.params_dict[
         "start"] = results['serpapi_pagination']['current'] * 10
        results = search.get_dict()

        print(f"Current page: {results['serpapi_pagination']['current']}")
 
        for dork_result in results["organic_results"]:
            #print(f"Title: {dork_result['title']}\nLink: {dork_result['link']}\n")
            if dork_result['link']:
               ext = tldextract.extract(dork_result['link'])
               ext = '.'.join(ext[:3])
               if ext not in sub_domains:
                  sub_domains.append(ext)
               dork_info = {}
               dork_info['link'] = dork_result['link']
               dork_info['title'] = dork_result['title']
               dork_info['query_file'] = results['search_metadata']['raw_html_file']
               links_extracted.append(dork_info)
               print(dork_info)


  
def bounty_hunt(target):
    myuuid = uuid.uuid4()
    filetocheck = str("trello_boards/"+str(myuuid)+".txt")
    for k,v in google_dorks.items():
        print(v.format(target))
        tmp_dork = v.format(target)
        try:
            run_dorks(tmp_dork)
        except Exception as glocks:
           print(glocks)
           pass

    

    return filetocheck


def result_parser(result_file):
   resultList = [line.rstrip('\n') for line in open(result_file)]
   for result in resultList:
      tmp_info = json.loads(result)
      json_board = tmp_info['link']
      print(json_board)
      try:
         if "trello" in json_board:
            board_parser_trello(json_board)
      except Exception as ex2:
         pass




def main():

    target = sys.argv[1]
    filetocheck = bounty_hunt(target)
    print(filetocheck)
    
       
    if not os.path.exists("trello_boards"):
       os.makedirs("trello_boards")

    if not os.path.exists("trello_boards/flagged_boards"):
       os.makedirs("trello_boards/flagged_boards")

    outfile = open(filetocheck,"a")
    print(outfile)
    if links_extracted: 
       for links in links_extracted:
           outfile.write(json.dumps(links)+"\n")
    outfile.close()
       

    result_parser(filetocheck)
    if flagged_boards:
       test =  Path(filetocheck).stem
       final_test = "trello_boards/flagged_boards/"+test+"_flaged_.txt"
       print(test)
       print(final_test)
       
       output_board_file =  open(final_test, 'w+')

       for boards in flagged_boards:
           output_board_file.write(boards+"\n")
       output_board_file.close()
       
    if sub_domains:
       print(sub_domains)

main()
