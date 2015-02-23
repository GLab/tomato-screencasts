#!/usr/bin/python
__author__ = 't-gerhard'
import os
import shutil
import subprocess
import sys
import json
import argparse
import inspect


# base dir of the source stuff. should be the directory of this file
basedir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# target formats for the main video
target_formats = [{'extension': "webm", 'mimetype': "video/webm"}]

# debug mode. can be changed via an argument
debug = False









# command to convert the video file.
def avconv(inputfilename, outputfilename):
	cmd = ['avconv', '-i', inputfilename, outputfilename]
	if debug:
		print " ".join(cmd)
		errcode = 0
	else:
		process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		for c in iter(lambda: process.stdout.read(1), ''):
			sys.stdout.write(c)
		errcode = process.returncode
	return errcode




# this is meant to build a single screencast.
# first, create an instance.
# then, add formats, tracks, downloadable files, and set a poster. This will not change any
# do NOT use any function which starts with a _   -- these are private ones.
# then, build it using the build function.
class ScreencastBuilder:
	tracks = []
	video_formats = []
	downloads = []
	poster = None
	descriptor_content = {'tracks': [], 'sources': [], 'downloads': []}
	md_filler = {'tracks': "", 'sources': "", 'downloads': ""}

	# key: the key this is referenced to.
	# title: onscreen title of the screencast
	# description: description of the screencast
	# input_video_file: video file to use as source
	# target_dir: the target dir. files will be saved in target_dir/key/ and target_dir/key.json
	def __init__(self, key, title, description, input_video_file, target_dir, markdown_baseurl=False, create_json=True):
		self.key = key
		self.descriptor_content['title'] = title
		self.descriptor_content['description'] = description
		self.input_video_filename = input_video_file
		self.target_dir = target_dir
		self.create_markdown = True if markdown_baseurl else False
		self.markdown_baseurl = markdown_baseurl
		self.create_json = create_json

		self.md_filler['key'] = self.key
		self.md_filler['title'] = self.descriptor_content['title']
		self.md_filler['description'] = self.descriptor_content['description']

	# convert to all video formats
	def _create_video_formats(self):
		for form in self.video_formats:
			print "Converting to %s" % form['extension']
			input = self.input_video_filename
			(outputfilename, _) = os.path.splitext(os.path.basename(input))
			outputfilename += (".%s" % form['extension'])
			output = os.path.join(self.media_dir, outputfilename)
			avconv(input, output)
			self.descriptor_content['sources'].append({'type': form['mimetype'], 'src': outputfilename})
			self.md_filler[
				'sources'] += '<source src="%(markdown_baseurl)s/%(key)s_media/%(filename)s" type="%(mimetype)s" />' % {
				'markdown_baseurl': self.markdown_baseurl, 'key': self.key, 'filename': outputfilename,
				'mimetype': form['mimetype']}

	#prepare all target directories so that files can be written directly.
	def _prepare_dir(self):
		self.media_dir = os.path.join(self.target_dir, self.key + '_media')
		assert not os.path.exists(self.media_dir)
		os.makedirs(self.media_dir)

	# Copy all tracks to the media directory.
	# Add it to md_filler and descriptor_content
	def _copy_tracks(self):
		for track in self.tracks:
			trackfilename = os.path.basename(track['filename'])
			print "Copying track %s" % trackfilename
			shutil.copy(track['filename'], os.path.join(self.media_dir, trackfilename))
			desc_entry = {'src': trackfilename, 'default': track['default'], 'kind': track['kind']}
			desc_entry.update(track['data'])
			http_opts = 'src="%(markdown_baseurl)s/%(key)s_media/%(src)s" kind="%(kind)s"' % {
				'markdown_baseurl': self.markdown_baseurl, 'key': self.key, 'src': trackfilename, 'kind': track['kind']}
			for o in track['data'].keys():
				http_opts += ' %(key)s="%(value)s"' % {'key': o, 'value': track['data'][o]}
			if track['default']:
				http_opts += ' default'
			self.descriptor_content['tracks'].append(desc_entry)
			self.md_filler['tracks'] += '<track %(httpopts)s>' % {'httpopts': http_opts}

	# Copy all downloads to the media directory.
	# Add it to md_filler and descriptor_content
	def _copy_downloads(self):
		for dl in self.downloads:
			filename = os.path.basename(dl['filename'])
			print "Copying download %s" % filename
			shutil.copy(dl['filename'], os.path.join(self.media_dir, filename))
			self.descriptor_content['downloads'].append({'title': dl['title'], 'src': filename})
			self.md_filler[
				'downloads'] += '<li><a href="%(markdown_baseurl)s/%(key)s_media/%(filename)s">%(title)s</a></li>' % {
				'markdown_baseurl': self.markdown_baseurl, 'key': self.key, 'filename': filename, 'title': dl['title']}

	# Copy the poster to the media directory.
	# Add it to md_filler and descriptor_content
	def _copy_poster(self):
		if self.poster:
			filename = os.path.basename(self.poster)
			shutil.copy(self.poster, os.path.join(self.media_dir, filename))
			self.descriptor_content['poster'] = filename
			self.md_filler['poster'] = "%(markdown_baseurl)s/%(key)s_media/%(filename)s" % {'markdown_baseurl': self.markdown_baseurl,
																					  'key': self.key,
																					  'filename': filename}

	# Write the descriptor files.
	# Should be the final action of build, since it requires md_filler and descriptor_content to be complete.
	def _write_descriptor(self):
		print "Writing descriptor file"

		if self.create_json:
			with open(os.path.join(self.target_dir, "%s.json" % self.key), "w+") as f:
				f.write(json.dumps(self.descriptor_content))

		if self.create_markdown:
			with open(os.path.join(self.target_dir, "%s.md" % self.key), "w+") as f:
				f.write("---\n")
				f.write('layout: screencast\n')
				f.write('key: "%(key)s"\n' % self.md_filler)
				f.write('title: "%(title)s"\n' % self.md_filler)
				f.write('description: "%(description)s"\n' % self.md_filler)
				f.write("sources: '%(sources)s'\n" % self.md_filler)
				f.write("tracks: '%(tracks)s'\n" % self.md_filler)
				if 'poster' in self.md_filler:
					f.write("poster: '%(poster)s'\n" % self.md_filler)
				f.write('---\n\n')
				if self.md_filler['downloads']:
					f.write("<br/>Used Files:\n")
				f.write("<ul>%(downloads)s</ul>\n" % self.md_filler)
		print "Done."


	# add a track to the screencast
	# kind: kind of the track
	# data: additional HTML5 data. Should not contain the keys src, default, kind
	# filename: absolute source file path of the track
	# default: if True, set track as default in player
	def add_track(self, kind, data, filename, default):
		sub = {'kind': kind, 'data': data, 'filename': filename, 'default': default}
		self.tracks.append(sub)

	# add a video format
	# extension: filename extension. should not start with ".". Example: "mp4"
	# mimetype: MIME type. example: "video/mp4"
	def add_video_format(self, extension, mimetype):
		self.video_formats.append({'mimetype': mimetype, 'extension': extension})

	# add a file for the viewer to download.
	# title: link title
	# filename: absolute path to the file
	def add_downloadable_content(self, title, filename):
		self.downloads.append({'title': title, 'filename': filename})

	# Set the poster file.
	# filename: absolute path of the source file
	def set_poster(self, filename):
		self.poster = filename

	# convert videos, copy files, etc.
	# i.e., create actual output.
	# This is the only public function which will do actual disk actions.
	def build(self):
		self._prepare_dir()
		self._create_video_formats()
		self._copy_tracks()
		self._copy_downloads()
		self._copy_poster()
		self._write_descriptor()


