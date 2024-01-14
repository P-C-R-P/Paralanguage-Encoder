import re
import spacy
import emoji
import nltk
import os

# from unidecode import unidecode
from nltk import pos_tag
from nltk.corpus import words
from nltk.tokenize import word_tokenize

# Load SpaCy language model:
nlp = spacy.load('en_core_web_sm')

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('universal_tagset')

# Define function to go over message list and find all examples of interjections:
def find_interjections(format, messages, exclusions=None):
    if exclusions == None:
        # Initiate empty list for interjections:
        interjections = []
    else:
        interjections = exclusions
    # Loop over messages in message list:
    for message in messages:
        if format == 'exported chat':
            message = message['message']
        # Tokenize message:
        tokens = word_tokenize(message)
        # Tag message:
        tagged_tokens = nltk.pos_tag(tokens)
        # Loop over tokens and tags in tagged token list:
        for token, tag in tagged_tokens:
            # If tag represents interjection and is not in interjections list already:
            if tag == 'UH' and token not in interjections:
                # Append to interjections list:
                interjections.append(token)
        universal_tagged = pos_tag(tokens, tagset='universal')
        for token, tag in universal_tagged:
            if tag == 'X' and token not in interjections and '\\' not in token:
                interjections.append(token)
        # Double check by tokenizing with second library:
        document = nlp(message)
        # Loop over tokens in message:
        for token in document:
            # If token text has interjection part-of-speech tag and is not already in interjections list:
            if token.pos_ == 'INTJ' and token.text not in interjections:
                # Append to interjections list:
                interjections.append(token.text)
    # Return list of interjections:
    return interjections


# Define function to encode and decode each message to convert to unicode:
def encode_emoji(character):
    # Encode and decode to maintain unicode for emojis:
    return character.encode('unicode-escape').decode('utf-8')


# Define function that splits up messages according to regular expression patterns to create list of dictionaries:
def format_messages(author_dict, message_list, line):
    # Defining regular expressions associated with date, time, author, message body and external links within file:
    date_regex = r'^[0-9]{2}\/[0-9]{2}\/[0-9]{4}(?=,\s)'
    time_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s)[0-9]{2}:[0-9]{2}(?=\s-\s)'
    author_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s[0-9]{2}:[0-9]{2}\s-\s).+(?=:\s)'
    message_regex = r'(?<=:\s).*$'
    # Store all regex patterns in list to allow efficient access:
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
            if message.strip() != '<Media omitted>':
                # author = encode_decode(author)
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
            elif message.strip() == '<Media omitted>':
                # Store message data in a dictionary, replacing unnecessary newlines:
                message_dict = {'date': date, 'time': time,
                                'author': 'WhatsApp', 'message': message.replace('\n', '')}
                # Append each dictionary to message list:
                message_list.append(message_dict)
    # Otherwise if there is an error with a character in that line, return an error message:
    except:
        print('Error: there was a problem processing this message.')


# Define function to read chat text file and output message dictionary list:
def read_chat(path):
    # Initiate list to store message data:
    message_list = []
    # Initiate dictionary to store author data:
    author_dict = {}
    # Open exported WhatsApp text file with UTF-8 encoding:
    with open(path, 'r', encoding='utf-8') as file:
        # Read each line in the file:
        lines = file.readlines()
        # Go through each line in the file:
        for line in lines:
            # Format each line as message:
            format_messages(author_dict, message_list, line)
    # Go over each message in list:
    for message in message_list:
        # Initiate empty string to store encoded message:
        encoded_message = ''
        # Loop over characters in message:
        for character in message['message']:
            # If character is emoji:
            if emoji.is_emoji(character):
                # Encode and decode to obtain unicode representation of emoji:
                character = encode_emoji(character)
            # Add characters to empty string:
            encoded_message += character
        # Store newly encoded string in message dictionary:
        message['message'] = encoded_message
    return message_list


# Define backtracking algorithm that finds all combinations of spans by recursively calling itself:
def backtrack(rest, current, combinations):
    # If there are no spans left in the list:
    if not rest:
        # Then append entire combination to list of possible combinations:
        combinations.append(current[:])
        # Return to exit recursive backtracking process:
        return
    # Assign first span in list of remaining spans to start and end variables:
    start, end = rest[0]
    # Loop over possible values from start and end:
    for i in range(start + 1, end + 1):
        # Append given span in range x to y, to form part of combination of spans, to current combination:
        current.append([start, i])
        # Backtrack in cases where there are remaining spans in list to find rest of span combinations:
        backtrack(rest[1:], current, combinations)
        # Removes final combination in order to find next possible combination:
        current.pop()
    # Return combinations found from backtracking process:
    return combinations


