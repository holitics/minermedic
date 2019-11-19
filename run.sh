#!/bin/sh

# export FLASK_ENV=development

has_core=$(pip list modules | grep phenome-core)

if [ -z "$has_core" ]; then
	echo "Installing Phenome Core..."
	pip install phenome-core --extra-index-url https://api.packagr.app/AvVcpYfO2/
fi

if [ ! -d "phenome" ]; then
	echo "Installing Phenome Extensions..."
	# must have the PHENOME extensions installed
	# the packaged distro has the needed extensions, but when
	# cloning directly from GitHub, the dependencies may not be there.
	git clone https://github.com/holitics/phenome-extensions phenome
fi

python3 run.py

