start:
	powershell ./env/Scripts/activate.ps1
test:
	cd ./src && python research.py -i one.csv -o test.csv
run:
	cd ./src && python research.py -i labs.csv -o output.csv
lint:
	make format && cd ./src && pylint research.py
format:
	cd ./src && black . -l 80