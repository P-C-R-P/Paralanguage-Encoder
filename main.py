"""Détection et recodage d'éléments paralinguistiques avec Python"""

import re
import spacy
import emoji
import nltk
import os

from nltk import pos_tag
from nltk.corpus import words
from nltk.tokenize import word_tokenize
from tqdm import tqdm

# Load SpaCy language model:
nlp = spacy.load('en_core_web_sm')

# IMPORTANT: Run following downloads to ensure programme runs successfully:
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('universal_tagset')

# Regex associated with date, time, author, message body and external links within file:
date_regex = r'^[0-9]{2}\/[0-9]{2}\/[0-9]{4}(?=,\s)'
time_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s)[0-9]{2}:[0-9]{2}(?=\s-\s)'
author_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s[0-9]{2}:[0-9]{2}\s-\s).+(?=:\s)'
message_regex = r'(?<=:\s).*$'
punctuation_regex = r'[^\w\s]'
link_regex = r'https?://\S+|www\.\S+'
emoji_regex = r'\\U[0-9a-fA-F]+'

# Store regex patterns for formatting in list to allow efficient access:
regex_list = [date_regex, time_regex, author_regex, message_regex]


# Function to go over message list and find all examples of interjections:
def find_interjections(format, messages, exclusions=[]):
    for message in messages:
        if format == 'exported chat':
            message = message['message']
        tokens = word_tokenize(message)
        tagged_tokens = nltk.pos_tag(tokens)
        for token, tag in tagged_tokens:
            if tag == 'UH' and token not in exclusions:
                exclusions.append(token)
        universal_tagged = pos_tag(tokens, tagset='universal')
        for token, tag in universal_tagged:
            if tag == 'X' and token not in exclusions and '\\' not in token:
                exclusions.append(token)
        document = nlp(message)
        for token in document:
            if token.pos_ == 'INTJ' and token.text not in exclusions:
                exclusions.append(token.text)
    return exclusions


# Function to encode and decode each message to convert to unicode:
def encode_emoji(character):
    return character.encode('unicode-escape').decode('utf-8')


# Function that splits messages given regex patterns to create list of dictionaries:
def format_messages(author_dict, message_list, line):
    try:
        if all(re.search(regex, line) for regex in regex_list):
            message_text = line.split(' - ', 1)
            date, time = message_text[0].split(', ', 1)
            author, message = message_text[1].split(': ', 1)
            if author not in author_dict:
                name = f'speaker{len(author_dict)}'
                author_dict[author] = name
                author = name
            else:
                author = author_dict[author]
            message_dict = {'date': date, 'time': time,
                                'author': author, 'message': message.replace('\n', '')}
            message_list.append(message_dict)
    except:
        print('Error: there was a problem processing this message.')


# Function to read chat text file and output message dictionary list:
def read_chat(path):
    message_list = []
    author_dict = {}
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            format_messages(author_dict, message_list, line)
    for message in message_list:
        encoded_message = ''
        for character in message['message']:
            if emoji.is_emoji(character):
                character = encode_emoji(character)
            encoded_message += character
        message['message'] = encoded_message
    return message_list


# Backtracking algorithm that finds all span combinations, recursively calling itself:
def backtrack(rest, current, combinations):
    if not rest:
        combinations.append(current[:])
        return
    start, end = rest[0]
    for i in range(start + 1, end + 1):
        current.append([start, i])
        backtrack(rest[1:], current, combinations)
        current.pop()
    return combinations


# Function to find all combinations of spans so all spans (x, y) are found until y = x:
def find_spans(spans):
    combinations = []
    combinations = backtrack(spans, [], combinations)
    return combinations


# Function to split message into tokens on whitespace, returning treated tokens:
def analyze_message(message, interjections=[]):
    tokens = message.split()
    token_list = analyze_tokens(tokens, interjections)
    treated_message = ' '.join(token_list)
    return treated_message


