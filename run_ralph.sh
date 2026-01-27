#!/bin/bash

[[ -d .tmp ]] || mkdir  -p .tmp;
[[ -d .tmp/models.txt  ]] || opencode models > .tmp/models.txt;

models=$(cat .tmp/models.txt|fzf);
while  (( $(grep -r '\[[ -]\]' .tickets/ | wc -l) > 0)) ; do 
	echo "session starting \$(date -Is)";
	timeout 30m opencode run  'read and proceed with instructions in ./ralphy.md' -m $models --agent build -f AGENTS.md;
	#ptimeout 30m -- gemini -yo text -p 'read and proceed with instructions in ./ralphy.md'
	sleep 10s;
	echo "session ended \$(date -Is)";
done;
