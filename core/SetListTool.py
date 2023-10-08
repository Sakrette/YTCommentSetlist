import re, os, platform

if __name__ == '__main__':
    from  utils import setlist_parser
else:
    from .utils import setlist_parser

FILE = "./SetList.txt"
DATA = {}
INFO = {"videoid": "", "datetime": "", "title": ""}
RAWS = {"setlist": "", "setlist_data": {}}
FIXS = {}

def refresh(*, suppress=False, from_raw=False):
    if from_raw:
        if RAWS['setlist_data']:
            DATA.clear()
            DATA.update(RAWS['setlist_data'])
        elif RAWS['setlist']:
            try:
                parse(RAWS['setlist'], suppress=True, with_fixed=True)
            except:
                print('Parse failed, content:')
                print(RAWS['setlist'])
                
    else:
        print('Reading File...')
        
        with open(FILE, 'rb') as file:
            raw = file.read().decode('utf8')

        FIXS.clear()
        try:
            parse(raw)
        except:
            print('Parse failed, content:')
            print(RAWS['setlist'])

    if not suppress:
        table()


def set_data(setlist_data:dict, /):
    #print('Set Data:', setlist_data)
    RAWS['setlist_data'].clear()
    RAWS['setlist_data'].update({data['Song']:{key:val for key, val in data.items()} for data in setlist_data})
    refresh(suppress=True, from_raw=True)
    return setlist_data

def parse(content, /, *, suppress=False, update=True, with_fixed=False):
    if update:
        data = DATA
        DATA.clear()
        if FIXS and not with_fixed:
            FIXS.clear()
        elif with_fixed and FIXS:
            contents = content.split('\r\n')
            for line_index, replacement in FIXS.items():
                contents[line_index] = replacement
            else:
                content = '\r\n'.join(contents)    
    else:
        data = dict()
    
    RAWS.update({'setlist': content})
    if content:
        setlist = setlist_parser.parse(content)
        clear() # may have modifying messages
        
        for song in setlist.values():
            data.update({song['Song']: song})
        return setlist


def fix(line_index=None, replacement=None, **kwargs):
    contents = RAWS['setlist'].split('\r\n')
    if line_index is None:
        w = len(str(len(contents)))
        for i, line in enumerate(contents):
            if i in FIXS:
                print(f'[{i:>{w}}]', FIXS[i])
            else:
                print(f'[{i:>{w}}]', line)
        line_index = input('Select line to fix: ')

    if line_index == '': # cancelled
        clear()
        refresh(from_raw=RAWS['setlist']!='')
    elif type(line_index) is not int and not str(line_index).isdigit():
        print('>> Invalid line index:', line_index, flush=True)
    elif type(line_index) is not int:
        line_index = int(str(line_index))
        if line_index < 0 or line_index >= len(contents):
            return print(f'Failed to fix line [{line_index}]: Invalid Line')

        print('Line to fix:')
        print(f'[{line_index}]', contents[line_index], flush=True)

        if replacement is None:
            replacement = input('Enter replacement line: ')
        
        clear()
        if replacement:
            FIXS[line_index] = replacement
            print(f'Fixed line [{line_index}]:', replacement)
        elif line_index in FIXS:
            FIXS.pop(line_index)
            print(f'Removed fix of line [{line_index}]:', contents[line_index])
        refresh(from_raw=RAWS['setlist']!='')
    else:
        print('>> No song index:', line_index, flush=True)

def setlist():
    return sorted(DATA.values(), key=lambda item: item['Index'])

def table(*, display=True):
    if display:
        for item in setlist():
            print(str(item['Index'])+'.', item['Time'], item['Song'], item['Artist'] or '(Unknown)', sep='\t', flush=True)
    else:
        return setlist()

def time(*, display=True):
    if display:
        for item in setlist():
            print(item['Time'], flush=True)
    else:
        return [item['Time'] for item in setlist()]

def song(*, display=True):
    if display:
        for item in setlist():
            print(item['Song'], flush=True)
    else:
        return [item['Song'] for item in setlist()]
def detail(index, /, *, display=True):
    index = int(index) - 1
    if index<0 or index>=len(DATA):
        return
    else:
        song_info = setlist()[index]
    if display:
        print("Song Index :", index              , flush=True)
        print("Timestamp  :", song_info['Time']  , flush=True)
        print("Song Title :", song_info['Song']  , flush=True)
        print("Artist Name:", song_info['Artist'], flush=True)
    else:
        return song_info

def raw(*, display=True):
    if display:
        print(RAWS['setlist'], flush=True)
    else:
        return RAWS['setlist']

def clear():
    os.system('cls' if 'win' in platform.platform().lower() else 'clear')


def main(vinfo:dict=None):
    info = ""
    if type(vinfo) is dict:
        for key in INFO.keys():
            INFO[key] = vinfo[key] if key in vinfo else ""
        if any(INFO.values()):
            info = " ".join((INFO["datetime"], f"({INFO['videoid']})", INFO["title"]))
    
        if info:
            print(info, flush=True)
            table()
            
    while (cmd:=input('> ')) or True:
        clear()
        if not cmd:
            print(info, flush=True)
            table()
            continue

        cmd, *args = cmd.split(' ')

        # make '\ ' in to combined arguments, last is ignored
        for i in range(len(args)-2, -1, -1):
            if args[i].endswith('\\'):
                args[i] = args[i][:-1] + ' ' + args.pop(i+1)
        
        if info:
            print(info, flush=True)
        if cmd in ['E', 'exit', 'Q', 'quit']:
            break
        elif cmd in ['R', 'refresh']:
            refresh(from_raw=not not info)
        elif cmd in ['B', 'table']:
            table()
        elif cmd in ['T', 'time']:
            time()
        elif cmd in ['S', 'song']:
            song()
        elif cmd.isdigit():
            detail(cmd)
        # data fixing
        elif cmd in ['raw']:
            raw()
        elif cmd in ['fix']:
            if args:
                fix(args[0], **dict((*pair.split('='), None)[:2] for pair in args[1:]))
            else:
                fix()
        cmd = ''


if __name__ == "__main__":
    refresh()
    main()
