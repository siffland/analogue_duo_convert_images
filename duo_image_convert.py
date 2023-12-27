#!/usr/bin/env python3.10

from pathlib import Path
from typing import Optional
import sys
import xml.etree.ElementTree as ET
from PIL import Image
import struct
import concurrent.futures
import re

special_chars = r'[&\/:*`<>?\\"|]'
target_height = 165

def fix_title(title):
    return re.sub(special_chars, '_', title)

def get_crc_from_game_hucard(game_name: str, games: list[ET.Element]) -> str:
    normalized_game_name = fix_title(game_name)
    for game in games:
        title = game.attrib.get('name')
        if title and fix_title(title) == normalized_game_name:
            rom = game.find('rom')
            if rom is not None:
                return rom.attrib.get('crc')
    return None

def get_crc_from_game_cd(game_name: str, games: list[ET.Element]) -> str:
    normalized_game_name = fix_title(game_name)
    track_pattern = re.compile(r'\(Track 0?2\)')  # Regex pattern to match both (Track 02) and (Track 2) since both are used

    for game in games:
        title = game.attrib.get('name')
        if title and fix_title(title) == normalized_game_name:
            bin_files = [rom for rom in game.findall('rom') if rom.attrib.get('name').endswith('.bin')]

            # If there's only one .bin file, return its CRC
            if len(bin_files) == 1:
                return bin_files[0].attrib.get('crc')

            # If there are multiple .bin files, look for "Track 02"
            for bin_file in bin_files:
                if track_pattern.search(bin_file.attrib.get('name')):
                    return bin_file.attrib.get('crc')

    return None

def find_matching_image(game_name: str, image_dir: Path) -> Optional[Path]:
    normalized_game_name = fix_title(game_name)
    for image_path in image_dir.iterdir():
        if image_path.is_file():
            image_file_name = fix_title(image_path.stem)
            if normalized_game_name in image_file_name:
                return image_path
    return None

def convert_image(game_name: str, image_dir: Path, out_dir: Path, games: list[ET.Element], is_cd: bool):
    image_path = find_matching_image(game_name, image_dir)
    if not image_path:
        print(f"No matching image found for {game_name}")
        return

    crc = get_crc_from_game_cd(game_name, games) if is_cd else get_crc_from_game_hucard(game_name, games)
    if not crc:
        print(f"No CRC found for {game_name}")
        return

    out_path = out_dir / f"{crc}.bin"
    print(f"Converting {image_path.name} to {out_path.name}")

    in_img = Image.open(image_path)
    width, height = in_img.size
    scale = target_height / height
    in_img = in_img.resize((int(width * scale), target_height))
    rgb_img = in_img.convert("RGBA")
    pixels = rgb_img.getdata()

    bpp = 4
    width, height = in_img.size

    image = [bpp * 8, 0x49, 0x50, 0x41,
             width & 0xFF, (width >> 8) & 0xFF,
             height & 0xFF, (height >> 8) & 0xFF]

    for i in range(width * height):
        image.extend([pixels[i][2], pixels[i][1], pixels[i][0], pixels[i][3]])

    with open(out_path, 'wb') as f:
        for byte in image:
            f.write(struct.pack('B', byte))

def convert_image_thread(game_name, image_dir, out_dir, games, is_cd):
    convert_image(game_name, image_dir, out_dir, games, is_cd)

def main():
    if len(sys.argv) != 4:
        print("Usage: script.py <data_file.dat> <input_dir> <output_dir>")
        sys.exit(1)

    data_file = Path(sys.argv[1])
    image_dir = Path(sys.argv[2])
    out_dir = Path(sys.argv[3])

    root = ET.parse(data_file).getroot()
    is_cd = 'CD' in root.find('header/name').text	#This checks the header name for the letters CD to determine which function to use
    games = root.findall('game')

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for game in games:
            game_name = game.attrib.get('name')
            if game_name:
                futures.append(executor.submit(convert_image_thread, game_name, image_dir, out_dir, games, is_cd))

        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("Unexpected error: " + str(e))
