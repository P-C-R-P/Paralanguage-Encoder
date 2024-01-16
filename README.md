# Détection et recodage d'éléments paralinguistiques

Projet de master en analyse textuelle avec Python, entrepris à l'UNIL sous la direction d'Aris Xanthos, SA2023.

## 1. Purpose

This programme is designed for detecting and recoding paralinguistic elements in chat data. Please read `final-report.pdf` for more detail about the work that I have undertaken.

## 2. Installation

Install the following required dependencies:

- `pip install spacy`
- `pip install emoji`
- `pip install nltk`
- `pip install tqdm`

Download the following resources by uncommenting the following code:

`
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')`

## 3. Initiation

1. Ensure you have prepared the text file you wish to encode.
2. Run the script from your terminal: `python main.py`.
3. Input the file name, format type and if you wish to include an external file of reserve words as prompted.
4. A progress bar will show you the status of the encoding process.
5. Once the programme has run, you will be asked whether you wish to save the encoded file externally.

## 4. Package

To use the programme functions externally and independently in your own programme, first import the script into your programme with `import main.py` and then use the functions as required.
