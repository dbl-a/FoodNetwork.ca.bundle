# PMS plugin framework
import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/foodnetworkca"

NAME = L('Title')

ART           = 'art-default.png'
ICON          = 'icon-default.jpg'

FOOD_SHOW_LIST = "http://www.foodnetwork.ca/About/sitemap.html"

FEED_LIST    = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getCategoryList?callback=jsonp1292029442754&field=ID&field=depth&field=hasReleases&field=fullTitle&PID=6yC6lGVHaVA8oWSm1F9PaIYc9tOTzDqY&query=CustomText|PlayerTag|z/FOODNET%20Player%20-%20Video%20Centre&field=title&field=fullTitle&field=thumbnailURL&customField=SortCriteria&customField=DisplayTitle"

FEEDS_LIST    = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=6yC6lGVHaVA8oWSm1F9PaIYc9tOTzDqY&startIndex=1&endIndex=500&query=contentCustomText|Show|%s&sortField=airdate&sortDescending=true&field=airdate&field=author&field=description&field=length&field=PID&field=thumbnailURL&field=title&CustomField=DisplayTitle"

#http://release.theplatform.com/content.select?pid=r_Nc23fN5bjSVKeXl3fY8ORXY2K0JC_e&UserName=Unknown&Tracking=True&Portal=FoodTV&TrackBrowser=True&TrackLocation=True

DIRECT_FEED = "http://release.theplatform.com/content.select?format=SMIL&pid=%s&UserName=Unknown&Embedded=True&Portal=FoodTV&TrackBrowser=True&Tracking=True&TrackLocation=True"

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)


####################################################################################################
def MainMenu():
    dir = MediaContainer(viewGroup="List")
    dir.Append(Function(DirectoryItem(ShowsPage, "Shows"), pageUrl = FOOD_SHOW_LIST, showtime='//div[@id="li_container4"]/ul/li'))
    #dir.Append(Function(DirectoryItem(ShowsPage, "Shows G-L"), pageUrl = HGTV_SHOW_LIST, showtime='//ul[@id="GL"]/li/a'))
    #dir.Append(Function(DirectoryItem(ShowsPage, "Shows M-Z"), pageUrl = HGTV_SHOW_LIST, showtime='//ul[@id="MZ"]/li/a'))
    return dir
    
####################################################################################################
def VideoPlayer(sender, pid):
    videosmil = HTTP.Request(DIRECT_FEED % pid)
    player = videosmil.split("ref src")
    player = player[2].split('"')
    if ".mp4" in player[1]:
        player = player[1].replace(".mp4", "")
        clip = player.split(";")
        clip = "mp4:" + clip[4]
    else:
        player = player[1].replace(".flv", "")
        clip = player.split(";")
        clip = clip[4]
    #Log(player)
    #Log(clip)
    return Redirect(RTMPVideoItem(player, clip))
    
####################################################################################################
def VideosPage(sender, showname):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    pageUrl = FEEDS_LIST % (showname)
    feeds = JSON.ObjectFromURL(pageUrl)
    for item in feeds['items']:
        title = item['title']
        pid = item['PID']
        summary =  item['description'].replace('In Full:', '')
        duration = item['length']
        thumb = item['thumbnailURL']
        airdate = int(item['airdate'])/1000
        subtitle = 'Originally Aired: ' + datetime.datetime.fromtimestamp(airdate).strftime('%a %b %d, %Y')
        dir.Append(Function(VideoItem(VideoPlayer, title=title, subtitle=subtitle, summary=summary, thumb=thumb, duration=duration), pid=pid))
    return dir
    
#def ClipsPage(sender, showname):
    #dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    #dir.Append(Function(DirectoryItem(VideosPage, "Full Episodes"), clips="episode", showname=showname))
    #dir.Append(Function(DirectoryItem(VideosPage, "Clips"), clips="", showname=showname))
    #return dir
    
####################################################################################################
def ShowsPage(sender, pageUrl, showtime):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")
    content = XML.ElementFromURL(pageUrl, True).xpath('//div[@class="CorporateContent DotsGreyBottom"][1]//a')
    for item in content:
        title = item.text
        Log(title)
        image = "" #item.xpath('.//img')[0].get('src')
        thumb = image.split("?")[0]
        Log(thumb)
        showname = title
        if "American Dad" in showname or "Entertainment Tonight" in showname or "The Simpsons" in showname:
            continue             ### NO VIDEOS FOR THESE SHOWS
        showname = showname.replace(' ', '%20').replace('&', '%26')  ### FORMATTING FIX
        Log(showname)
        dir.Append(Function(DirectoryItem(VideosPage, title, thumb=thumb), showname=showname))
    return dir