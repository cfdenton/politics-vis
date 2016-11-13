#!/usr/bin/python

import sys
import re
import requests
from bs4 import BeautifulSoup
from newspaper import Article

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

# check that to urls are not from the same domain
def same_domain(url1, url2, print_out):
    #?(.*?)\.(?:com|au.uk|co\.in)/
    reg = re.compile(r'\.[a-zA-Z0-9]*\.(?:com|au.uk|co\.in|co\.uk|gov|org|edu|us)')
    s1 = reg.search(url1)
    s2 = reg.search(url2)
    if not (s1 and s2): return False
    domain1 = reg.search(url1).group(0)
    domain2 = reg.search(url2).group(0)

    if print_out:
        print(1, url1)
        print(2, url2)
        print(domain1 == domain2)
    return domain1 == domain2

# search a web page's text to find given phrase matches. assumes a validated url
def search_page(url, phrases):
    try:
        r = requests.get(url, timeout=.1)
        page_soup = BeautifulSoup(r.text, 'html.parser')
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

    r = requests.get(source_url)
    page_soup = BeautifulSoup(r.text, 'html.parser')
    page_summaries = []

    for ref_tag in page_soup.find_all('a', href=True):
        if (not valid_url(ref_tag['href'])) or same_domain(source_url, ref_tag['href'], False):
            continue

        if search_page(ref_tag['href'], phrases):   
            print("adding "+ ref_tag['href'][0:40] + " remaining levels ", max_depth-1)
            print(same_domain(source_url, ref_tag['href'], True))
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
    return {"url": url, "parent_url": url}            

def main(arg):
    guardian_ref = 'https://www.theguardian.com/commentisfree/2016/nov/10/after-donald-trump-win-americans-organizing-us-politics'
    nyt_ref = 'https://www.nytimes.com/2016/11/13/business/economy/can-trump-save-their-jobs-theyre-counting-on-it.html'
    google_ref = "http://www.google.com"
    reddit_ref = "http://www.reddit.com"
    guardian_ref2 = "http://www.theguardian.com/us"
    facebook_ref = "https://www.facebook.com"
    
    pages = branch_from_source(guardian_ref, ['Donald Trump', 'Trump', 'Donald', 'Election'], 3)
    pages = delete_duplicate(pages)
    for p in pages:
        print(p)

    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]));
