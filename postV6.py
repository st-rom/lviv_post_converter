#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Roman Stepaniuk
import argparse
import os
import pathlib
import shutil

from PIL import Image, UnidentifiedImageError
from tkinter import Tk, filedialog, messagebox


PIXELS = 600  # max width and height in pixels
CYR_TO_LAT_DICT = {  # All the symbols required to be changed
    'А': 'A', 'а': 'a',
    'Б': 'B', 'б': 'b',
    'В': 'V', 'в': 'v',
    'Г': 'H', 'г': 'h',
    'Ґ': 'G', 'ґ': 'g',
    'Д': 'D', 'д': 'd',
    'Е': 'E', 'е': 'e',
    'Є': 'Ye', 'є': 'ie',
    'Ж': 'Zh', 'ж': 'zh',
    'З': 'Z', 'з': 'z',
    'И': 'Y', 'и': 'y',
    'І': 'I', 'і': 'i',
    'Ї': 'Yi', 'ї': 'i',
    'Й': 'Y', 'й': 'i',
    'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm',
    'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o',
    'П': 'P', 'п': 'p',
    'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't',
    'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f',
    'Х': 'Kh', 'х': 'kh',
    'Ц': 'Ts', 'ц': 'ts',
    'Ч': 'Ch', 'ч': 'ch',
    'Ш': 'Sh', 'ш': 'sh',
    'Щ': 'Shch', 'щ': 'shch',
    'Ь': '', 'ь': '',
    'Ю': 'Yu', 'ю': 'iu',
    'Я': 'Ya', 'я': 'ia',
    'Ъ': '', 'ъ': '',
    'Ы': 'Y', 'ы': 'y',
    'Ё': 'Yo', 'ё': 'io',
    'Э': 'E', 'э': 'e',
    "'": '', '`': '',
    '"': '', ' ': '_'
}


class FolderConverter:
    """
    Class for image files in the folder
    """
    def __init__(self, windowed: bool, **kwargs):
        """
        Initiates class variables
        :param windowed: bool, if True, the program has GUI and will show message boxes
        :param dir_path: str, path to the directory that will be processed
        :param vprint: bool, if True, prints information on every important step
        """
        self.windowed = windowed  # is in tkinter window
        self.dir_path = kwargs['dirname']  # name of the directory that will be copied
        self.vprint = print if kwargs['verbose'] else lambda *a, **k: None  # prints only if --verbose was passed

    def cyrillic_to_latin(self, path_string: str) -> str:
        """
        Replaces cyrillic characters in string with latin ones
        :param path_string: str, path to the file
        :return: str, updated path to the file
        """
        names = path_string.split(os.sep)
        name = names.pop(-1)  # retrieving the name of file itself
        new_name = ''
        for letter in name:  # renaming it
            new_name += CYR_TO_LAT_DICT.get(letter, letter)
        names.append(new_name)
        new_path = os.sep.join(names)  # putting path back together
        if path_string.startswith(os.sep):  # add slash at the start if necessary
            new_path = os.sep + new_path
        self.vprint(f"Working on {new_path}")
        return new_path

    def convert(self):
        """
        Creates new copied folder and replaces old image files with new updated ones
        """
        if not self.dir_path or not os.path.isdir(self.dir_path):
            if self.windowed:
                messagebox.showerror('Error',  'Wrong path "{}" selected. Try again'.format(self.dir_path))
            print('Wrong path "{}" selected. Try again'.format(self.dir_path))
            return
        if sum(f.stat().st_size for f in pathlib.Path(self.dir_path).glob('**/*') if f.is_file()) > 1000000000:
            if self.windowed:
                messagebox.showerror('Error',  'Selected directory is too big (max 1Gb)')
            print('Selected directory is too big (max 1 Gb)')  # if directory size is bigger than 1Gb we abort
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
            except (UnidentifiedImageError, IsADirectoryError, PermissionError):  # ignoring non-image files
                pass
            except Exception as e:
                if self.windowed:  # error window if error
                    messagebox.showerror('Error',  str(e))
                shutil.rmtree(new_dir)  # remove copied folder
                raise e
        if self.windowed:  # confirmation that operation was successful
            messagebox.showinfo('Success', 'Успіх! Вдалої та легкої роботи на номером!')
        self.vprint('Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creates a copy of selected directory with all files renamed from '
                                                 f'cyrillic alphabet to latin. Also, resizes images so that'
                                                 f' either dimension is not higher than {PIXELS} pixels.')
    parser.add_argument('dirname', help="path to the directory, which should be converted. If you will not enter it,"
                                        " the path selection window will pop up", nargs='?', const='')
    parser.add_argument('--verbose', action='store_true', help="increase output verbosity")

    args = parser.parse_args()
    is_windowed = False
    if not args.dirname:  # if directory was not passed through args, you will have to choose it manually
        is_windowed = True  # from now on message boxes are activated
        root = Tk()
        root.withdraw()

        args.dirname = filedialog.askdirectory()
    args.dirname = args.dirname.rstrip(os.sep)  # removing trailing slashes
    fc = FolderConverter(windowed=is_windowed, **vars(args))
    fc.convert()
