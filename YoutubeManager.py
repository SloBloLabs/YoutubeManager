# -*- coding: utf-8 -*-

# Useful links:
# https://console.cloud.google.com/home/dashboard
# https://console.cloud.google.com/iam-admin/quotas
# https://developers.google.com/youtube/v3/quickstart/python
# https://developers.google.com/youtube/v3/docs
# https://developers.google.com/explorer-help/guides/code_samples#python
# https://github.com/SloBloLabs/YoutubeManager

import os
import json
import argparse
import time
import logging
from pprint                         import pp
from googleapiclient.discovery      import build
from googleapiclient.errors         import HttpError
from google_auth_oauthlib.flow      import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials      import Credentials

'''
LOGGER = logging.getLogger('googleapiclient.http')
LOGGER.setLevel(level=logging.DEBUG)

ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(ch)
LOGGER.addHandler(ch)'''

class YTManager:
    """A class to maintain youtube playlists"""

    def __init__(self):
        
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        #self.SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
        self.SCOPES= ["https://www.googleapis.com/auth/youtube"]
        self.client_secrets_file = "client_secret_file.json"
        self.api_service_name = "youtube"
        self.api_version = "v3"
        with open("ytauthkey.txt") as f:
            self.api_key = f.read()
            f.close()
        self.ytOAuth = None
        self.ytKey = build(self.api_service_name, self.api_version, developerKey=self.api_key)
        self.model = {}
    
    def __del__(self):
        #self.ytKey.close()
        self.logout()
    
    def getModel(self):
        return self.model

    def login(self):
        if(self.ytOAuth == None):
            # Get credentials and create an API client
            flow = InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, self.SCOPES)
            credentials = flow.run_console()
            self.ytOAuth = build(
                self.api_service_name, self.api_version, credentials=credentials)
            print("Logged in to youtube.")

    def logout(self):
        if(self.ytOAuth):
            self.ytOAuth.close()
            self.ytOAuth = None
            print("Logged out from youtube.")

    def fetchSubscriptions(self, channel):
        
        if(self.ytOAuth == None):
            self.login()
        
        nextPageToken = None
        
        result = []
        
        while True:
            request = self.ytOAuth.subscriptions().list(
                part="snippet",
                channelId=channel,
                maxResults=50,
                pageToken=nextPageToken
            )
            response = request.execute()
            #pp(response)
            
            for i in response['items']:
                result.append({
                    "title": i['snippet']['title'],
                    "channel": i['snippet']['resourceId']['channelId'],
                    "id": i['id']
                })
            
            try:
                nextPageToken = response["nextPageToken"]
            except KeyError:
                break
        
        return result
    
    def addSubscription(self, subscription):
        if(self.ytOAuth == None):
            self.login()
        
        request = self.ytOAuth.subscriptions().insert(
            part="snippet",
            body={
              "snippet": {
                "resourceId": {
                  "kind": "youtube#channel",
                  "channelId": subscription
                }
              }
            }
        )
        response = request.execute()
        #pp(response)
    
    def removeSubscription(self, subscriptionID):
        if(self.ytOAuth == None):
            self.login()
        
        request = self.ytOAuth.subscriptions().delete(
            id=subscriptionID
        )
        request.execute()
    
    def findLikesListFromChannel(self, channel, mine=None):
        if(self.ytOAuth == None):
            self.login()
        
        if mine:
            channel = None
        
        request = self.ytOAuth.channels().list(
            part="contentDetails",
            id=channel,
            mine=mine,
            maxResults=50
        )
        response = request.execute()
        #pp(response)
        
        return response['items'][0]['contentDetails']['relatedPlaylists']['likes']
    
    def fetchLists(self, channel, mine=None):
        if(self.ytOAuth == None):
            self.login()
        
        if mine:
            channel = None
        
        request = self.ytOAuth.playlists().list(
            part="id, snippet, status",
            channelId=channel,
            maxResults=50,
            mine=mine
        )
        response = request.execute()
        #pp(response)

        result = []
        for i in response['items']:
            result.append({"title": i['snippet']['title'], "id": i['id']})
        
        return result
    
    def createList(self, title):
        if(self.ytOAuth == None):
            self.login()
        
        request = self.ytOAuth.playlists().insert(
            part="snippet,status",
            body={
              "snippet": {
                "title": title,
                "description": "",
                "tags": [
                    "API call"
                ],
                "defaultLanguage": "en"
              },
              "status": {
                "privacyStatus": "private"
              }
            }
        )
        response = request.execute(num_retries=10)
        #pp(response)
        
        return {"title": response['snippet']['title'], "id": response['id']}
    
    def setListStatus(self, playlist, title, status):
        if(self.ytOAuth == None):
            self.login()
        request = self.ytOAuth.playlists().update(
            part="snippet, status",
            body={
                "id": playlist,
                "snippet": {
                    "title": title
                },
                "status": {
                  "privacyStatus": status
                }
            }
        )
        response = request.execute()
        pp(response)
    
    def deleteList(self, playlist):
        if(self.ytOAuth == None):
            self.login()
        
        request = self.ytOAuth.playlists().delete(
            id=playlist
        )
        request.execute()
    
    def fetchListItems(self, playlist):
        if(self.ytOAuth == None):
            self.login()
        
        nextPageToken = None
        
        result = []

        while True:
            request = self.ytOAuth.playlistItems().list(
                part="snippet",
                maxResults=50,
                playlistId=playlist,
                pageToken=nextPageToken
            )
            response = request.execute()
            #pp(response)

            for i in response['items']:
                result.append({
                    "position": i['snippet']['position'],
                    "title": i['snippet']['title'],
                    "vid": i['snippet']['resourceId']['videoId'],
                    "id": i["id"]
                })

            try:
                nextPageToken = response["nextPageToken"]
            except KeyError:
                break
        
        return result
    
    def insertListItem(self, playlistID, videoID):
        if(self.ytOAuth == None):
            self.login()
        
        request = self.ytOAuth.playlistItems().insert(
            part="snippet",
            body={
              "snippet": {
                "playlistId": playlistID,
                #"position": 0,
                "resourceId": {
                  "kind": "youtube#video",
                  "videoId": videoID
                }
              }
            }
        )
        response = request.execute()
        #pp(response)

        return response
    
    def loadModelFromChannel(self, channelID):
        # Self created lists
        print("Loading playlists...", end=' ')
        self.model['playlists'] = self.fetchLists(self, channelID)
        for l in self.model['playlists']:
            id = l['id']
            l['items'] = self.fetchListItems(id)
        print("done.")

        # Liked videos
        print("Loading liked videos...", end=' ')
        likesID = self.findLikesListFromChannel(channelID)
        self.model['likedVideos'] = self.fetchListItems(likesID)
        print("done.")

        # Subscriptions
        print("Loading subscriptions...", end=' ')
        self.model['subscriptions'] = self.fetchSubscriptions(channelID)
        print("done.")
    
    def transferModelToChannel(self, channelID):
        
        # Self created lists
        existingPlaylists = self.fetchLists(self, channelID)

        print("Saving playlists")
        for l in self.model['playlists']:
            print(l['title'], end='', flush=True)
            # check if list name exists
            n = [s for s in existingPlaylists if s['title'] == l['title']]
            if(len(n) > 0):
                # playlist exists
                listId = n[0]['id']
            else:
                # new playlist
                while(True):
                    try:
                        newList = self.createList(l['title'])
                    except HttpError as err:
                        print("Error resp: ", err.resp)
                        # <HttpError 429 when requesting https://youtube.googleapis.com/youtube/v3/playlists?part=snippet%2Cstatus&alt=json returned "Resource has been exhausted (e.g. check quota).". Details: "Resource has been exhausted (e.g. check quota).">
                        # https://stackoverflow.com/questions/22786068/how-to-avoid-http-error-429-too-many-requests-python
                        # https://stackoverflow.com/questions/65907439/youtube-data-api-v3-returns-429-resource-has-been-exhausted-havent-used-nearly
                        if(err.resp['status'] == '429'):
                            # Retry after 10s
                            print("Retry...", end=' ', flush=True)
                            time.sleep(10)
                        else:
                            print(err)
                            self.logout()
                            exit(0)
                    else:
                        break
                #pp(newList)
                listId = newList['id']
            
            existingPlaylistItems = self.fetchListItems(listId)
            for v in l['items']:
                n = [s for s in existingPlaylistItems if s['vid'] == v['vid']]
                if(len(n) == 0):
                    # New video item
                    try:
                        newVideoItem = self.insertListItem(listId, v['vid'])
                    except HttpError:
                        print("!", end='', flush=True)
                    #pp(newVideoItem)
                    #break
                    else:
                        print(".", end='', flush=True)
                else:
                    print("\\", end='', flush=True)
            print("done.", flush=True)
            #break
        
        # Liked Videos
        likesPlaylist = self.findLikesListFromChannel(channelID)
        existingLikedVideos = self.fetchListItems(likesPlaylist)
        
        print("Saving liked videos")
        for v in self.model['likedVideos']:
            n = [s for s in existingLikedVideos if s['vid'] == v['vid']]
            if(len(n) == 0):
                # New video item
                try:
                    newVideoItem = self.insertListItem(likesPlaylist, v['vid'])
                except HttpError:
                    print("!", end='', flush=True)
                #pp(newVideoItem)
                #break
                else:
                    print(".", end='', flush=True)
            else:
                print("\\", end='', flush=True)
        print("done.", flush=True)
        
        # Subscriptions
        existingSubscriptions = self.fetchSubscriptions(channelID)
        print("Saving subscriptions")
        for l in self.model['subscriptions']:
            #print(l['title'], end=' ', flush=True)
            n = [s for s in existingSubscriptions if s['channel'] == l['channel']]
            if(len(n) > 0):
                # subscription exists
                print("\\", end='', flush=True)
            else:
                # new subscription
                self.addSubscription(l['channel'])
                print(".", end='', flush=True)
            #break
        print("done.", flush=True)
    
    def loadModelFromFile(self, filename):
        with open(filename, 'r', encoding='utf8') as f:
            self.model = json.load(f)
            #self.mode = f.read()
            f.close()
    
    def saveModelToFile(self, filename):
        with open(filename, 'w', encoding='utf8') as f:
            json.dump(self.model, f, indent=4)
            #f.write(str(self.model))
            f.close()

