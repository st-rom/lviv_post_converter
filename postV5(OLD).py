#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2018, Roman Stepaniuk
# GNU General Public License Version 6
# переіменувати програму magick convert в convert-im з пакету ImageMagic і magick identify в identify
import os
import sys
import shutil


########################################################################
######################## User Parameters ########################
width = '600'  # Required width in pixels
height = '600'	 # Required height in pixels
extension = ['jpg', 'JPG', 'JPEG','jpeg', 'png', 'gif']  # Extensions
kir = ['а', 'б', 'в', 'г', 'ґ', 'д', 'е', 'є', 'ё',  # All symbols required to be changed
		'ж', 'з', 'и', 'і', 'ї', 'й', 'к', 'л', 'м',
		'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х',
		'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', "'", '`', '"', ' ']
lat = ['a', 'b', 'v', 'h', 'g', 'd', 'e', 'je', 'jo',  # Symbols they are gonna be changed to
		'zh', 'z', 'y', 'i', 'ji', 'j', 'k', 'l', 'm',
		'n', 'o', 'p', 'r', 's', 't', 'u', 'f', 'h',
		'z', 'ch', 'sh', 'sh4', "", 'y', "", 'e', 'ju', 'ja', '', '', '', '_']
#################### End of User Parameters #####################
########################################################################


def rescaler(file, src, dest):
	try:
		str_com = 'identify -format "%[width]x%[height]" "{file}"'.format(file=src) #image resolution
		p = os.popen(str_com)
		line = str(p.readlines()[0])
	except IndexError:
		str_com = 'magick identify -format "%[width]x%[height]" "{file}"'.format(file=src) #image resolution if using another lib 
		p = os.popen(str_com)
		line = str(p.readlines()[0])
		
	img_res = line.split('x')
	printif('Image resolution %s:' % (file)) 
	file_w = int(img_res[0])
	file_h = int(img_res[1])
	printif('Width => %s' % (file_w))
	printif('Height => %s' % (file_h))

	if (file_w >= file_h and file_w <= int(width)) or (file_w <= file_h and file_h <= int(height)):  # if image's size fits requirements 
		printif("Image's resolution wasn't changed since it already in required resolution")
		shutil.copy(src, dest)
	elif file_w >= file_h and file_w >= int(width): # if width of image is bigger than height and width is bigger than required
		try:
			str_com = 'convert-im "%s" -resize %sx "%s"' % (src, width, dest)
			p = os.popen(str_com)
			line_try = str(p.readlines()[0])
		except IndexError:
			str_com = 'magick convert "%s" -resize %sx "%s"' % (src, width, dest)
			os.popen(str_com)
		printif("Image's width was converted to 600 so now image has fits requirements")
	else:  # if height of image is bigger than width and height is bigger than required
		try:
			str_com = 'convert-im "%s" -resize x%s "%s"' % (src, height, dest)
			p = os.popen(str_com)
			line_try = str(p.readlines()[0])
		except IndexError:
			str_com = 'magick convert "%s" -resize x%s "%s"' % (src, height, dest)
			os.popen(str_com)
		printif("Image's height was converted to 600 so now image has fits requirements")


def copynrename(src, dest):
	files = os.listdir(src)
	for file in files:
		change = False
		fine_ext = False
		for e in extension:
			if file.endswith(e):
				fine_ext = True
		r_file = list(file)
		for k in range(len(r_file)):
			if r_file[k].lower() in kir and fine_ext:
				r_file[k] = lat[kir.index(r_file[k].lower())]
				change = True
		if change:
			new_name = ''.join(r_file)
		else:
			new_name = file
		if not os.path.isdir(dest + '/' + file) and os.path.isdir(src + '/' + file):
			os.mkdir(dest + '/' + file)
			copynrename(src + '/' + file, dest + '/' + file)
		elif os.path.isdir(src + '/' + file):
			copynrename(src + '/' + file, dest + '/' + file)
		elif os.path.isfile(src + '/' + file) and fine_ext:
			if change:
				printif('\n\n' + file + ' is copied to ' + dest + ' and renamed to ' + new_name)
			else:
				printif('\n\n' + file + ' is copied to ' + dest + ' and not renamed since image name fits requirements')
			rescaler(file, src + '/' + file, dest + '/' + new_name)
		elif os.path.isfile(src + '/' + file) and file.endswith(".indd"):
			shutil.copy(src + '/' + file, copy_dir)


def printif(strng):
	if prt:
		try:
			print(strng)
		except UnicodeEncodeError:
			print('Cannot print letter "i"... Update is coming in near future')


if len(sys.argv) == 1:
	print("Where are my arguments, dude?\n-s    start program in current directory\nor just type path"
		  " to directory you want to run this program in\n-p    as second argument for printing what program is doing")
	sys.exit()
elif len(sys.argv) >= 2:
	if sys.argv[1] == '-s':
		img_dir = os.getcwd()
	else:
		try:
			if '\\' in sys.argv[1] or '/' in sys.argv[1]:
				img_dir = sys.argv[1]
			else:
				img_dir = os.getcwd() + '/' + sys.argv[1]
			os.chdir(img_dir)
		except:
			print('Wrong path to the directory with images')
			sys.exit()

if '-h' in sys.argv:
	print('No one can help you now my friend...')
prt = True if '-p' in sys.argv else False
img_dir = list(img_dir)
for i in range(len(img_dir)):
	if img_dir[i] == '\\':
		img_dir[i] = '/'
img_dir = ''.join(img_dir)

copy_dir = img_dir + '_copy'
if not os.path.isdir(copy_dir):
	os.mkdir(copy_dir)
else:
	print('Error! Mayday! SOS!\n' + copy_dir + ' already exists!')
	sys.exit()
copynrename(img_dir, copy_dir)
