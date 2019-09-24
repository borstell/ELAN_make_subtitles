from __future__ import print_function
from moviepy.editor import *
from collections import defaultdict
import os,sys,argparse,cv2
from PIL import Image,ImageDraw
import numpy as np
try:
	from xml.etree import cElementTree as et
except ImportError:
	from xml.etree import ElementTree as et


"""
This script outputs (subtitled) video clips (.mp4) from annotations made in ELAN, using moviepy
"""

def vid(vid):
	return vid.split(".")[0]+".mp4"

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

def get_texts(texts,dur,w):
	"""
	Creates individual TextClip objects in case of longer sequences and returns objects in a list
	"""
	subs = []
	for n,text in enumerate(texts):
		subs.append(TextClip(text,font="Arial-Bold",fontsize=w/30,color="white",bg_color="black").set_pos(("center","bottom")).set_start(n*dur+n*0.05).set_duration(dur-(n*0.05)))
	return subs

def get_glosses(root,tiername):
	times = get_times(root)
	clips = get_clips(root,tiername)
	segments = defaultdict(list)
	for clip in clips:
		clipmp4 = vid(clip)
		for i,seg in enumerate(clips[clip]):
			start = seg[0]
			end = seg[1]
			for tier in root.iter("TIER"):
				if tier.attrib["TIER_ID"] == "Glosa_DH S2":
					for cell in tier.iter("ALIGNABLE_ANNOTATION"):
						t1 = times[cell.attrib["TIME_SLOT_REF1"]]
						t2 = times[cell.attrib["TIME_SLOT_REF2"]]
						if t1 >= start and t1 <= end:
							gloss = cell.find("ANNOTATION_VALUE").text
							segments[i].append((t1,t2,gloss,clipmp4))
	return segments

def make_stills(root,tiername):
	segments = get_glosses(root,tiername)
	for seg in segments:
		imgs = []
		vidcap = cv2.VideoCapture(segments[seg][0][-1])
		success, image = vidcap.read()
		success = True
		for gloss in segments[seg]:
			im1 = cv2.VideoCapture(gloss[-1])
			im1.set(cv2.CAP_PROP_POS_FRAMES,(gloss[0]/1000*25))
			success,image1 = im1.read()
			w = int(im1.get(cv2.CAP_PROP_FRAME_WIDTH))
			h = int(im1.get(cv2.CAP_PROP_FRAME_HEIGHT))
			im2 = cv2.VideoCapture(gloss[-1])
			im2.set(cv2.CAP_PROP_POS_FRAMES,(gloss[1]/1000*25))
			success,image2 = im2.read()
			con = cv2.hconcat([image1,image2])
			con2 = cv2.putText(con,gloss[2],(int(w*.7),int(.9*h)),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2)
			#con2 = ImageDraw.Draw(con)
			#con2 = con2.text((50,50),gloss[2],fill="white")
			#success,con2 = con2.read()
			imgs.append(con2)
		#vis = np.concatenate(tuple(imgs), axis=1)
		#vis = cv2.hconcat(imgs[:2])
		vis = np.hstack(imgs)
		cv2.imwrite("sequence_"+str(seg+1)+".jpg", vis)

def make_video(videofile,clip,num,speed):
	"""
	Creates a video file with subtitles of the clip sequence
	"""
	t1 = clip[0]/1000
	t2 = clip[1]/1000
	texts = clip[2].split("//")
	dur = (t2-t1)/len(texts)
	v = VideoFileClip(videofile).subclip(t1,t2)
	w = v.w
	short_texts = []
	for text in texts:
		if len(text)>w/20:
			split = text.split(" ")
			mod = []
			for n in range(len(split)):
				if n == round(len(split)/2)-1:
					mod.append(split[n]+"\n")
				else:
					mod.append(split[n])
			short_texts.append(" ".join(mod))
		else:
			short_texts = texts
	subs = get_texts(short_texts,dur,w)
	video = CompositeVideoClip([v]+subs).speedx(speed/100)
	clipfile = videofile.split(".")[0]+"_subtitles_"+str(num+1)+".mp4"
	video.write_videofile(clipfile,temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")

def make_all_clips(tiername,speed):
	"""
	Iterates through .eaf files in a directory and looks for clips to subtitles. Creates videos when found
	"""
	for f in os.listdir():
		if f.endswith(".eaf"):
			#segs = get_glosses(et.parse(f).getroot(),"make_subtitles_S002")
			make_stills(et.parse(f).getroot(),"make_subtitles_S002")
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
	parser = argparse.ArgumentParser()
	parser.add_argument("-t", "--tiername", help="Name of tier", type=str, default="make_subtitles")
	parser.add_argument("-s", "--speed", help="Speed of output video", type=int, default=100)
	args = parser.parse_args()
	make_all_clips(args.tiername,args.speed)

if __name__=="__main__":
	main()
