import datetime
import json
import os
import platform
import sys
from os import rename
from pathlib import Path
from moviepy.editor import VideoFileClip
import filetype
import requests

import convert
from convert import convertFile
try:
    from winreg import *
except:
    pass


def checkifexist(folder, name):
    return Path(folder + '/' + name).exists()


def downloadurl(url, count, name, folder):
    name += '.gif' if not '.gif' in name else ''
    if checkifexist(folder, name):
        name = str(count) + '_duplicate_' + name
    if url.split('.')[-1] != 'gif':
        url += '.gif'
    r = requests.get(url)
    print("\t status (", r.status_code, ')')
    if r.status_code in range(200, 300):
        file = open(folder + '/' + name, "wb")
        file.write(r.content)
        file.close()
        print(f'\t downloaded {name} in {folder}')
        return 1
    return 0


def downloadsrc(src, count, name, folder):
    if checkifexist(folder, name):
        name = str(count) + '_duplicate_' + name
    r = requests.get(src, allow_redirects=True)
    print("\t status (", r.status_code, ')')
    if r.status_code in range(200, 300):
        file = open(folder + '/' + name, "wb")
        file.write(r.content)
        file.close()
        print(f'\t downloaded {name} in {folder}')
        return 1
    return 0


def checkfolder(path):
    from os import walk

    _, _, filenames = next(walk(path))
    for file in filenames:
        fullpath = path + '/' + file
        guess = filetype.guess(fullpath)
        if guess is None:
            print(f'\033[93m\033[1mcouldn\'t process {path}/{file} you ended up with a binary file')
        elif file[len(file)-len(guess.extension)-1:] != '.'+guess.extension:
            rename(fullpath, fullpath + '.' + guess.extension)
            if not guess.mime.split('/')[0] == 'video':
                print(f'renamed {path}/{file} ➡ {path}/{file}.{guess.extension}')
            else:
                convertFile(f'{fullpath}.{guess.extension}',convert.TargetFormat.GIF)
                os.remove(f'{fullpath}.{guess.extension}')



def finddownloaddirectory():
    folder = None
    if len(sys.argv) == 2:
        folder = sys.argv[1]
    if platform.system() == 'Windows':
        with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
            folder = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
    else:
        folder = str(Path.home()) + '/Downloads'
    if folder:
        return folder
    else:
        raise NameError('Path do HOME Download folder not found')


def main(giffavs, folder):
    errorcount = 0
    value = json.loads(giffavs)["_state"]["favorites"]
    print(f'found {len(value)} faved gifs')
    for count, el in enumerate(value):
        url = str(el["url"])
        src = (el["src"])
        print(f'\n➡{count + 1}: {url}')
        name = url.split('/')[-1].split('?')[-2] if '?' in url.split('/')[-1] else url.split('/')[-1]
        if not downloadurl(url, count, name, folder):
            print(f'\t\033[93m\033[1mCouldn\'t download {name}\n\ttrying src method but you might end up with a non gif file :\033[0m')
            if not downloadsrc(src, count, name, folder):
                print(
                    f'\t\033[91m\033[1mAn error occurred while downloading {name} try manually at source:\033[0m {el["src"]}')
                errorcount += 1
    if errorcount > 0:
        checkfolder(folder)
    return errorcount


if __name__ == '__main__':
    now = datetime.datetime.now()

    # put your JSON GIFFavorite store here
    data = ''
    #
    
    folder = finddownloaddirectory()

    folder += '/DiscordFavoriteGif(' + now.strftime("%d") + '.' + now.strftime("%b") + '.' + now.strftime(
        "%Y") + '_' + now.strftime("%H") + now.strftime("%M") + now.strftime("%S") + ')'

    Path(folder).mkdir(parents=True, exist_ok=True)

    result = main(data, folder)

    print('script ended with ' + str(result) + ' error(s)')