def main():

    parser = argparse.ArgumentParser(description='Youtube Manager by SloBlo Labs')
    parser.add_argument('-sc', '--sourceChannelId', type=str, help='the source youtube channel id')
    parser.add_argument('-tc', '--targetChannelId', type=str, help='the target youtube channel id')
    parser.add_argument('-f' , '--modelFile'      , type=str, help='the model file to store and read data', nargs='?', default='ytmodel.json')
    #parser.add_arguement('--help', help='help text')
    args = parser.parse_args()
    #print(args)
    #print("src: ", args.sourceChannelId)
    #print("trg: ", args.targetChannelId)
    #print("file: ", args.modelFile)

    ytmgmt = YTManager()

    if(args.sourceChannelId is None and args.targetChannelId is None):
        print("Neither source nor target channel provided. Skipping!")
        exit(0)

    if(args.sourceChannelId is not None):
        print("Source channel: ", args.sourceChannelId)
        goodToGo = False
        if(os.path.isfile(args.modelFile)):
            print("model file ", args.modelFile, " already exists. Overwrite? [Y/n]", end=' ')
            x = input()
            if(x == 'Y'):
                goodToGo = True
            else:
                print("Skipping.")
        else:
            goodToGo = True
        
        if(goodToGo):
            print("Fetching model...")
            ytmgmt.loadModelFromChannel(args.sourceChannelId)
            ytmgmt.saveModelToFile(args.modelFile)
            ytmgmt.logout()
    
    if(args.targetChannelId is not None):
        print("Target channel: ", args.targetChannelId)
        if(os.path.isfile(args.modelFile)):
            print("Adding model to target channel ", args.targetChannelId)
            ytmgmt.loadModelFromFile(args.modelFile)
            ytmgmt.transferModelToChannel(args.targetChannelId)
        else:
            print("No such file ", args.modelFile, ". Please run YoutubeManager providing a source channel id first.")

if __name__ == "__main__":
    main()