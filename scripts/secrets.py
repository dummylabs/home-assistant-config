def get_secret(key):
    global s
    return s[key]

s = {}
with open('/config/secrets.yaml', encoding='utf-8-sig') as f:
     for line in f.readlines():
         p = line.split(":")
         if len(p) > 1:
             s[p[0].strip()] = ":".join(p[1:]).strip()