# YoutubeManager
## Python skript to transfer playlists, liked videos and subscriptions from one Youtube account to another using Youtube API V3.

You can call the YoutubeManager script from command line providing a source and/or a target channel id. Optionally you can choose the model file in order to manage different accounts.
If a source but no target channel is provided, the script will simply download the model and write it to a file before aborting. On the other hand, if a target channel id but no source is given, the script will try to load the model from the file and start pushing contents.

### Preparation
Before starting the script you need to create an OAuth 2.0 client id within the Google Cloud Api Console at https://console.cloud.google.com/apis/credentials. Download the secret file into the same folder of the YoutubeManager script and call it "client_secret_file.json".

### Usage
#### Help
```
python YoutubeManager.py --help
usage: YoutubeManager.py [-h] [-sc SOURCECHANNELID] [-tc TARGETCHANNELID] [-f [MODELFILE]]

Youtube Manager by SloBlo Labs

optional arguments:
  -h, --help            show this help message and exit
  -sc SOURCECHANNELID, --sourceChannelId SOURCECHANNELID
                        the source youtube channel id
  -tc TARGETCHANNELID, --targetChannelId TARGETCHANNELID
                        the target youtube channel id
  -f [MODELFILE], --modelFile [MODELFILE]
                        the model file to store and read data
```

#### Render source channel to model file
```
python YoutubeManager.py -sc <SOURCE CHANNEL ID>
```

#### Write model file to target channel
```
python YoutubeManager.py -tc <TARGET CHANNEL ID>
```

#### Both steps in one go
```
python YoutubeManager.py -sc <SOURCE CHANNEL ID> -tc <TARGET CHANNEL ID>
```

## Scope
The script is intended to help porting existing channel conents to another. Please note, as of today, only self created playlists, liked videos and subscriptions are supported.
The Youtube Client API v3 as of today (2nd April 2021) does not support the WatchList. This is why there will be still some manual steps left to complete the transfer.
In addition, the script will not preserve watch states of individual videos.