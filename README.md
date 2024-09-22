# 5coltabdelconverter

GenBank to Tab Delimited Converter

This is a simple Python script that allows users to input GenBank files on command line and convert them to a 5-column tab-delimited format based on allowed features and qualifiers. The script uses BioPython to parse and convert the GenBank files.

Features

- Input a Genbank file (.gb or .gbk format) and empty output file in command line
- Automatically extract allowed features and qualifiers from the INSDC Feature Table
- Convert the GenBank file to a 5-column tab-delimited format
- Write converted data to output file

Technologies

- BioPython: Toolkit for biological computations
- BeautifulSoup: Python library for web scraping (to extract feature and qualifier data)

Installation

1. Clone the repository:
git clone https://github.com/azc9673/genbank-to-tab-converter.git
cd genbank-to-tab-converter
2. Install the required packages:
pip install -r requirements.txt

Usage

1. Run the converter by executing:
python testconverter.py input_file.gb output_file.tab

Project Structure

genbank-to-tab-converter/
│
├── parsedconverter.py     # Main converter application
├── requirements.txt       # List of dependencies
├── README.md              # Project documentation
├── .gitignore             # Files and directories to be ignored by Git
└── LICENSE                # License for the project

Credits
BioPython: BioPython.org
Flask: Flask.palletsprojects.com
Contact
If you have any questions or feedback, please contact:
Albert Chen: azc9673@nyu.edu
