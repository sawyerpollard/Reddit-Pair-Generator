git clone https://github.com/Microsoft/Recognizers-Text.git

cd Recognizers-Text/Python/libraries/resource-generator
pip install -r ./requirements.txt
python index.py ../recognizers-number/resource-definitions.json
python index.py ../recognizers-number-with-unit/resource-definitions.json
python index.py ../recognizers-date-time/resource-definitions.json

cd ..
pip install -e ./recognizers-text/
pip install -e ./recognizers-number/
pip install -e ./recognizers-number-with-unit/
pip install -e ./recognizers-date-time/