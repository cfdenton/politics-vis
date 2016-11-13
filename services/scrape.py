import sys
import requests
from bs4 import BeautifulSoup

def main(arg):
    guardian_ref = 'https://www.theguardian.com/politics/2016/nov/12/nigel-farage-arrives-in-new-york-to-meet-president-elect'
    nyt_ref = 'https://www.nytimes.com/2016/11/13/business/economy/can-trump-save-their-jobs-theyre-counting-on-it.html'
    r = requests.get(guardian_ref)
    soup = BeautifulSoup(r.text, 'html.parser')
    print(soup.title.string)
    for a in soup.find_all(href=True):
        print(a['href'])

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]));
