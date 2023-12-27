# Image Conversion Script

This script uses the [NO-Intro](https://datomatic.no-intro.org) DAT file for TB16/PC-Engine HUcards or the [Redump](http://http://redump.org/downloads/) DAT file for TB16/PC-Engine CD's and the [libretro-thumbnails](https://github.com/libretro-thumbnails/libretro-thumbnails) to create bin files compatible with the Analogue Duo.  The files will need to be put in the SDCard in the System\Library\Images\pce or System\Library\Images\pcecd directory depending if it is ahucard or CD game.

Probably still has bugs and a few games are missing, will keep working on it.  Also BoxArt has to be reduced to 165x165 pixels.

I created a release zip file with the images.  Unzip it to the System\Library\Images\pce directory on your SDCard, it is only the BoxArt.  Working on a PCECD release should be up shortly

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

## Conversion Process for HuCard and CD Games
For each game listed in the XML data file:

### Match Game Title to Image File:
  - For HuCard games, match the game title directly from the XML to the image file names in the input directory.
  - For CD games, if there's only one .bin file associated with the game, use its CRC. If there are multiple .bin files, select the CRC of the file named "(Track 02)" or "(Track 2)".

### Skip Image if No Match Found:
  - If no matching image file is found for a game title, or if no appropriate CRC value is found, skip the image.

### Image Resizing:
  - Resize the matched image to a height of 165 pixels while maintaining the aspect ratio.

### Convert Image to RGBA Mode:
  - Convert the image to RGBA mode to ensure it has a consistent format for processing.

### Write Pixel Data to Custom Binary Format:
  - Process the pixel data of the image and write it to a custom binary format as per the requirements of the target system or application.

### Save the Converted Image:
  - Save the converted image file with the name format "{crc}.bin", where {crc} is the CRC value extracted from the XML data file.

## Threading

The image conversion process is threaded using the `concurrent.futures` module to utilize multiple CPU cores.

## Error Handling

Any exceptions during processing will be printed but otherwise ignored, allowing the script to continue converting other images
