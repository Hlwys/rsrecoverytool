# RuneScape Cache Recovery Tool

This script will recover any RuneScape Classic or early RuneScape 2 cache file from an image of a hard drive. The tool works for any RuneScape versions from 4 January 2001 until 16 May 2006.

## Requirements

- Windows operating system
- Python 3.x

## Usage

1. You can either recover directly from a currently active hard drive, or from an image backup of the drive. There are several programs that can create an image, [DMDE](https://dmde.com/) is a free tool.

2. Edit either the `Recover from active hard drive.bat` or `Recover from drive image.bat` file depending on your preference. Replace `DRIVE LETTER` or `{IMAGE LOCATION}` on both lines, to either specify the drive letter (e.g. `F:`) or the image location (e.g. `C:\Users\User\myimage.img`)

3. Two scripts will run - the first will scan the image for all file locations then produce a list of locations called `output.txt`.
   The second will then extract files based on these locations. If you are running the script again you can delete the search command and just run the extraction.

The search should take roughly 30 minutes for an 80GB hard drive.
