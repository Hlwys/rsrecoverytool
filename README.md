# RuneScape Cache Recovery Tool

- This script will recover any RuneScape Classic or early RuneScape 2 cache file from an image of a hard drive.

## Requirements

- Windows operating system
- Python 3.x

## Usage

1. You will need to make an image of the drive you are recovering from. There are several programs that can do this, DMDE is a free tool. <https://dmde.com/>

2. Edit the "run.bat" to specify the filepath of the image you have created for both lines.

3. Two scripts will run - the first will scan the image for all file locations then produce a list of locations called `output.txt`.
   The second will then extract files based on these locations. If you are running the script again you can delete the search command and just run the extraction.

The search should take roughly 30 minutes for an 80GB hard drive.
