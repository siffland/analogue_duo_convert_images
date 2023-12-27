# Image Conversion Script

This script uses the [NO-Intro](https://datomatic.no-intro.org) DAT file for TB16/PC-Engine and the [libretro-thumbnails](https://github.com/libretro-thumbnails/libretro-thumbnails) to create bin files compatible with the Analogue Duo.  the files will need to be put in the SDCard in the System\Library\Images\pce directory.  Currently this only works for HuCards.  

Probably still has bugs and a few games are missing, will keep working on it.  Also BoxArt has to be reduced to 165x165 pixels, I understand this on the Pocket, but not on a 1080p tv, hopefully that gets fixed in an update.

I created a release zip file with the images.  Unzip it to the System\Library\Images\pce directory on your SDCard, it is only the BoxArt.

## Usage

&nbsp;

Copy code

`duo_image_convert.py <data_file.dat> <input_dir> <output_dir>`

- `data_file.dat` \- DAT file containing game metadata like names and CRC values, get from NO-Intro
- `input_dir` \- Directory containing images to convert
- `output_dir` \- Where to save converted images - this has to already exist

The script looks up the CRC value for each input image based on the filename and game title in the XML data. The converted images are named using the CRC value + ".bin" extension.

A real world example might be:

`python3.10 duo_image_convert.py NEC\ -\ PC\ Engine\ -\ TurboGrafx-16\ \(20231220-141601\).dat /mnt/thumbnails/NEC\ -\ PC\ Engine\ CD\ -\ TurboGrafx-CD/Named_Boxarts/ output_directory/`

## Requirements

- Python 3.10+
- PIL / Pillow image library

## Conversion Process

For each input image:

1.  Lookup CRC by matching filename to game title in XML
2.  Skip image if no CRC found
3.  Resize image to 165 pixels tall, maintaining aspect ratio
4.  Convert to RGBA mode
5.  Write pixel data to custom binary format
6.  Save converted image as "{crc}.bin"

## Threading

The image conversion process is threaded using the `concurrent.futures` module to utilize multiple CPU cores.

## Error Handling

Any exceptions during processing will be printed but otherwise ignored, allowing the script to continue converting other images
