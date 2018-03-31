from __future__ import print_function
from moviepy.editor import *
from collections import defaultdict
import os,sys#,string
try:
	from xml.etree import cElementTree as et
except ImportError:
	from xml.etree import ElementTree as et


"""
This script outputs (subtitled) video clips (.mp4) from annotations made in ELAN, using moviepy
"""

def get_times(root):
	"""
	Finds the time codes in the .eaf file and returns a dictionary
	"""
	times = {}
	for timeslot in root.iter("TIME_ORDER"):
		for slot in timeslot:
			ts = slot.attrib["TIME_SLOT_ID"]
			ms = slot.attrib["TIME_VALUE"]
			times[ts] = int(ms)
	return times

def get_clips(root,tiername):
	"""
	Parses .eaf and looks for clips to subtitle. Returns a defaultdict of clips
	"""
	times = get_times(root)
	clips = defaultdict(list)
	videos = []
	for info in root.iter("HEADER"):
		for media in info.iter("MEDIA_DESCRIPTOR"):
			v = media.attrib["RELATIVE_MEDIA_URL"].split("/")[-1]
			videos.append(v)
	for tier in root.iter("TIER"):
		if tier.attrib["TIER_ID"].startswith(tiername):
			video = tier.attrib["TIER_ID"].split("_")[-1]
			for v in videos:
				if video in v:
					videofile = v
			for cell in tier.iter('ALIGNABLE_ANNOTATION'):
				t1 = cell.attrib["TIME_SLOT_REF1"]
				t2 = cell.attrib["TIME_SLOT_REF2"]
				text = cell.find("ANNOTATION_VALUE").text
				clips[videofile].append((times[t1],times[t2],text))
	return clips

def get_texts(texts,dur):
	"""
	Creates individual TextClip objects in case of longer sequences and returns objects in a list
	"""
	subs = []
	for n,text in enumerate(texts):
		subs.append(TextClip(text,font="Georgia-Bold",fontsize=20,color="white",bg_color="black").set_pos(("center","bottom")).set_start(n*dur+n*0.05).set_duration(dur-(n*0.05)))
	return subs

def make_video(videofile,clip,num,speed):
	"""
	Creates a video file with subtitles of the clip sequence
	"""
	t1 = clip[0]/1000
	t2 = clip[1]/1000
	texts = clip[2].split("//")
	dur = (t2-t1)/len(texts)
	short_texts = []
	for text in texts:
		if len(text)>25:
			split = text.split(" ")
			mod = []
			for n in range(len(split)):
				if n == round(len(split)/2):
					mod.append(split[n]+"\n")
				else:
					mod.append(split[n])
			short_texts.append(" ".join(mod))
		else:
			short_texts = texts
	v = VideoFileClip(videofile).subclip(t1,t2)
	subs = get_texts(short_texts,dur)
	video = CompositeVideoClip([v]+subs).speedx(speed/100)
	clipfile = videofile.split(".")[0]+"_subtitles_"+str(num+1)+".mp4"
	video.write_videofile(clipfile)

def make_all_clips(tiername=None,speed=None):
	"""
	Iterates through .eaf files in a directory and looks for clips to subtitles. Creates videos when found
	"""
	if tiername is None:
		tiername = "make_subtitles"
	if speed is None:
		speed = 100
	for f in os.listdir():
		if f.endswith(".eaf"):
			clips = get_clips(et.parse(f).getroot(),tiername)
			print(">>> Searching clips in file: ",f)
			for v in clips:
				for num,c in enumerate(clips[v]):
					print("\n>>> Processing clip number",num+1)
					make_video(v,c,num,speed)

def main():
	"""
	Main function looks for arguments <tiername> and <speed>. If not found, defaults are given
	"""
	if len(sys.argv)>1:
		tiername = None
		speed = None
		for a in sys.argv[1:]:
			if a.isdigit():
				speed = int(a)
			else:
				tiername = a
		make_all_clips(tiername,speed)
	else:
		make_all_clips()

if __name__=="__main__":
	main()
