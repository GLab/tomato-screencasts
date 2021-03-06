# tomato-screencast

This project includes the source files and final output of the screencasts which will be used to demonstrate ToMaTo.

## Please reade before contributing

I don't commit big binary files (i.e., captivate projects and their output) regularly. Please contact @t-gerhard before making actual changes to avoid conflicts

## the sources directory

Each screencast has a subdirectory, and is identified by its key.
This contains all sources, and the compiled versions of these (i.e., video files). It does not need to contain these in different formats.

In this directory, there is a json file named after its key, the descriptor file. This lists all files which will be included in the published version, and some metadata.
The descriptor is of the format:

```
{
  "title": "Human-Readable screencast title",
  "description": "description text for the screencast. What is this about?",
  "video_file": "filename of the raw video, which will be converted to the required formats",
  "poster": "filename of the poster, i.e., the picture to be displayed before the user presses the play button",
  "tracks": [
              {"filename": "example.srt",
               "kind": "subtitles",
               "label": "Example",
               "srclang": "en",
               "default": false}
             ],
  "downloads": [
              {"title": "Example File",
               "filename": "example.tar.gz"}
             ]
}
```

The key `index` may not be used.
The `sources` directory contains an `index.json` file which lists all keys in their desired order.

## build.py

This creates JSON and Jekyll files to integrate these into a website.
It also converts the source video file into the target formats (currently hardcoded in the script)

It needs the avconv command to be installed on the computer.

Example usages: 
```
# build the screencast in the 'basic' directory and create json files
build.py -k basic -j -t /home/user/screencasts

# build all screencasts and create an index file, everything to be used in a jekyll project
# e.g., the basic screencast shall be available as http://127.0.0.1:4000/screencasts/basic
# the user will have to put files in _* directories where they need to be put, the rest in the 'screencasts' folders
build.py -a -c -m screencasts -t /home/user/screencasts

# display help
build.py --help
```
## json

Use the `--json` option to produce JSON metadata files.
For each screencast `key`, it creates a folder named `key_media` and a descriptor file named `key.json`. The descriptor is of the format:
```
{
  "title": "Basic Usage",
  "description": "Create and start your first topology.",
  "sources": [
              {"src": "basic.webm",
               "type": "video/webm"}
             ],
  "tracks": [], #list of objects, which have html objects inside them, e.g. {"src":"subtitle.srt", "type": "caption", "srclang":"en", "label":"English"}
  "downloads": [] #list of objects of form {"src": "example.tar.gz", "title":"Example archive"}
}
```
All files linked in the descriptor file are relative to the screencast's key directory.

There is a `index.json` file next to all other files, which is a sorted list of all screencasts:
```
[
  {
  'key': 'basic',
  'title': 'title as in basic.json',
  'description': 'description as in basic.json'
  },
  ....
]
```

## Jekyll

build.py can also output files to include into a jekyll project. Use the `--markdown` option.
Example usage:
```
build.py -acm screencastss -t ~/screencast_out
```
creates links between files assuming the screencast root is in http://screencastss.
Move the `_includes`, `_layouts`, and `_data` folders where they belong, and the rest into your `/screencastss` directory.
Then you can `{% include screencast_list.html %}`.
