
test:
	pytest

dev-watch-yaml:
	devbin/watch.sh datadictionary "python3.7 datadictionary/package.py --vv"

# outputs the help for the CLI tool `package.py`
yaml-package-help:
	python3.7 datadictionary/package.py --help

# Processes the source YAML into both C and markdown formats
# This will direct both outputs to the same folder which is probably undesirable
yaml-package:
	python3.7 datadictionary/package.py --sourcedir datadictionary --job all --outdir ../ventosdoc

# Package up the YAML into C files
yaml-package-c:
	python3.7 datadictionary/package.py --sourcedir datadictionary --job c --outdir ../ventosdoc

# Package up the YAML into C markdown
yaml-package-md:
	python3.7 datadictionary/package.py --sourcedir datadictionary --job markdown --outdir ../ventosdoc