# Define function that finds all possible combinations of spans such that all spans (x, y) are retrieved until y = x:
def find_spans(spans):
    # Initiate empty list to store each combination of spans found, representing repetitions:
    combinations = []
    # Assign result of backtracking algorithm that finds all combinations of spans to combinations list:
    combinations = backtrack(spans, [], combinations)
    # Return the list of retrieved combinations of spans within range:
    return combinations


# Define function to split given message into tokens on whitespace, returning list of treated tokens and joining them:
def analyze_message(interjections, message):
    # Split message into tokens:
    tokens = message.split()
    # Pass tokens to function to analyse and return encoded tokens as list:
    token_list = analyze_tokens(interjections, tokens)
    # Join tokens in token list with whitespace again:
    treated_message = ' '.join(token_list)
    # Return encoded message:
    return treated_message


# Define function that goes over tokens in list, identifying in and out of vocabulary tokens and encoding them:
def analyze_tokens(interjections, tokens):
    # Initiate treated token as empty string to allow it to be accessed from outside of for loop:
    treated_token = ''
    # Initiate empty list for encoded tokens:
    token_list = []
    punctuation_regex = r'[^\w\s]'
    link_regex = r'https?://\S+|www\.\S+'
    # Loop over tokens in token list:
    for token in tokens:
        # Initiate list for treated punctuation-separated tokens:
        treated_list = []
        if re.match(link_regex, token):
            word = []
            for character in token:
                if not re.match(punctuation_regex, character):
                    symbol = 'ω'
                    character = symbol
                word.append(character)
            # Join encoded word together:
            encoded_word = ''.join(word)
            treated_list.append(encoded_word)
        else:
            # Use find all to further split on punctuation and maintain special characters as one token:
            punctuation_separated = re.findall(r'[-_.:\"\',;!?]|[A-Za-z0-9]+|\\U[0-9a-fA-F]+', token)
            # Loop over punctuation-separated tokens:
            for element in punctuation_separated:
                # If punctuation-separated token is in vocabulary according to nltk or it represents a digit:
                if (element.lower() in words.words('en') and element.lower() not in interjections) or element.isdigit():
                    # Immediately encode element:
                    element = encode_word(element)
                # Otherwise if punctuation-separated token is not in vocabulary:
                elif element.lower() not in words.words('en') and element.lower() not in interjections:
                    # Attempt to identify and encode token:
                    element = identify_word(interjections, element, token)
                # Append encoded token to list of treated tokens:
                treated_list.append(element)
        # Join punctuation-separated tokens back together:
        treated_token = ''.join(treated_list)
        # Append punctuation-joined token to list of tokens split on whitespace:
        token_list.append(treated_token)
    # Return whitespace-separated token list:
    return token_list


# Define function that takes individual token and encodes it using symbols:
def encode_word(element):
    # Initiate empty list to append characters of token:
    word = []
    # Loop through characters in given token:
    for character in element:
        # If character is uppercase:
        if character.isupper():
            # Symbol is also uppercase:
            symbol = 'Λ'
        # Otherwise if character is number:
        elif character.isdigit():
            # Symbol is different:
            symbol = 'μ'
        # Otherwise symbol is lowercase:
        else:
            symbol = 'λ'
        # Character is replaced with symbol:
        character = symbol
        # Append encoded character to word list:
        word.append(character)
    # Join encoded word together:
    encoded_word = ''.join(word)
    # Return encoded word:
    return encoded_word


# Define function to attempt to identify and encode tokens that are out of vocabulary:
def identify_word(interjections, element, token):
    # Use regular expressions to find number of repeats, repeated characters, and check if token is purely alphabetic:
    number_repeats = len(re.findall(r'([a-zA-Z])\1{1,}', element))
    repeated_characters = re.search(r'([a-zA-Z])\1{1,}', element)
    unique_alphabetic = re.search(r'([a-zA-Z])(?!\1)(?![\d\W])', element)
    # If only one character is repeated:
    if repeated_characters and number_repeats == 1:
        # Call and return function for tokens with one repetition:
        return identify_single(interjections, repeated_characters, element)
    # Otherwise if multiple characters are repeated:
    elif repeated_characters and number_repeats > 1:
        # Call and return function for tokens with multiple repetitions:
        return identify_multiple(element, token)
    # Otherwise if no characters are repeated and token is purely alphabetic:
    elif not repeated_characters and unique_alphabetic:
        # Encode word immediately:
        return encode_word(element)
    # Otherwise simply return given element:
    else:
        return element


