#!/bin/sh

# need boto3 for AWS access
pip install boto3

# need twine to upload package
pip install twine

# cleanup old build (if applicable)
rm -rf build
rm -rf dist

# must have the PHENOME extensions installed (for tests AND packaging)
git clone https://${GH_TOKEN}@github.com/holitics/phenome-extensions phenome

# copy version file to phenome dir
cp ./version.py phenome/version.py

# build the core agent (with no CORE files)
python setup.py sdist

# build the APP package
python package.py 

# upload the APP package to s3
if [ ! -z "$AMZ_ACCESS_KEY" ]
then
	python3 setup_functions.py upload_minermedic_s3
fi

# This will deploy using twine
twine upload -u $PACKAGR_USERNAME -p $PACKAGR_PASSWORD --verbose --repository-url $PACKAGR_REPOSITORY_URL dist/*

