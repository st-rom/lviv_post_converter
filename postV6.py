#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Roman Stepaniuk
import argparse
import os
import pathlib
import shutil

from PIL import Image
from tkinter import Tk, filedialog


PIXELS = 600  # max width and height in pixels
CYRILLIC = ['а', 'б', 'в', 'г', 'ґ', 'д', 'е', 'є', 'ё',  # All symbols required to be changed
            'ж', 'з', 'и', 'і', 'ї', 'й', 'к', 'л', 'м',
            'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х',
            'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я', "'", '`', '"', ' ']
LATIN = ['a', 'b', 'v', 'h', 'g', 'd', 'e', 'je', 'jo',  # Symbols they are gonna be changed to
         'zh', 'z', 'y', 'i', 'ji', 'j', 'k', 'l', 'm',
         'n', 'o', 'p', 'r', 's', 't', 'u', 'f', 'h',
         'z', 'ch', 'sh', 'sh4', "", 'y', "", 'e', 'ju', 'ja', '', '', '', '_']


class FolderConverter:
    def __init__(self, **kwargs):
        self.dir_path = kwargs['dirname']
        self.vprint = print if kwargs['verbose'] else lambda *a, **k: None

    @staticmethod
    def cyrillic_to_latin(name):
        new_name = ''
        for letter in name:
            if letter.lower() in CYRILLIC:
                letter = LATIN[CYRILLIC.index(letter.lower())]
            new_name += letter
        return new_name

    def convert(self):
        if not self.dir_path or not os.path.isdir(self.dir_path):
            self.vprint('Wrong path "{}" selected. Try again'.format(self.dir_path))
            return 0
        new_dir = self.dir_path + '_copy'
        i = 1
        while os.path.exists(new_dir):
            new_dir = self.dir_path + '_copy({})'.format(i)
            i += 1
        self.vprint('Copying and converting files from {} to folder {}'.format(self.dir_path, new_dir))
        shutil.copytree(self.dir_path, new_dir)

        files = list(pathlib.Path(new_dir).rglob("*"))
        for file in files:
            try:
                image = Image.open(file)
                self.vprint(f"Original size of {file} : {image.size}")  # 5464x3640

                image.thumbnail((PIXELS, PIXELS), Image.Resampling.LANCZOS)
                self.vprint(f"New size : {image.size}")  # 5464x3640
                new_name = self.cyrillic_to_latin(str(file))
                image.save(new_name, "JPEG")
                if new_name != str(file):
                    os.remove(file)
            except IOError:
                pass
        self.vprint('Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a copy of selected directory with all files renamed from '
                                                 f'cyrillic alphabet to latin. Also, resizes images so that'
                                                 f' either dimension is not higher than {PIXELS} pixels.')
    parser.add_argument('dirname', help="path to the directory, which should be converted. If you will not enter it,"
                                        " the path selection window will pop up", nargs='?', const='')
    parser.add_argument('--verbose', action='store_true', help="increase output verbosity")

    args = parser.parse_args()
    if not args.dirname:
        root = Tk()
        root.withdraw()

        args.dirname = filedialog.askdirectory()
    fc = FolderConverter(**vars(args))
    fc.convert()
