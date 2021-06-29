import os
import sys
import json
from serpapi import GoogleSearch
import tldextract

secret_api_key = ""#pull from config
links_extracted = []
html_reports = []
sub_domains = []

flagged_boards = []
google_dorks = {}
DOMAIN  = sys.argv[1]
google_dorks = {}
google_dorks['subDomains'] = "site:.{}"
google_dorks['SQLErrors'] = "site:{} intext:\"sql syntax near\" | intext:\"syntax error has occurred\" | intext:\"incorrect syntax near\" | intext:\"unexpected end of SQL command\" | intext:\"Warning: mysql_connect()\" | intext:\"Warning: mysql_query()\" | intext:\"Warning: pg_connect()\""
google_dorks['PubDocum'] = 'site:{} ext:doc | ext:docx | ext:odt | ext:rtf | ext:sxw | ext:psw | ext:ppt | ext:pptx | ext:pps | ext:csv'
google_dorks['PHP_Err_Warn'] = "site:{} \"PHP Parse error\" | \"PHP Warning\" | \"PHP Error\""
google_dorks['PHP_INFO'] =  "site:{} ext:php intitle:phpinfo \"published by the PHP Group\""
google_dorks['DirLIstVuln'] = "site:{} intitle:index.of"
google_dorks['ConfigsFiles'] = "site:{} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini | ext:env"
google_dorks['DBFiles'] = "site:{} ext:sql | ext:dbf | ext:mdb"
google_dorks['SearchGit'] = "site:github.com | site:gitlab.com \"{}\""
google_dorks['LogsFiles'] = "site:{} ext:log"
google_dorks['BackupFiles'] = "site:{} ext:bkf | ext:bkp | ext:bak | ext:old | ext:backup"
google_dorks['LoginPages'] = "site:{} inurl:login | inurl:signin | intitle:Login | intitle:\"sign in\" | inurl:auth"
google_dorks['SignupPages'] = "site:{} inurl:signup | inurl:register | intitle:Signup"

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
               if dork_info['link'] not in links_extracted:
                  links_extracted.append(dork_info['link'])
               print(dork_info)
               
               
for k,v in google_dorks.items():
    print(v.format(DOMAIN))
    try:
       run_dorks(v.format(DOMAIN))
    except Exception as ex1:
       print(ex1)
       pass

if links_extracted:
   outfile_writer = open("crawled_links.txt","a")
   for links in links_extracted:
       outfile_writer.write(links+"\n")
