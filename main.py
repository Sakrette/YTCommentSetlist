import os, platform, copy

if __name__ == '__main__':
    from  core import YtVideoTool as YVT, SetListTool as SLT
else:
    from .core import YtVideoTool as YVT, SetListTool as SLT


def show_help():
    helplist = {
        "H": {
                "cmd": ('H', 'help'),
                "arg": ()
            },
        "R": {
                "cmd": ('R', 'refresh'),
                "arg": ('last=10', )
            },
        "L": {
                "cmd": ('L', 'list'),
                "arg": ('last=10', )
            },
        "V": {
                "cmd": ('(empty)', 'V', 'video'),
                "arg": ('index', )
            },
        "E": {
                "cmd": ('E', 'Q', 'exit', 'quit'),
                "arg": ()
            }
    }
    for helpitem in helplist.values():
        print('/'.join(helpitem['cmd']), *helpitem['arg'])

# helpers
def clear():
    os.system('cls' if 'win' in platform.platform().lower() else 'clear')
def parse_int(string, num_range:tuple=None):
    if type(string) is int or string.isdigit():
        if num_range is None or (
                type(num_range) is tuple
                    and len(num_range)==2
                    and num_range[0] < num_range[1]
                    and num_range[0]<=int(string)<=num_range[1]
            ):
            return int(string)
    return # invalid
            


# globals
LATEST   = [] # [(VideoId, DateTime, Title)]
SETLISTS = [] # [{Index, Time, Song, Artist}]


# side functions
def get_latest(last=10):
    LATEST  [:] = YVT.show_last(last)
    SETLISTS[:] = [None] * last

def show_latest(last=10, /, refresh=False):
    last = parse_int(last) or len(LATEST) or 10 # 0 is not valid, get all or 10 as default
    if not LATEST or len(LATEST)<last or refresh:
        get_latest(last)
    else:
        latest = LATEST[:last]
        for index, (_id, timestamp, title) in enumerate(latest, 1):
            print(f'{index:>{len(str(last))}}.', timestamp, _id, title, flush=True)

def get_setlist(vid, /, *, update=False):
    '''
        @param  VideoId
        @return [{Index, Time, Song, Artist}]
    '''
    if (type(vid) is int or vid.isdigit()):
        if 0<=int(vid)<len(LATEST):
            index = int(vid)
            vid   = LATEST[index][0]
        else:
            return
    else:
        index = [item[0] for item in LATEST].find(vid) # -1 if not found

    if not update and (~index and SETLISTS[index]): # use cached
        return SLT.set_data(SETLISTS[index])
        
    setlist = YVT.setlist(vid)
    if not setlist:
        default_candis = "セトリ,setlist,set list"
        print('Setlist not found, maybe try other keywords? (separate with comma: ",")')
        print('Current Keywords:', default_candis)
        while candis:=input('New Keywords: '):
            setlist = YVT.setlist(vid, candidates=candis.split(','))
            if setlist:
                break
            else:
                print('Setlist not found, maybe try other keywords? (separate with comma: ",")')
                print('Current Keywords:', candis)
        else:
            return
    
    if type(setlist) is list: # need select
        print(f'Find {len(setlist)} SetLists, please select:', flush=True)
        for i, sl in enumerate(setlist, 1):
            print(f"{i}.", flush=True)
            print(*['    ' + line for line in sl.split('\n')[:5]], sep='\n', flush=True)
        while (select:=input('Select: ')) or True:
            if select.isdigit() and 1<=int(select)<=len(setlist):
                setlist = setlist[int(select)-1]
                break
            else:
                select = ''
        clear()

    
    try:
        SLT.parse(setlist)
    except:
        print('Parse failed, content:')
        print(setlist)
        return

    setlist = copy.deepcopy(SLT.setlist())
    
    if ~index: # not -1
        SETLISTS[index] = setlist
    return setlist

def route_video(index):
    index = parse_int(index, (1, len(SETLISTS)))
    if index is None:
        return
    setlist = get_setlist(index-1)
    if not setlist:
        SLT.parse("") # clear
    SLT.main(dict(zip(("videoid", "datetime", "title"), LATEST[index-1])))
    # back from SLT.main
    SETLISTS[index-1] = SLT.setlist() # update, maybe fixed
    clear()
    show_latest(0) # 0 for all

# main function
def main():
    while (cmd:=input('> ')) or True:
        clear()
        if not cmd:
            show_latest(0)
            continue
        
        cmd, *args = cmd.split()
        # quit
        if cmd in ['E', 'exit', 'Q', 'quit']:
            break
        # help
        elif cmd in ['H', 'help']:
            show_help()
        # refresh
        elif cmd in ['R', 'refresh']:
            show_latest(*args[:1], refresh=True)
        # get list (last N)
        elif cmd in ['L', 'list']:
            show_latest(*(args[:1] or [0])) # default 0 for all
        # enter video last N
        elif cmd in ['V', 'video']:
            route_video(*args[:1])
        elif cmd.isdigit():
            route_video(cmd)
        cmd = ''

if __name__ == "__main__":
    clear()
    get_latest()
    main()
    
