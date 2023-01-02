This script copies a selected directory, renames all image files with cyrillic names in it and resizes those images to 600px max.

Make sure you have **python3.x** installed, as well as **pip** and **tk**(on Windows) 

To generate .exe file on Windows run the following code in downloaded project directory:
```
pip install virtualenv
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
pyinstaller --onefile -w --icon logofb.ico --name LvivPostConverter postV6.py
```
After this you'll have .exe file in `dist` folder, which you can use without worrying about code anymore.
