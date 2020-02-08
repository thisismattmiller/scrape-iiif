
from PIL import Image
import json, requests
import sys
import tempfile
import io

if len(sys.argv) < 2:
	raise ValueError('You did not pass the info URL')

infourl = sys.argv[1]

if 'http' not in infourl or 'info.json' not in infourl:
	raise ValueError('Does not look like you passed the url to info.json')	

# https://images.iiifhosting.com/iiif/d61510444851fe89a337cc0fcdd58ccca5a3cb164a21089e027f79cba9c7efe1/info.json

try:
	infodata = requests.get(infourl).json()
	height = infodata['height']
	width = infodata['width']

	# force 1000px titles 
	title_size = 1000

	# uncomment to use the defined tile sizes
	# if 'tiles' in infodata:
	# 	title_size = infodata['tiles'][0]['width']

except:
	raise ValueError('Could not download/parse image metadata from info.json')	


img = Image.new("RGB", (width,height), "white")

for x in range(int(width/title_size)+1):
	for y in range(int(height/title_size)+1):
		print(f'/{x*title_size},{y*title_size},{title_size},{title_size}/full/0/native.jpg')
		url = infourl.replace('/info.json','') + f'/{x*title_size},{y*title_size},{title_size},{title_size}/full/0/native.jpg'
		buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
		r = requests.get(url, stream=True)
		if r.status_code == 200:
			downloaded = 0
			# print(r.headers)
			# filesize = int(r.headers['content-length'])
			for chunk in r.iter_content():
				downloaded += len(chunk)
				buffer.write(chunk)
			buffer.seek(0)
			i = Image.open(io.BytesIO(buffer.read()))

			img.paste(i, (x*title_size,y*title_size))
		else:
			raise ValueError('Error downloading tiles')	


img.save(f"{infourl.replace('/info.json','').split('/')[-1]}.jpg")

