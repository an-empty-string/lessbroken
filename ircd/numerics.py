import yaml
with open("ircd/data/numerics.yaml") as f:
    numerics = yaml.load(f)

def get_numeric(s):
    return str(numerics[s]).zfill(3)
