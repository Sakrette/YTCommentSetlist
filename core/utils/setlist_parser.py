
import re

RULE_MAP = dict((
    ('%T', r'(\d{1,2}(?:\:\d{1,2}){1,2})'),
    ('%t', r'(\d{1,2}(?:\:\d{1,2}){1,2})'),
    ('%I', r'(\d+)'),
    ('%S', r'(.+)'),
    ('%s', r'(\(.+\))?'),
    ('%A', r'(.+)'),
    ('%a', r'(\(.+\))?'),
    ('%#', r'(.+)'),
))
DATA_MAP = {
    'Index' : ('%I', int),
    'Time'  : ('%T', str),
    'Song'  : ('%S', str),
    'Artist': ('%A', str),
}

def _parse(content, rule='%T ~ %t %I. %S%s | %A%a'):
    # basic check, no duplicated key
    key_order = re.findall('|'.join(RULE_MAP.keys()), rule)

    re_rule = rule

    for c in '\\^$|[]().?*+:{}':
        re_rule = re_rule.replace(c, '\\' + c)
    re_rule = re.sub('\\s+', '\\\\s+', re_rule)
    
    re_rule = '^' + re_rule + '$'

    for key, reg in RULE_MAP.items():
        re_rule = re_rule.replace(key ,reg)

    setlist_raw = []
    for line in re.findall(re_rule, content.replace('\r', ''), re.M):
        # print(f'{line=}')
        song_dict = dict(zip(key_order, line))
        # fix mixed
        for key, reg in RULE_MAP.items():
            if reg.endswith('?') and (key.upper()+key) in rule and song_dict[key] == '': # mixed
                par, chi = key.upper(), key
                # print('test:', par, chi, song_dict[par], RULE_MAP[chi][:-1]+'$')
                match_n = re.search(RULE_MAP[chi][:-1]+'$', song_dict[par])
                if match_n:
                    song_dict.update({
                        par: song_dict[par][:-len(match_n[0])],
                        chi: match_n[0]
                    })
        setlist_raw.append(song_dict)
    setlist_raw.sort(key=lambda item:item.get('%I', None) or item.get('%T'))    

    setlist = {}
    for i, song_data in enumerate(setlist_raw):
        data = {}
        for key, (code, type) in DATA_MAP.items():
            data[key] = type(song_data.get(code, type()))
        setlist[data.get('Index', i+1)] = data
    return setlist

def parse(content, /):
    setlist = _parse(content)
    default_format = '%T ~ %t %I. %S%s | %A%a'
    if not setlist:
        print('No songs found, maybe try another format?')
        print('Content:')
        print(*content.split('\r\n')[:5], sep='\r\n')
        print('Formats:')
        print('<Main>')
        print('   %I=Index')
        print('   %T=Time')
        print('   %S=Song Name')
        print('   %A=Artist Name')
        print('<Ignores>')
        print('   %t=End Time')
        print('   %s=Romanized/English Song Name (with parenthesis)')
        print('   %a=Romanized/English Artist Name (with parenthesis)')
        print('   %#=Any other unwanted words')
        print('Current format:', default_format, flush=True)

        while rule:=input('New Format: '):
            setlist = _parse(content, rule=rule)
            if setlist:
                break
            else:
                print('No songs found, maybe try another format?')
                print('Current format:', rule, flush=True)
    return setlist