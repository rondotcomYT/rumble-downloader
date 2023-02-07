# Import Libraries
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
import requests
import m3u8

# to avoid errors
chunklist_url = "na"
chunklist_code = "na"
video_url = "na"
video_bitrate = "na"
video_size = "na"

# Video + Resolution Input
input_url = input("URL: ")
res = input("Resolution [360, 720, etc.]: ")

html = requests.get(input_url)
soup = BeautifulSoup(html.content, "html.parser")
embedJS = str(soup.find("link", rel="alternate"))[92:].split("%2F")[0]
vid_id = str(soup.find("link", rel="canonical"))[31:].split("-")[0]
video_ids = "https://rumble.com/embedJS/u3/?request=video&ver=2&v=" + embedJS
dvr = "https://rumble.com/live-hls-dvr/" + embedJS[1:] + "/playlist.m3u8"
dvr_code = requests.get(dvr).status_code
dvr_html = requests.get(dvr)
dvr_soup = BeautifulSoup(dvr_html.content, "html.parser")

if dvr_code == 200:
    chunklist_code = int(requests.get(dvr_soup.text.split("\n")[-1]).status_code)

if chunklist_code == 200:
    chunklist_url = dvr_soup.text.split("\n")

    while res + "p" not in str(chunklist_url):
        print("Resolution Unavailable / Invalid")
        res = input("Resolution: ")

    i = 0
    while (str(chunklist_url[i])).find(res + "p") == -1:
        i = i+1

    chunklist_url = chunklist_url[i]
    chunklist_code = int(requests.get(chunklist_url).status_code)

if dvr_code == 404 or chunklist_code == 404:
    js_html = requests.get(video_ids)
    js_data = json.loads(js_html.text)

    while "'" + res + "'" not in str(js_data['ua']['mp4']):
        print("Resolution Unavailable / Invalid")
        res = input("Resolution: ")

    video_url = js_data['ua']['mp4'][res]['url']
    video_size = js_data['ua']['mp4'][res]['meta']['size']

if chunklist_code == 404 or dvr_code == 404:
    # Whole Video (.mp4)
    chunk_size = 64
    r = requests.get(video_url, stream=True)
    with open(vid_id + "_" + res + "p.mp4", "wb") as f:
        for chunk in tqdm(r.iter_content(chunk_size=chunk_size)):
            f.write(chunk)

elif chunklist_code == 200 and dvr_code == 200:
    # Chunk Video (.ts)
    chunklist_html = requests.get(chunklist_url)
    m3u8_playlist = m3u8.loads(chunklist_html.text)
    m3u8_segment_uris = [segment['uri'] for segment in m3u8_playlist.data['segments']]
    thing = str(chunklist_url.rsplit("/", 1)[0]) + "/"
    with open(vid_id + "_" + res + "p.ts", 'wb') as f:
        for segment in tqdm(m3u8_playlist.data['segments']):
            url = segment['uri']
            r = requests.get(thing + url, stream=True)
            f.write(r.content)