# Function that goes over tokens in list, identifying in and out of vocabulary tokens:
def analyze_tokens(tokens, interjections=None):
    emoticons = get_exclusions('emoticons.txt')
    treated_token = ''
    token_list = []
    for token in tokens:
        treated_list = []
        escaped_emoticons = []
        for emoticon in emoticons:
            escaped_emoticons.append(re.escape(emoticon))
        emoticons_regex = '|'.join(escaped_emoticons)
        if re.match(emoticons_regex, token):
            treated_list.append(token)
        elif re.match(link_regex, token):
            word = []
            for character in token:
                if not re.match(punctuation_regex, character):
                    symbol = 'ω'
                    character = symbol
                word.append(character)
            encoded_word = ''.join(word)
            treated_list.append(encoded_word)
        else:
            punctuation_separated = re.findall(r'[-_.:\"\',;!?]|[A-Za-z0-9]+|\\U[0-9a-fA-F]+', token)
            for element in punctuation_separated:
                if (element.lower() in words.words('en') and element.lower() not in interjections) or element.isdigit():
                    element = encode_word(element)
                elif element.lower() not in words.words('en') and element.lower() not in interjections and not re.match(emoji_regex, element):
                    element = identify_word(element, interjections)
                treated_list.append(element)
        treated_token = ''.join(treated_list)
        token_list.append(treated_token)
    return token_list


# Function that takes individual token and encodes it using symbols:
def encode_word(element):
    word = []
    for character in element:
        character = choose_symbol(character)
        word.append(character)
    encoded_word = ''.join(word)
    return encoded_word


# Function to choose symbol associated with character depending on type:
def choose_symbol(character):
    if character.isupper():
        symbol = 'Λ'
    elif character.isdigit():
        symbol = 'μ'
    else:
        symbol = 'λ'
    character = symbol
    return character


# Function to attempt to identify and encode tokens that are out of vocabulary:
def identify_word(element, interjections=[]):
    number_repeats = len(re.findall(r'([a-zA-Z])\1{1,}', element))
    repeated_characters = re.search(r'([a-zA-Z])\1{1,}', element)
    unique_alphabetic = re.search(r'([a-zA-Z])(?!\1)(?![\d\W])', element)
    if repeated_characters and number_repeats == 1:
        return identify_single(repeated_characters, element, interjections)
    elif repeated_characters and number_repeats > 1:
        return identify_multiple(element, interjections)
    elif not repeated_characters and unique_alphabetic:
        return encode_word(element)
    else:
        return element


# Function to identify if out of vocabulary word with single repetition is in vocabulary:
def identify_single(repeated_characters, element, interjections=[]):
    start, end = repeated_characters.span()
    sliced_word = element
    sliced_index = end - 1
    while sliced_word.lower() not in words.words('en') and sliced_word.lower() not in interjections and re.search(r'([a-zA-Z])\1{1,}', sliced_word):
        sliced_word = element[:sliced_index] + element[end:]
        sliced_index -= 1
    s, e = sliced_index, end
    if sliced_word.lower() not in interjections:
        word = []
        for index, character in enumerate(element):
            if index not in range(s, e):
                character = choose_symbol(character)
            word.append(character)
        encoded_word = ''.join(word)
        return encoded_word
    return element


