#!/bin/sh

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

	# TODO - remove the auth token when making extensions Repo public
	git clone https://${GH_TOKEN}@github.com/holitics/phenome-extensions phenome
	
fi

# run the tests
pytest