# build the screencast KEY to TARGET_DIR
# reads the descriptor file of the screencast,
#  then uses a ScreencastBuilder to build it.
def build_screencast(key, target_dir, markdown_baseurl, create_json):
	print "Creating '%s' at '%s'" % (key, target_dir)
	screencast_root = os.path.join(basedir, "sources", key)
	with open(os.path.join(screencast_root, "%s.json" % key), "r") as f:
		descriptor = json.loads(f.read())
	video_filename = os.path.join(screencast_root, descriptor['video_file'])
	builder = ScreencastBuilder(key=key, title=descriptor['title'], description=descriptor['description'],
								input_video_file=video_filename, target_dir=target_dir,
								markdown_baseurl=markdown_baseurl, create_json=create_json)
	for form in target_formats:
		builder.add_video_format(form['extension'], form['mimetype'])
	for dl in descriptor['downloads']:
		builder.add_downloadable_content(dl['title'], os.path.join(screencast_root, dl['filename']))
	for track in descriptor['tracks']:
		assert 'kind' in track and 'filename' in track
		kind = track['kind']
		filename = os.path.join(screencast_root, track['filename'])
		default = track['default'] if 'default' in track else False
		del track['kind']
		del track['filename']
		if 'default in track':
			del track['default']
		builder.add_track(kind, track, filename, default)
	if 'poster' in descriptor:
		builder.set_poster(os.path.join(screencast_root, descriptor['poster']))
	# TODO: add tracks
	builder.build()

