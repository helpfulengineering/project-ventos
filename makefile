
test:
	pytest

dev-watch:
	devbin/watch.sh datadictionary "python3.7 datadictionary/package.py > ../ventosdoc/index.md"