# Define function to identify if out of vocabulary word with single repeated character is in vocabulary and encode:
def identify_single(interjections, repeated_characters, element):
    # Find start and end index of repeated character:
    start, end = repeated_characters.span()
    # Assign given token to new variable for slicing:
    sliced_word = element
    # Assign index repeating last instance of repeated character to variable:
    sliced_index = end - 1
    # While sliced token is not in vocabulary and repeated characters still exist in token:
    while sliced_word.lower() not in words.words('en') and sliced_word.lower() not in interjections and re.search(r'([a-zA-Z])\1{1,}', sliced_word):
        # Further slice word to get rid of one instance of repeated character:
        sliced_word = element[:sliced_index] + element[end:]
        # Decrease index at which to slice word on next iteration:
        sliced_index -= 1
    # Define final start and end index that make word in vocabulary word after removal of repeats:
    s, e = sliced_index, end
    # If word not in list of interjections:
    if sliced_word.lower() not in interjections:
        # Initiate empty list to store characters of given token:
        word = []
        # Loop over characters in given token with associated index position:
        for index, character in enumerate(element):
            # If index not in given range of repeated characters to remove to form in vocabulary word:
            if index not in range(s, e):
                # If character is uppercase:
                if character.isupper():
                    # Symbol is uppercase:
                    symbol = 'Λ'
                elif character.isdigit():
                    # Symbol is different:
                    symbol = 'μ'
                # Otherwise symbol is lowercase:
                else:
                    symbol = 'λ'
                # Replace character with given symbol:
                character = symbol
            # Append encoded character to word list:
            word.append(character)
        # Join word back together to form encoded word:
        encoded_word = ''.join(word)
        # Return encoded word:
        return encoded_word
    # Return element without encoding:
    return element


# Define function to identify if token with multiple repetitions is in vocabulary and encode accordingly:
def identify_multiple(element, token):
    # Initiate empty list to store spans at which repetitions occur:
    spans = []
    # Find all repeated sequences of characters in given token:
    repeated_sequences = re.finditer(r'([a-zA-Z])\1{1,}', token)
    # Loop over each repeated sequence:
    for match in repeated_sequences:
        # Identify start and end of repetition:
        start, end = match.span()
        # Append start and end of span to list of spans as list of form [x, y]
        spans.append([start, end])
    # Call function to find all possible combinations of spans and assign to combinations list:
    combinations = find_spans(spans)
    # Initiate empty list to store all possible combinations of characters that could be in vocabulary:
    results = []
    # Loop over each possible combination of spans in combinations list:
    for combination in combinations:
        # Initiate empty list for characters representing possible in vocabulary word:
        result = []
        # Initiate variable to allow starting from first character of given token:
        start = 0
        # Loop over each span in combination of spans:
        for index, item in enumerate(combination):
            # Append sliced token to result list:
            result.append(element[start:item[0]] + element[item[0]:item[1]])
            # Change start position to end of current span:
            start = spans[index][1]
        # Append rest of token remaining to result list:
        result.append(element[start:])
        # Join result back together to form word:
        joined = ''.join(result)
        # If joined result has no more than two repeated characters in row and thus could be potential word:
        if all(joined[i] != joined[i + 1] or joined[i] != joined[i + 2] for i in range(len(joined) - 2)):
            # Append dictionary with potential word and its associated spans to results list:
            results.append({'word': joined, 'spans': combination})
    # Initiate longest in vocabulary word as empty string:
    longest_word = ''
    # Initiate successful spans to slice for longest word as empty string:
    final_spans = ''
    # Loop over potential options in results list:
    for option in results:
        singular = option['word'].rstrip('s')
        # If given word is in vocabulary and its length is greater than current token:
        if singular.lower() in words.words('en') and len(singular) > len(longest_word):
            # Replace longest word with this word:
            longest_word = option['word']
            # Replace associated spans representing repetitions with those associated with new word:
            final_spans = option['spans']
    # If a word has been retrieved from list of possible options of words:
    if len(longest_word) > 0:
        # Initiate empty list to store encoded characters:
        word = []
        # Loop over each character in original token:
        for index, character in enumerate(element):
            # Loop over successful spans representing start and end of characters creating in vocabulary word:
            for i, combination in enumerate(final_spans):
                # If current combination is not last item:
                if i < len(spans) - 1:
                    # Then next span start is defined:
                    next = spans[i + 1]
                # If character is not repeated character or represents essential character to form word:
                if (index < spans[0][0] or index >= spans[-1][-1]) or (index in range(combination[0], combination[1])) or (index >= spans[i][-1] and index < next[0]):
                    # If character is uppercase:
                    if character.isupper():
                        # Character replaced by uppercase symbol:
                        character = 'Λ'
                    elif character.isdigit():
                        # Symbol is different:
                        character = 'μ'
                    # Character replaced by symbol:
                    else:
                        character = 'λ'
            # Append encoded character to word list:
            word.append(character)
        # Join encoded characters to form encoded word:
        encoded_word = ''.join(word)
        # Return encoded word:
        return encoded_word
    else:
        # Initiate empty list to store encoded characters:
        word = []
        # Loop over each character in original token:
        for index, character in enumerate(element):
            # If character is uppercase:
            if character.isupper():
                # Character replaced by uppercase symbol:
                character = 'Λ'
            elif character.isdigit():
                # Symbol is different:
                character = 'μ'
            # Character replaced by symbol:
            else:
                character = 'λ'
            # Append encoded character to word list:
            word.append(character)
        # Join encoded characters to form encoded word:
        encoded_word = ''.join(word)
        # Return encoded word:
        return encoded_word


