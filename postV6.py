#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Roman Stepaniuk
import argparse
import os
import pathlib
import shutil

from PIL import Image, UnidentifiedImageError
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
    """
    Class for image files in the folder
    """
    def __init__(self, **kwargs):
        self.dir_path = kwargs['dirname']  # name of the directory that will be copied
        self.vprint = print if kwargs['verbose'] else lambda *a, **k: None  # prints only if --verbose was passed

    @staticmethod
    def cyrillic_to_latin(path_string: str) -> str:
        """
        Replaces cyrillic characters in string with latin ones
        :param path_string: str, path to the file
        :return: str, updated path to the file
        """
        names = path_string.split(os.sep)
        name = names.pop(-1)  # retrieving the name of file itself
        new_name = ''
        for letter in name:  # renaming it
            if letter.lower() in CYRILLIC:
                letter = LATIN[CYRILLIC.index(letter.lower())]
            new_name += letter
        names.append(new_name)
        new_path = os.path.join(*names)  # putting path back together
        if path_string.startswith(os.sep):  # add slash at the start if necessary
            new_path = os.sep + new_path
        return new_path

    def convert(self):
        if not self.dir_path or not os.path.isdir(self.dir_path):
            print('Wrong path "{}" selected. Try again'.format(self.dir_path))
            return
        if sum(f.stat().st_size for f in pathlib.Path(self.dir_path).glob('**/*') if f.is_file()) > 1000000000:
            print('Selected directory is too big')  # if directory size is bigger than 1Gb we abort
            return
        new_dir = self.dir_path + '_copy'
        i = 1
        while os.path.exists(new_dir):  # trying to find unique name for copied dir
            new_dir = self.dir_path + '_copy({})'.format(i)
            i += 1
        self.vprint('Copying and converting files from {} to folder {}'.format(self.dir_path, new_dir))
        shutil.copytree(self.dir_path, new_dir)  # copies whole directory recursively

        files = list(pathlib.Path(new_dir).rglob("*"))  # selects all the files in new directory
        for file in files:  # iterating through all files in copied dir
            try:
                image = Image.open(file)  # trying to read an image file
                self.vprint(f"Original size of {file}: {image.size}")

                image.thumbnail((PIXELS, PIXELS), Image.Resampling.LANCZOS)  # resizing image with same aspect ratio
                new_name = self.cyrillic_to_latin(str(file))  # renames the file if necessary
                image.save(new_name)  # creating new image
                self.vprint(f"New size of {new_name}: {image.size}")
                if new_name != str(file):  # if new name differs from the old we should delete old file(to avoid copies)
                    os.remove(file)
            except (UnidentifiedImageError, IsADirectoryError):  # ignoring non-image files
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
    if not args.dirname:  # if directory was not passed through args, you will have to choose it manually
        root = Tk()
        root.withdraw()

        args.dirname = filedialog.askdirectory()
    args.dirname = args.dirname.rstrip('\\/')  # removing trailing slashes
    fc = FolderConverter(**vars(args))
    fc.convert()
