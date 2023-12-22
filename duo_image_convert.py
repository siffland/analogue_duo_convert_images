#!/usr/bin/env python3.10

from pathlib import Path
from typing import Optional
import sys
import xml.etree.ElementTree as ET
from PIL import Image
import struct
import concurrent.futures

target_height = 165

def get_crc_name(filename: str, games: list[ET.ElementTree]) -> Optional[str]:
    for game_title in games:
        if game_title.attrib['name'] in filename:
            rom = game_title.find('rom')
            crc = rom.attrib.get('crc')
            if crc:
                return crc + '.bin'
    return None

def convert_image(in_path: Path, out_dir: Path, games: list[ET.ElementTree]):

    filename = in_path.name
    crc_name = get_crc_name(filename, games)

    if not crc_name:
        print(f"No CRC found for {filename}") 
        return

    out_path = out_dir / crc_name 

    print(f"Converting {filename} to {crc_name}")
    
    in_img = Image.open(in_path)  

    width, height = in_img.size  
    scale = target_height / height
    in_img = in_img.resize((int(width*scale), target_height))

    rgb_img = in_img.convert("RGBA") 

    pixels = rgb_img.getdata()

    bpp = 4  
    width, height = in_img.size

    image = []
    image.append(bpp*8)   
    image.append(0x49)
    image.append(0x50)
    image.append(0x41)

    image.append(width&0xFF)
    image.append((width>>8)&0xFF)    
    image.append(height&0xFF)
    image.append((height>>8)&0xFF)
    
    for i in range(width*height):
        image.append(pixels[i][2]) 
        image.append(pixels[i][1])
        image.append(pixels[i][0])
        image.append(pixels[i][3])

    with open(out_path, 'wb') as f:
        for i in range((width*height*bpp)+8):
            f.write(struct.pack('B', image[i]))
            
def convert_image_thread(in_path, out_dir, games): 
    convert_image(in_path, out_dir, games)

def main():

    if len(sys.argv) != 4:
        print("Usage: script.py <data_file.dat> <input_dir> <output_dir>")
        sys.exit(1)

    data_file = Path(sys.argv[1])  
    in_dir = Path(sys.argv[2])
    out_dir = Path(sys.argv[3])

    root = ET.parse(data_file).getroot()
    games = root.findall('game')  

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for in_path in in_dir.iterdir():
            if in_path.is_file():
                futures.append(executor.submit(convert_image_thread, in_path, out_dir, games))

        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("Unexpected error: " + str(e))
