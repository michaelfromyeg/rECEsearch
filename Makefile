start:
	powershell ./env/Scripts/activate.ps1
try:
	cd ./src/research && python research.py -i one.csv -o test.csv
run:
	cd ./src/research && python research.py -i labs.csv -o output.csv
lint:
	make format && cd ./src/research && pylint research.py
format:
	cd ./src && black . -l 80
tests:
	cd ./src && python -m unittest research_test.py
