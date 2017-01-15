import yaml
with open("ircd/data/strings.yaml") as f:
    strings = yaml.load(f)

def get_string(s):
    return strings[s]
