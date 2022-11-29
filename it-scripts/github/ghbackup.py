#!/usr/bin/env python3
#
# backup all gh repos for an org based on pcre; uses PyGithub, python-env
#
# 2019-12-21 - bjm -initial
# 2020-01-03 - bjm - env support, docs
#

import re,subprocess,dotenv,github

#### config

dotenv.load() # .env
API_KEY = dotenv.get('API_KEY')
ORG     = dotenv.get('ORG', default='axiomzen')
REGEXP  = dotenv.get('REGEXP', default='^cc_.+')

#### 

r     = re.compile(REGEXP)
g     = github.Github(API_KEY)
org   = g.get_organization(ORG)
repos = org.get_repos()

for repo in repos:
	if r.match(repo.name):
		print("Backing up " + repo.ssh_url)
		try:
			subprocess.run(['git','clone','-q',repo.ssh_url])
			subprocess.run(['tar','czf',repo.name+".tgz",repo.name])
			subprocess.run(['rm','-rf',"./"+repo.name])
		except:
			print("\n -- FAILED backup for: " + repo.ssh_url)
			input("CTRL-C to abort, anything else to resume...")
