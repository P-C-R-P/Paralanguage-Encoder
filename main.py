import re
import spacy
import emoji

from unidecode import unidecode
from nltk.corpus import names


# Define function to remove names from message passed to function:
def remove_names(names_list, message):
    # Convert message to message list to allow string to be mutable:
    message_list = list(message)
    # Loop over names in list of names:
    for name in names_list:
        # Assign result of regular expression search for name to variable:
        search = re.search(re.escape(name), message, flags=re.IGNORECASE)
        # If regular expression result returns a result:
        if search:
            # Access start and end index position using span method defined on search:
            start, end = search.span()
            # Loop over indexes in range given by span:
            for index in range(start, end):
                # If individual character in list of characters constituting message string is uppercase:
                if message_list[index].isupper():
                    # Assign uppercase symbol:
                    symbol = 'O'
                # Otherwise:
                else:
                    # Assign lowercase symbol:
                    symbol = 'o'
                # Change character to appropriate symbol:
                message_list[index] = symbol
    # Rejoin message list to form string:
    message = ''.join(message_list)
    # Return altered string:
    return message


# Define function to remove any numbers from message passed to it:
def remove_numbers(message):
    # Substitute any numeric character with symbol:
    return re.sub(r'\d', 'o', message)


# Define function to anonymise message:
def anonymise_message(names_list, message):
    # First call function to remove names in message:
    message = remove_names(names_list, message)
    # Second return message with numbers removed:
    return remove_numbers(message)


# Define function that simply splits text on whitespace (default):
def split_text(text):
    return text.split()


# Define function to retrieve any names that can be identified from messages and authors:
def retrieve_names(author_dict, names_list, message):
    # Split message on whitespace into 'tokens':
    tokens = split_text(message)
    # Loop over each token:
    for token in tokens:
        # Focus on alphabetic characters and ignore/clean others:
        clean_token = re.sub(r'[^a-zA-Z]', '', token)
        # If that clean token is included in nltk's male or female names and is not yet in the list of names:
        if clean_token in (names.words('male.txt') or names.words('female.txt') and clean_token not in names_list):
            # Then append it:
            names_list.append(clean_token)
    # Iterate over keys in author dictionary used to anonymise speakers:
    for key in author_dict.keys():
        # Create a list based on splitting each name:
        key_list = split_text(key)
        # Loop over names in list:
        for item in key_list:
            # If that name is not yet in the list of names:
            if item not in names_list:
                # Add to the list of names:
                names_list.append(item)
    # Return the list of names:
    return names_list


# Define function to convert emojis and decode line to remove accents:
def decode_text(line):
    # Convert emojis and decode line to remove accents:
    return unidecode(emoji.demojize(line))


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
    # Execute function to convert emojis and decode line to remove accents; assign to variable:
    line_decoded = decode_text(line)
    # Attempt to read each line:
    try:
        # If each line includes a date, time, author and message than proceed:
        if all(re.search(regex, line_decoded) for regex in regex_list):
            # Split line on hyphen to separate timestamp:
            message_text = line_decoded.split(' - ', 1)
            # Assign timestamp to date and time variables by splitting on comma:
            date, time = message_text[0].split(', ', 1)
            # Assign rest of message body to author and message variables by splitting on colon:
            author, message = message_text[1].split(': ', 1)
            # Ignore messages that represent omitted media or just links:
            if message.strip() != '<Media omitted>' and not re.match(link_regex, message):
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
                message_dict = {'date': date, 'time': time, 'author': author, 'message': message.replace('\n', '')}
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


def main():
    # MESSAGE TO BE REPLACED WITH MESSAGE_LIST WHEN FUNCTIONAL:
    message = 'yeah, Adammmm, Adam will-you send me a linkkk :pray: 3409'
    # Initiate list to store message data:
    message_list = []
    # Initiate dictionary to store author data:
    author_dict = {}
    # Initiate list to store names:
    names_list = []
    # Execute function to read chat text file and output message dictionary list:
    read_chat(author_dict, message_list)
    # Retrieve all names in all messages first before going over messages to anonymise
    retrieve_names(author_dict, names_list, message)
    # Treated message is anonymized with numbers removed:
    message = anonymise_message(names_list, message)


if __name__ == '__main__':
    main()