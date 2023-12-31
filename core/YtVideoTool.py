

from sys import stderr
import datetime, pytz
import googleapiclient.discovery, googleapiclient.errors



GLOBALS = {
        "DEVELOPER": {
            "KEY": "", # your own developer key
        },
        "CHANNEL"  : {
            "ID"      : "UC7A7bGRVdIwo93nqnA3x-OQ", # Maisaki Berry's channel id
            "PLAYLIST": "UU7A7bGRVdIwo93nqnA3x-OQ"  # Maisaki Berry's channel's videos id
        }
    }




# get youtube
def yt(new=False, /, _yt=dict()):
    if not new and "yt" in _yt:
        return _yt['yt']
    
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = GLOBALS['DEVELOPER']['KEY']
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = DEVELOPER_KEY)
    _yt['yt'] = youtube
    return youtube

# time convert
def convt(ftime, to_str=True):
    # *T*Z should be forced to be set as UTC+0
    time = datetime.datetime.strptime(ftime+'+00:00', '%Y-%m-%dT%H:%M:%SZ'+'%z').astimezone(pytz.timezone('japan'))
    if to_str:
        return datetime.datetime.strftime(time, '%Y/%m/%d %H:%M:%S')
    else:
        return time


    

# comments
def cmts(vid):
    request = yt().commentThreads().list(
        part="snippet",
        maxResults=100,
        videoId=vid
    )
    try:
        response = request.execute()
    except googleapiclient.errors.HttpError as error:
        print(f'{type(error).__name__}:', (error.error_details[0]['reason']), file=stderr)
        return
    return response

# find setlist in comments
def setlist(vid, candidates=("セトリ", "setlist", "set list")):
    comments = cmts(vid)
    if not comments:
        return
    
    contents = [cmt['snippet']['topLevelComment']['snippet']['textOriginal'] for cmt in comments['items']]
    setlists = [cont for cont in contents
                    if any([candi in cont.lower() for candi in candidates])
                ]
    return None if not setlists else setlists[0] if len(setlists)==1 else setlists

# video infos
def info(*vids, jst=True):
    if not vids:
        return []
    
    info_list = []
    iterator = range(0,len(vids),50) # 50 for each time

    for start_vid in iterator:
        request = yt().videos().list(
            part="snippet,liveStreamingDetails",
            id = ",".join(vids[start_vid:start_vid+50])
        )
        response = request.execute()
        info_list += [(video['id'], (lambda t: convt(t) if jst else t)(
                        video['snippet']['publishedAt'] if 'liveStreamingDetails' not in video # videos
                        else video['liveStreamingDetails']['actualStartTime'   ] if 'actualStartTime'    in video['liveStreamingDetails'] # archive
                        else video['liveStreamingDetails']['scheduledStartTime'] if 'scheduledStartTime' in video['liveStreamingDetails'] # scheduled
                        else video['snippet']['publishedAt'] # mysterious livestream
                    ), video['snippet']['title']) for video in response['items']]

    return sorted(info_list, key=lambda item: item[1], reverse=True)

# new uploads
def news(last=None):
    request = yt().playlistItems().list(
        part="contentDetails",
        playlistId=GLOBALS['CHANNEL']['PLAYLIST'], # videos playlist (latest videos from channel)
        maxResults=50 if last==-1 else last # uplimit is 50
    )
    response = request.execute()

    video_list = [video['contentDetails']['videoId'] for video in response['items']]

    if last is not None:
        while last == -1 or len(video_list) < last:
            nextPageToken = response.get('nextPageToken', None)
            if nextPageToken is None: # no more pages
                break
            request = yt().playlistItems().list(
                part="contentDetails",
                playlistId=GLOBALS['CHANNEL']['PLAYLIST'], # videos playlist (latest videos from channel)
                maxResults=50 if last==-1 else last-len(video_list), # uplimit is 50
                pageToken=nextPageToken
            )
            response = request.execute()
            if not response['items']: # no more videos found
                break
            video_list += [video['contentDetails']['videoId'] for video in response['items']]

    return video_list


# show lastest
def show_last(last=10):
    latest = news(last)
    infos  = info(*latest)
    for index, (_id, timestamp, title) in enumerate(infos, 1):
        print(f'{index:>{len(str(last))}}.', timestamp, _id, title, flush=True)
    return infos
