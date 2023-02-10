# Import Libraries
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
import requests
import m3u8

input_url = input("URL: ")

while "rumble.com/" not in input_url:
    print("Invalid URL")
    input_url = input("URL: ")

resolution = input("Resolution [360, 720, etc.]: ")

html = BeautifulSoup(requests.get(input_url).content, "html.parser")
base = "https://rumble.com/embedJS/u3/?request=video&ver=2&v="
embedJS = base + str(html.find("link", rel="alternate"))[92:].split("%2F")[0]
json = json.loads(requests.get(embedJS).content)

if str(json["livestream_has_dvr"]) == "True" and str(json["live_placeholder"]) != "True":

    playlist = BeautifulSoup(requests.get(json["u"]["hls"]["url"]).content, "html.parser").text.split("\n")
    while resolution + "p" not in str(playlist):
        print("Invalid Resolution")
        resolution = input("Resolution: ")

    i = 0
    while (str(playlist[i])).find(resolution + "p") == -1:
        i = i+1

    ts_base = playlist[i].rsplit("/", 1)[0] + "/"
    chunklist = m3u8.loads(requests.get(playlist[i]).text)

    with open("video.ts", 'wb') as f:
        for segment in tqdm(chunklist.data['segments']):
            url = segment['uri']
            r = requests.get(ts_base + url, stream=True)
            f.write(r.content)

elif str(json["livestream_has_dvr"]) != "True":

    while "'h': " + resolution not in str(json["ua"]["mp4"]):
        print("Invalid Resolution")
        resolution = input("Resolution: ")

    r = requests.get(json["ua"]["mp4"][resolution]["url"], stream=True)
    with open("video.mp4", "wb") as f:
        for chunk in tqdm(r.iter_content(chunk_size=64)):
            f.write(chunk)
