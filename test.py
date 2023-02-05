# Import Libraries
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import m3u8

input_url = input("URL: ")
res = input("Resolution: ")
resolutions = [".oaa.mp4", ".baa.mp4", ".caa.mp4", ".gaa.mp4", ".haa.mp4", ".iaa.mp4", ".jaa.mp4"]

html = requests.get(input_url)
soup = BeautifulSoup(html.content, "html.parser")
video_url = str(soup.find("meta", property="og:image")).split('"')[1]

while video_url.count(".") > 2:
    video_url = video_url.rsplit(".", 1)[0]

s8 = video_url.find("s8") + 3
video_url = video_url[:int(s8)] + "2" + video_url[int(s8+1):] + resolutions[int(res)]
dvr = "https://rumble.com/live-hls-dvr/" + str(soup.find("link", rel="alternate"))[93:99] + "/playlist.m3u8"
dvr_code = requests.get(dvr).status_code

# Fallback
chunklist_code = 404
chunklist_url = "nan"

if requests.get(dvr).status_code == 200:
    html = requests.get(dvr)
    soup = BeautifulSoup(html.content, "html.parser")
    chunklist_url = str(soup.text.split("\n")[-1])
    chunklist_code = int(requests.get(chunklist_url).status_code)

if chunklist_code == 404 or dvr_code == 404:
    # Whole Video (.mp4)
    if requests.get(dvr).status_code == 200:
        video_url = video_url[:video_url.rfind(".")] + ".rec" + video_url[video_url.rfind("."):]
        print(video_url)
    chunk_size = 1024
    r = requests.get(video_url, stream=True)
    with open("video.mp4", "wb") as f:
        for chunk in tqdm(r.iter_content(chunk_size=chunk_size)):
            f.write(chunk)

elif chunklist_code == 200:
    # Chunk Video (.ts)
    html = requests.get(chunklist_url)
    m3u8_playlist = m3u8.loads(html.text)
    m3u8_segment_uris = [segment['uri'] for segment in m3u8_playlist.data['segments']]
    thing = str(chunklist_url.rsplit("/", 1)[0]) + "/"
    with open("video.ts", 'wb') as f:
        for segment in tqdm(m3u8_playlist.data['segments']):
            url = segment['uri']
            r = requests.get(thing + url)
            f.write(r.content)
