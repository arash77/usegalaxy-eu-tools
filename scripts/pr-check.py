import sys
import requests
import yaml

TOOLSHED_API = 'https://toolshed.g2.bx.psu.edu/api/repositories'
fn = sys.argv[1]

# never mind about fancy yaml linting, let's just make sure the files are openable
sys.stdout.write('Checking modified yaml file {}...\n'.format(fn))
with open(fn) as f:
    yml = [(n['name'], n.get('owner', 'iuc')) for n in yaml.safe_load(f)['tools']]

with open('{}.lock'.format(fn)) as f:
    yml_lock = {n['name'] for n in yaml.safe_load(f)['tools']}

new_tools = [(name, owner) for name, owner in yml if name not in yml_lock]

for name, owner in new_tools:  # check all new tools are in the tool shed
    sys.stdout.write('Checking new tool {} is in the toolshed...\n'.format(name))
    resp = requests.get(TOOLSHED_API, params={'name': name, 'owner': owner}, timeout=30)
    resp.raise_for_status()
    results = resp.json()
    assert any(r['name'] == name for r in results), '{} not in toolshed.'.format(name)
