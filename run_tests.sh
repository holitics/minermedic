#!/bin/sh

# must have the PHENOME core installed
pip install phenome-core --extra-index-url https://api.packagr.app/AvVcpYfO2/

# must have the PHENOME extensions installed (for tests AND packaging)
git clone https://${GH_TOKEN}@github.com/holitics/phenome-extensions phenome

# run the tests
pytest
