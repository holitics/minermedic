#!/bin/sh

pip install phenome-core --extra-index-url https://api.packagr.app/AvVcpYfO2/

if [ ! -d "phenome" ]; then
	# must have the PHENOME extensions installed
	# the packaged distro has the needed extensions, but when
	# cloning directly from GitHub, the dependencies may not be there.
	git clone https://github.com/holitics/phenome-extensions phenome
fi

python3 run.py 2>/dev/null &

