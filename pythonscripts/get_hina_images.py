from bs4 import BeautifulSoup
import urllib
import cloudinary
import cloudinary.uploader
from pprint import pprint

import os

cloudinary.config(
  cloud_name = os.environ.get("cloud_name"),
  api_key = os.environ.get("api_key"),
  api_secret = os.environ.get("api_secret")
)

def get_mem_list():
  url = "https://www.hinatazaka46.com/s/official/search/artist?ima=0000"
  base = "https://www.hinatazaka46.com"
  headers = {
          "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
          }

  request = urllib.request.Request(url, headers=headers)
  html = urllib.request.urlopen(request)

  soup = BeautifulSoup(html, 'html.parser')

  li = soup.select('ul[class="p-member__list"] li[class="p-member__item"] a')
  li = list(set([base + str(l.attrs['href']) for l in li]))

  return li

def get_img(url):

  headers = {
          "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
          }

  request = urllib.request.Request(url=url, headers=headers)
  html = urllib.request.urlopen(request)

  soup = BeautifulSoup(html, 'html.parser')

  img = soup.select('div[class="c-member__thumb c-member__thumb__large"] img')[0].attrs['src']
  name = str(soup.select('div[class="p-member__info"] div[class="p-member__info__head"] div[class="c-member__name--info"]')[0].text).replace(' ', '')
  #print(img)

  res = cloudinary.uploader.upload(file=img, public_id='q-u46/member-images/'+''.join(name.splitlines()))
  #pprint(res)

  return 'finished {} !!'.format(name)

def main():
  list_ = get_mem_list()

  for url in list_:
    
    print(get_img(url), end=' | ')

if __name__ == "__main__":
  main()
