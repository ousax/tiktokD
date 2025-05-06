import os
import sys
import random 
import string
import argparse
from requests import get, post, ConnectionError, ConnectTimeout
from bs4 import BeautifulSoup as bs
from termcolor import colored, cprint
parser = argparse.ArgumentParser()
parser.add_argument("-u", metavar="Username", help="The username, tiktok handler", required=True, type=str)
args = parser.parse_args()
user = args.u
profile = "https://urlebird.com/fr/user/"
cdir = os.getcwd() #current directory
class TikTokUser:
    """
    This is a simple script to scrap video from tiktok using urlebird.com
    still needs improvements 
    still need to fix the `load more` videos
    """
    def _Start():
        try:
            global profile, user, all_media 
            all_media = []
            try:
                os.mkdir("TikTok_")
            except FileExistsError:
                pass
            try:
                os.chdir("TikTok_")
            except:
                cprint(f"Unbale to change the directory to TikTok_", "red")
                exit()
            headers = {
                "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language":"fr"
            }
            reqUserProfile = get(f"{profile}{user}/", headers=headers, timeout=5)
            if reqUserProfile.status_code == 200:
                Parse_Profile = bs(reqUserProfile.text, "html.parser")
                find_info3 = Parse_Profile.find_all("div", {"class":"info3"}) # div class=infos3
                if len(find_info3) != 0:
                    try:
                        os.mkdir(user)
                        cprint(f"{user} created successfully", "green")
                        try:
                            os.chdir(user)
                            cprint(f"{user} is the current directory", "blue")
                        except Exception as cantChdirUser:
                            cprint(f"CantChdirUser: {cantChdirUser}", "red")
                    except FileExistsError:
                        pass
                    except Exception as CnCreateUF:
                        cprint(f"Cant create the folder name CnCreateUF: {CnCreateUF}", "red")
                    for x, infos in enumerate(find_info3):
                        find_a = infos.find_all('a')
                        title, href = find_a[-1].text.replace(" ", "_"), find_a[-1].attrs['href']
                        all_media.append((title, href))
                    def LoadMore(): # load more pages if they exist
                        load_more = Parse_Profile.find_all("button", {"id":"load_more"}) # button
                        if len(load_more) != 0:
                            for items in load_more:
                                if items.attrs == 'disabled':
                                    break
                                else:
                                    print(items)
                                    
                                    Headers = {
                                        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
                                        #"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                                        "Origin":"https://urlebird.com",
                                        "Referer":f"https://urlebird.com/user/{user}/"
                                    }
                                    data = {
                                        "user_id":items.attrs['data-user-id'],
                                        "sec_uid":items.attrs['data-sec-uid'],
                                        "cursor":items.attrs['data-cursor'],
                                        "lang":"",
                                        "x":items.attrs['data-x'],
                                        "page":items.attrs['data-page']
                                    }
                                    reqAjaxMoreMedia = post("https://urlebird.com/ajax/", data=data, headers=Headers, timeout=5)
                                    cprint(("Status code for the ajax request", reqAjaxMoreMedia.status_code), "yellow")
                                    cprint(reqAjaxMoreMedia.headers, "green")
                    #LoadMore() # don't uncomment this one now. and fix it later so it can load more media for the given user
                else:
                    cprint(f"Looks like {user} has no media", "yellow")
                    exit()
            else:
                cprint(f"The username {user} doesn't exist", "red") 
            def DownloadMedia(title, href):
                ntitle = f"{title}_{''.join(random.sample(string.ascii_letters+string.digits, 5))}.mp4"
                reqHref = get(href, headers=headers, timeout=5)
                if reqHref.status_code == 200:
                    parseHref = bs(reqHref.text, "html.parser")
                    find_video = parseHref.find("video")['src']
                    def Downloader(f, n):
                        Chunk_Size = (5 * (1024*1024))
                        with get(f, stream=True) as respose:
                            try:
                                respose.raise_for_status()
                                with open(n, "wb") as file:
                                    for chunk in respose.iter_content(Chunk_Size):
                                        file.write(chunk)
                                    cprint(f'{n} downloaded successfully.')
                            except Exception as httpE:
                                cprint(f"httpE: {httpE}", "red")
                                cprint(f"Unable to download: {n}", "yellow")
                    if len(find_video) != 0:
                        cprint(f"Title: {ntitle}", "magenta")
                        Downloader(find_video, ntitle)
            # downloading section 
            for item_id, items in enumerate(all_media):
                cprint(item_id, "blue")
                DownloadMedia(items[0], items[1]) # works fine
        except KeyboardInterrupt:
            cprint("\nCanceled by the user.", "light_yellow")
            exit()
        except ConnectionError as eHttp:
            cprint(eHttp, "red")
            exit()
        except ConnectTimeout as cTout:
            cprint(cTout, "red")
            exit(0)
        except Exception as A_err:
            cprint(A_err, "red") # another error
            exit()
    try:
        os.chdir(cdir)
    except:
        pass
if "," in user:
    users = [u.replace(" ", "") for u in user.split(',')]
    for user in users:
        TikTokUser._Start()
        try:
            os.chdir(cdir)
        except Exception as CantChdirUsers:
            cprint(f"CantChdirUsers: {CantChdirUsers}", "red")
else:
    print(user, "single account")
    TikTokUser._Start()
