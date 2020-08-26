start:
	powershell ./start.ps1
try:
	cd ./src && python research.py -i one.csv -o test.csv
run:
	cd ./src && python research.py -i labs.csv -o output.csv
groups:
	cd ./src && python groups.py -i groups.csv -o groups_test.csv
lint:
	make format && cd ./src/research && pylint .
format:
	cd ./src && black . -l 80
tests:
	cd ./src && python -m unittest research_test.py