# Function to identify if token with multiple repetitions is in vocabulary and encode:
def identify_multiple(element, interjections=[]):
    spans = []
    repeated_sequences = re.finditer(r'([a-zA-Z])\1{1,}', element)
    for match in repeated_sequences:
        start, end = match.span()
        spans.append([start, end])
    combinations = find_spans(spans)
    results = []
    for combination in combinations:
        result = []
        start = 0
        for index, item in enumerate(combination):
            result.append(element[start:item[0]] + element[item[0]:item[1]])
            start = spans[index][1]
        result.append(element[start:])
        joined = ''.join(result)
        if all(joined[i] != joined[i + 1] or joined[i] != joined[i + 2] for i in range(len(joined) - 2)):
            results.append({'word': joined, 'spans': combination})
    longest_word = ''
    final_spans = ''
    for option in results:
        singular = option['word'].rstrip('s')
        if singular.lower() in interjections:
            longest_word = option['word']
            return element
        if singular.lower() in words.words('en') and len(singular) > len(longest_word):
            longest_word = option['word']
            final_spans = option['spans']
    if len(longest_word) > 0:
        word = []
        for index, character in enumerate(element):
            for i, combination in enumerate(final_spans):
                if i < len(spans) - 1:
                    next = spans[i + 1]
                if (index < spans[0][0] or index >= spans[-1][-1]) or (index in range(combination[0], combination[1])) or (index >= spans[i][-1] and index < next[0]):
                    character = choose_symbol(character)
            word.append(character)
        encoded_word = ''.join(word)
        return encoded_word
    else:
        word = []
        for index, character in enumerate(element):
            character = choose_symbol(character)
            word.append(character)
        encoded_word = ''.join(word)
        return encoded_word


# Function to read file when provided as body of text rather than formatted export:
def read_file(path):
    messages = []
    with open(path, 'r', encoding='utf-8') as file:
        contents = file.read()
        encoded_message = ''
        for character in contents:
            if emoji.is_emoji(character):
                character = encode_emoji(character)
            encoded_message += character
        messages.append(encoded_message)
    return messages


# Function to allow export of encoded messages to external text file:
def write_file(path, messages):
    with open(path, 'w', encoding='utf-8') as file:
        for message in messages:
            if isinstance(message, dict):
                message = str(message)
            file.write(message + '\n')


# Function that reads external files to make list of exclusions:
def get_exclusions(file):
    exclusions = []
    with open(file, 'r', encoding='utf-8') as file:
        for line in file:
            exclusions.append(line.strip())
    return exclusions


# Function that allows initiation of programme and user input of options for encoding:
def initiate():
    messages = None
    exclusions = []
    while True:
        path = input('Please input the name of the file you wish to encode:\n')
        if os.path.exists(path):
            break
        else:
            print("File not found.")
    format = input('Choose your format (body of text/exported chat):\n')
    while format.lower() != 'body of text' and format.lower() != 'exported chat':
        format = input("Enter 'body of text' or 'exported chat':\n")
    if format.lower() == 'body of text':
        message_list = read_file(path)
    elif format.lower() == 'exported chat':
        message_list = read_chat(path)
    options = input('Do you have an external text file of words you wish to be excluded from encoding?\n')
    while options.lower() != 'no' and options.lower() != 'yes':
        options = input("Enter 'yes' or 'no':\n")
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
                exclusions = get_exclusions(external_file)
                break
            else:
                print("File not found.")
    interjections = find_interjections(format, message_list, exclusions)
    with tqdm(total=len(message_list)) as pbar:
        for message in message_list:
            if format.lower() == 'exported chat':
                message_in = message['message']
            else:
                message_in = message
            if message_in == '<Media omitted>':
                treated_message = message_in
            else:
                treated_message = analyze_message(message_in, interjections)
            if format.lower() == 'body of text':
                messages = [treated_message]
            elif format.lower() == 'exported chat':
                message['message'] = treated_message
            pbar.update(1)
    if format.lower() == 'exported chat':
        messages = message_list
    print(messages)
    save = input('Do you want to save externally?\n')
    while save.lower() != 'no' and save.lower() != 'yes':
        save = input("Enter 'yes' or 'no':\n")
    if save.lower() == 'yes':
        save_path = input('Write path name:\n')
        confirmation = input(f'Is "{save_path}" correct?\n')
        if confirmation.lower() == 'yes':
            try:
                write_file(save_path, messages)
            except:
                print('Error: there was a problem saving to this file path.')


# Function that allows programme to be initiated:
def main():
    initiate()


# Allow programme functions to be used independently as package:
if __name__ == '__main__':
    main()