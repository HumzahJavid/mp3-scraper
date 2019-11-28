from pathlib import Path
import urllib.request
import bs4
import requests
from bs4 import BeautifulSoup
import html


def get_page_urls():
    base_url = "https://muslimcentral.com/series/yasir-qadhi-seerah/page/"
    page_urls = []
    for i in list(range(12))[::-1]:
        page_urls.append(base_url+str(i))
    return page_urls


def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def get_html_soup(url):
    r = requests.get(url)
    if r.status_code == 404:
        return None
    else:
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
    return soup


def extract_data_elements(soup):
    # the formatting of the website changed as I was coding this 27/11/19 @ 3-3:30pm
    # return soup.select("div.ep.ep--narrow > button")
    return soup.find_all("div", {"itemtype": "http://schema.org/AudioObject"})


def clean_titles(titles, underscore=False):
    clean_titles = []
    for i in range(len(titles)):
        title = html.unescape(titles[i])
        if underscore:
            #"_".join(title.split(" "))
            title.replace(" ", "_")
        clean_titles.append(title)
    return clean_titles


def parse_data_elements(soup_data):
    titles = []
    urls = []
    for i in range(len(soup_data)):
        title = soup_data[i].meta["content"]
        url = soup_data[i].a["href"]
        titles.append(title)
        urls.append(url)
    titles = clean_titles(titles, True)
    return (titles, urls)


def get_titles_urls(page_url):
    video_titles = []
    video_urls = []
    soup = get_html_soup(page_url)
    element_containing_episodes = extract_data_elements(soup)
    video_titles, video_urls = parse_data_elements(element_containing_episodes)
    return video_titles[::-1], video_urls[::-1]


def file_stats(title, url):
    file_len = int(urllib.request.urlopen(url).headers.get("Content-Length"))
    file_mb = str(file_len/10.0**6)[:5]
    print(f"File name: {title}.mp3")
    print(f"File size: {file_mb} MB")
    print("Downloading...")


def download(file_title, file_url, progress_bar=False):
    if is_downloadable(file_url):
        file_stats(file_title, file_url)
        if progress_bar:
            # tqdm PROGRESS BAR IS SLOW 4:16(m:s) with vs < 0:20 without
            response = requests.get(file_url, stream=True)
            with open(file_title+".mp3", "wb") as handle:
                for data in tqdm.tqdm(response.iter_content()):
                    handle.write(data)
        else:
            urllib.request.urlretrieve(file_url, file_title+".mp3")


def main(download_location=""):
    page_urls = get_page_urls()
    page_number=1
    for page in page_urls:
        print(f"Accessing page {page_number} / {len(page_urls)}")
        print("Downloading from page " + page)
        titles, urls = get_titles_urls(page)
        for i in range(len(titles)):
            print(f"Downloading file {str(i+1)} / {str(len(titles))} (on current page)")
            download(download_location+titles[i], urls[i])
        page_number+=1


home = str(Path.home())
download_path = home+"\music\download\\"
main(download_path)
