
test:
	pytest

lint:
	pylint datadictionary/*.py

# Watch processes that use script taking
# 1 - path to watch
# 2 - command to run
dev-watch-test:
	devbin/watch.sh datadictionary "make test"

dev-watch-lint:
	devbin/watch.sh datadictionary "make lint"

dev-watch-yaml:
	devbin/watch.sh datadictionary "python3.7 datadictionary/package.py --job all -vv --outdir ../ventosdoc"

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


