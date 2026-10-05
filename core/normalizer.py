def normalize(raw_input: str) -> str: 
    s = raw_input   

    if s.lower().endswith('am'): 
        s = s[:-2] + 'AM'
    elif s.lower().endswith('pm'): 
        s = s[:-2] + 'PM'

    if len(s) >= 2 and s[0].isdigit() and s[1] == ':':
        s = '0' + s
        
    return s

