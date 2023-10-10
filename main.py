import re
import spacy
import emoji

from unidecode import unidecode
from nltk.corpus import names

# TODO Split or tokenise to treat each message
# TODO Function to take the default case (something considered in vocabulary by nltk or spacy) and encode with upper and lowercase symbol
# TODO Function to identify default interjections and preserve them
# TODO Algorithm to go through repetitions in out of vocabulary word to identify if removing repetitions makes word in-vocabulary
# TODO If removing all repetitions is not fruitful, call that word a word and conceal except repetitions
# TODO If possible interjection, go through word until longest possible interjection match inside it is found (see article) and maintain
# TODO If there is no interjection match then codify aspects which are not repeated
# TODO Ensure emojis and emoticons remain


# Define function to encode and decode each message to convert to unicode:
def encode_decode(text):
    # Encode and decode to maintain unicodes for emojis and accents:
    return text.encode('unicode-escape').decode('utf-8-sig')


# Define function that splits up messages according to regular expression patterns to create list of dictionaries:
def format_messages(author_dict, message_list, line):
    # Defining regular expressions associated with date, time, author, message body and external links within file:
    date_regex = r'^[0-9]{2}\/[0-9]{2}\/[0-9]{4}(?=,\s)'
    time_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s)[0-9]{2}:[0-9]{2}(?=\s-\s)'
    author_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s[0-9]{2}:[0-9]{2}\s-\s).+(?=:\s)'
    message_regex = r'(?<=:\s).*$'
    link_regex = r'^https?:\/\/\S+$'
    # Store all regex patterns in array to allow efficient access:
    regex_list = [date_regex, time_regex, author_regex, message_regex]
    # Attempt to read each line:
    try:
        # If each line includes a date, time, author and message than proceed:
        if all(re.search(regex, line) for regex in regex_list):
            # Split line on hyphen to separate timestamp:
            message_text = line.split(' - ', 1)
            # Assign timestamp to date and time variables by splitting on comma:
            date, time = message_text[0].split(', ', 1)
            # Assign rest of message body to author and message variables by splitting on colon:
            author, message = message_text[1].split(': ', 1)
            # Ignore messages that represent omitted media or just links:
            if message.strip() != '<Media omitted>' and not re.match(link_regex, message):
                author = encode_decode(author)
                # Check if author is already in the author dictionary:
                if author not in author_dict:
                    # Anonymise speaker name:
                    name = f'speaker{len(author_dict)}'
                    # Add to author dictionary:
                    author_dict[author] = name
                    # Replace author name with anonymized name:
                    author = name
                # Otherwise:
                else:
                    # Replace author name with anonymized name from author dictionary:
                    author = author_dict[author]
                # Store message data in a dictionary, replacing unnecessary newlines:
                message_dict = {'date': date, 'time': time,
                                'author': author, 'message': message.replace('\n', '')}
                # Append each dictionary to message list:
                message_list.append(message_dict)
    # Otherwise if there is an error with a character in that line, return an error message:
    except:
        print('Error: there was a problem processing this message.')

# Define function to read chat text file and output message dictionary list:
def read_chat(author_dict, message_list):
    # Assign file name to variable:
    chat = 'test-chat.txt'
    # Open exported WhatsApp text file with UTF-8 encoding:
    with open(chat, 'r', encoding='utf-8-sig') as file:
        # Read each line in the file:
        lines = file.readlines()
        # Go through each line in the file:
        for line in lines:
            # Format each line as message:
            format_messages(author_dict, message_list, line)
    # Go over each message in list:
    for message in message_list:
        # Encode and decode message to keep unicode for emojis and accents:
        message['message'] = encode_decode(message['message'])


def main():
    # MESSAGE TO BE REPLACED WITH MESSAGE_LIST WHEN FUNCTIONAL:
    message = 'yeah, Adammmm, Adam will-you send me a linkkk \\U0001f603 3409'
    # Initiate list to store message data:
    message_list = []
    # Initiate dictionary to store author data:
    author_dict = {}
    # Execute function to read chat text file and output message dictionary list:
    read_chat(author_dict, message_list)


if __name__ == '__main__':
    main()
