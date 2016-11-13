#!/usr/bin/python
import pickle
import sys
import re
import requests
from bs4 import BeautifulSoup
from langdetect import detect
from newspaper import Article
import random

# check that a url is valid
def valid_url(url):
    validator = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if validator.match(url):
        return True
    return False

# check that two urls are not from the same domain
def same_domain(url1, url2, print_out):
    #?(.*?)\.(?:com|au.uk|co\.in)/
    reg = re.compile(r'\.[a-zA-Z0-9]*\.(?:com|au.uk|co\.in|co\.uk|gov|org|edu|us|it|fr|mx|net|int|mil|arpa|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|bq|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cw|cx|cy|cz|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|ru)')
    s1 = reg.search(url1)
    s2 = reg.search(url2)
    if not (s1 and s2): return False
    domain1 = re.search(r'\.[a-zA-Z0-9]*\.', reg.search(url1).group(0)).group(0)
    domain2 = re.search(r'\.[a-zA-Z0-9]*\.', reg.search(url2).group(0)).group(0)
    #print(domain1, domain2) 
    
    if print_out:
        print(1, url1)
        print(2, url2)
        print(domain1 == domain2)
    return domain1 == domain2


# perform two tasks: 
# check that a web page is in english
# search the web page's text to find given phrase matches. assumes a validated url
def check_page(url, phrases):
    try:
        r = requests.get(url, timeout=.1)
        page_soup = BeautifulSoup(r.text, 'html.parser')
        content = " ".join( \
                [x for x in [p.string for p in page_soup.find_all('p')] \
                if x is not None])
        if detect(content) != 'en':
            return False

        for p in page_soup.find_all('p'):
            for phrase in phrases:
                if p.string and phrase in p.string:
                    return True
        for a in page_soup.find_all('a'):
            for phrase in phrases:
                if a.string and phrase in a.string:
                    return True
        return False

    except Exception:
        return False



# return a list of pages connected relevant pages branching at most to depth `max_depth`
def branch_from_source(source_url, phrases, max_depth):
    assert(max_depth > 0)
    try:
        r = requests.get(source_url, timeout=1)
        page_soup = BeautifulSoup(r.text, 'html.parser')
    except Exception:
        return [] 

    page_summaries = []

    for ref_tag in page_soup.find_all('a', href=True):
        if (not valid_url(ref_tag['href'])) or same_domain(source_url, ref_tag['href'], False):
            continue

        if check_page(ref_tag['href'], phrases):   
            print("adding "+ ref_tag['href'][0:40] + " remaining levels ", max_depth-1)
            page_summaries.append(page_summary(ref_tag['href'], source_url))
            if max_depth > 1:
                page_summaries.extend(branch_from_source(ref_tag['href'], phrases, max_depth - 1))

    return page_summaries
    
def delete_duplicate(array):
    output = []
    for x in array:
        if x not in output:
            output.append(x)
    return output

def page_summary(url, parent_url):
    return {"url": url, "parent_url": parent_url} 

def populate(source_url, phrases, max_depth):
    page_list = branch_from_source(source_url, phrases, max_depth)
    #page_list = []
    #with open("temp_file.out", 'r') as f:
    #    page_list = pickle.load(f)
    nodes = []
    links = []

    for i in range(len(page_list)):
        one_node = {"id": page_list[i]['url'], 
                    "x": random.randint(50, 900), 
                    "y": random.randint(50, 550), 
                    "affiliation": random.choice(["blue","red"])}
	two_node = None
	if page_list[i]['parent_url'] not in nodes and page_list[i]['url'] != page_list[i]['parent_url']:
            two_node = {"id": page_list[i]['parent_url'],
                    "x": random.randint(50, 900),
                    "y": random.randint(50, 550),
                    "affiliation": random.choice(["blue", "red"])}

        one_link = {"source": page_list[i]['url'], 
                    "target": page_list[i]['parent_url']}
        
        if {"source": page_list[i]['parent_url'], "target": page_list[i]['url']} in links:
            if two_node:
                nodes.append(two_node)
            nodes.append(one_node)
        else:
            links.append(one_link)
            nodes.append(one_node)
            if two_node:
                nodes.append(two_node)

    return {"nodes": nodes, "links": links}

def main(arg):
    guardian_ref = 'https://www.theguardian.com/commentisfree/2016/nov/10/after-donald-trump-win-americans-organizing-us-politics'
    nyt_ref = 'https://www.nytimes.com/2016/11/13/business/economy/can-trump-save-their-jobs-theyre-counting-on-it.html'
    google_ref = "http://www.google.com"
    reddit_ref = "http://www.reddit.com"
    guardian_ref2 = "http://www.theguardian.com/us"
    facebook_ref = "https://www.facebook.com"
    
    pages = branch_from_source(guardian_ref, ['Donald Trump', 'Trump', 'Donald'], 4)
    pages = delete_duplicate(pages)
    for p in pages:
        print(p)

    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]));
