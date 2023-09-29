import re
import spacy
import emoji

from unidecode import unidecode
from nltk.corpus import words

def main():
    # Assign file name to variable:
    chat = 'test-chat.txt'

    # Load SpaCy natural language model:
    model = spacy.load('en_core_web_sm')

    example_message = 'send me a linkkk'

    document = model(example_message)
    tokens = []
    for token in document:
        if token.text.lower() not in words.words('en'):
            tokens.append(token.text)
    # Initiate list and dictionary to store message and author data:
    message_list = []
    author_dict = {}

    # Defining the Regular Expressions associated with date, time, author, message body and external links within WhatsApp file
    date_regex = r'^[0-9]{2}\/[0-9]{2}\/[0-9]{4}(?=,\s)'
    time_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s)[0-9]{2}:[0-9]{2}(?=\s-\s)'
    author_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s[0-9]{2}:[0-9]{2}\s-\s).+(?=:\s)'
    message_regex = r'(?<=:\s).*$'
    link_regex = r'^https?:\/\/\S+$'

    # Store all regex patterns in array to allow efficient access:
    regex_list = [date_regex, time_regex, author_regex, message_regex]

    # Open exported WhatsApp text file with UTF-8 encoding:
    with open(chat, 'r', encoding='utf-8-sig') as file:
        # Read each line in the file:
        lines = file.readlines()
        # Go through each line in the file:
        for line in lines:
            # Convert emojis and decode line to remove accents:
            line_decoded_emojis = unidecode(emoji.demojize(line))
            # Attempt to print each line:
            try:
                # If each line includes a date, time, author and message than proceed:
                if all(re.search(regex, line_decoded_emojis) for regex in regex_list):
                    # Split line on hyphen to separate timestamp:
                    message_text = line_decoded_emojis.split(' - ', 1)
                    # Assign timestamp to date and time variables by splitting on comma:
                    date, time = message_text[0].split(', ', 1)
                    # Assign rest of message body to author and message variables by splitting on colon:
                    author, message = message_text[1].split(': ', 1)
                    # Ignore messages that represent omitted media or just links:
                    if message.strip() != '<Media omitted>' and not re.match(link_regex, message):
                        # Check if author is already in the author dictionary:
                        if author not in author_dict:
                            # Anonymise speaker name and add to author dictionary:
                            name = f'speaker{len(author_dict)}'
                            author_dict[author] = name
                            # Replace author name with anonymized name:
                            author = name
                        else:
                            # Replace author name with anonymized name from author dictionary:
                            author = author_dict[author]
                            # Store message data in a dictionary, replacing unnecessary newlines:
                            message_dict = {'date': date, 'time': time, 'author': author, 'message': message.replace('\n', '')}
                        # Append each dictionary to message list:
                            message_list.append(message_dict)
            # Otherwise if there is an error with a character in that line, return an error message:
            except:
                print('Error: there was a problem processing this message.')

if __name__ == '__main__':
    main()