def read_file(path):
    messages = []
    with open(path, 'r', encoding='utf-8') as file:
        contents = file.read()
        messages.append(contents)
    return messages


def write_file(path, messages):
    with open(path, 'w', encoding='utf-8') as file:
        for message in messages:
            if isinstance(message, dict):
                message = str(message)
            file.write(message + '\n')


def initiate():
    messages = None
    while True:
        path = input('Please input the name of the file you wish to encode:\n')
        if os.path.exists(path):
            break
        else:
            print("File not found.")
    format = input('Choose your format (body of text/exported chat):\n')
    while format.lower() != 'body of text' and format.lower() != 'exported chat':
        format = input("Enter 'body of text' or 'exported chat':\n")
    # Execute function to read chat text file and output message dictionary list:
    if format.lower() == 'body of text':
        message_list = read_file(path)
    elif format.lower() == 'exported chat':
        message_list = read_chat(path)
    options = input('Do you have an external text file of words you wish to be excluded from encoding?\n')
    while options.lower() != 'no' and options.lower() != 'yes':
        options = input("Enter 'yes' or 'no':\n")
    exclusions = []
    if options.lower() == 'yes':
        while True:
            external_file = input('Please input the name of the file you wish to include or cancel:\n')
            if external_file.lower() == 'cancel':
                external_file = None
                options = input('Do you have an external text file of words you wish to be excluded from encoding?\n')
                while options != 'no' and options != 'yes':
                    options = input("Enter 'yes' or 'no':\n")
                if options.lower() == 'no':
                    break
            elif os.path.exists(external_file):
                with open(external_file, 'r', encoding='utf-8') as file:
                    for line in file:
                        exclusions.append(line.strip())
                break
            else:
                print("File not found.")
    # Find all interjections and create list from them:
    interjections = find_interjections(format, message_list, exclusions)
    # Loop over message dictionaries in message list:
    for message in message_list:
        if format.lower() == 'exported chat':
            message_in = message['message']
        else:
            message_in = message
        if message_in == '<Media omitted>':
            treated_message = message_in
        else:
            # Assign result of identifying and encoding message to treated message variable:
            treated_message = analyze_message(interjections, message_in)
        # Assign treated message to message value in message dictionary:
        if format.lower() == 'body of text':
            messages = [treated_message]
        elif format.lower() == 'exported chat':
            message['message'] = treated_message
    if format.lower() == 'exported chat':
        messages = message_list
    print(messages)
    save = input('Do you want to save externally?\n')
    while save.lower() != 'no' and save.lower() != 'yes':
        save = input("Enter 'yes' or 'no':\n")
    if save.lower() == 'yes':
        save_path = input('Write path name:\n')
        confirmation = input(f'Is "{save_path}" correct:\n')
        if confirmation.lower() == 'yes':
            try:
                write_file(save_path, messages)
            except:
                print('Error: there was a problem saving to this file path.')


def main():
    initiate()


if __name__ == '__main__':
    main()