# iterate over all screencasts in index.json, and build all of them individually using the build_screencast function
def create_all(target_dir, markdown_baseurl, create_json):
	with open(os.path.join(basedir, "sources", "index.json"), "r") as f:
		list = json.loads(f.read())
	for key in list:
		build_screencast(key, target_dir, markdown_baseurl, create_json)

# create index files (i.e., a list of all screencasts)
def create_index(target_dir, markdown_baseurl, create_json):
	print "Creating screencast list..."
	with open(os.path.join(basedir, "sources", "index.json"), "r") as f:
		list = json.loads(f.read())
	res = []
	for key in list:
		screencast_root = os.path.join(basedir, "sources", key)
		with open(os.path.join(screencast_root, "%s.json" % key), "r") as f:
			descriptor = json.loads(f.read())
		res.append({"key": key, "title": descriptor["title"], "description": descriptor["description"]})

	if create_json:
		with open(os.path.join(target_dir, "index.json"), "w+") as f:
			f.write(json.dumps(res))
	if markdown_baseurl:
		os.makedirs(os.path.join(target_dir, "_includes"))
		os.makedirs(os.path.join(target_dir, "_data"))
		shutil.copy(os.path.join(basedir, "markdown_deps", "index.html"), os.path.join(target_dir, "index.html"))
		with open(os.path.join(target_dir, "_data", "screencasts.yml"), "w+") as data:
			for scr in res:
				data.write("- key: %(key)s\n" % scr)
				data.write("  title: %(title)s\n" % scr)
				data.write("  description: %(description)s\n" % scr)
				data.write("  url: %(key)s\n" % {'key': scr['key']})
		with open(os.path.join(target_dir, "_includes", "screencast_list.html"), "w+") as incl:
			incl.write('<ul>')
			incl.write('{% for screencast in site.data.screencasts %}')
			incl.write(
				'<li><strong><a href="%(baseurl)s/{{screencast.url}}" >{{ screencast.title }}</a></strong><br/>' % {
					'baseurl': markdown_baseurl})
			incl.write(scr['description'])
			incl.write('{% endfor %}')
			incl.write('</ul>')
	print "Done."








# The following is to parse the command line arguments, and call the respective functions

def parseArgs():
	parser = argparse.ArgumentParser(prog="Screencasts Builder",
									 description="Converts video files, copies tracks and downloads, and puts them into a final format for the player.",
									 add_help=False)
	parser.add_argument('--help', action='help')
	parser.add_argument("--key", "-k", required=False, help="Screencast directory in sources")
	parser.add_argument("--targetdir", "-t", required=True,
						help="The target directory. The output will be created in a subfolder specified via --i")
	parser.add_argument("--create-index", "-c", help="Recreate the screencast index.", action="store_true",
						default=False)
	parser.add_argument("--all", "-a", help="Create all. Overwrites the -i option.", action="store_true", default=False)
	parser.add_argument("--markdown", "-m",
						help="Also create Markdown files for a jekyll project. Set media root directory for URL generating (needs the KEY_media and KEY.md files to be in this folder)",
						default=False)
	parser.add_argument("--json", "-j", help="Also create JSON files.", action="store_true", default=False)
	parser.add_argument("--debug", "-d", help="Debug mode: do not run video conversion.", action="store_true", default=False)
	options = parser.parse_args()
	return options


# interpret arguments to variables
opts = parseArgs()
debug = opts.debug
key = opts.key
target_dir = opts.targetdir
markdown_baseurl = (opts.markdown if opts.markdown.startswith("/") else "/" + opts.markdown) if opts.markdown else None
create_json = opts.json


# build screencasts
if opts.all:
	create_all(target_dir, markdown_baseurl, create_json)
elif key:
	build_screencast(key, target_dir, markdown_baseurl, create_json)
if (opts.all or key) and markdown_baseurl: #i.e. build at least one screencast, and have markdown output enabled
	os.makedirs(os.path.join(target_dir, "_layouts"))
	shutil.copy(os.path.join(basedir, "markdown_deps", "layout.html"),
				os.path.join(target_dir, "_layouts", "screencast.html"))


# create the index files
if opts.create_index:
	create_index(target_dir, markdown_baseurl, create_json)
