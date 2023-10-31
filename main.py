import re
import spacy
import emoji
import nltk

from unidecode import unidecode
from nltk import pos_tag
from nltk.corpus import names, words
from nltk.tokenize import word_tokenize

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('universal_tagset')

# TODO Function to identify default interjections and preserve them IN PROGRESS
# TODO If possible interjection, go through word until longest possible interjection match inside it is found (see article) and maintain TO DO
# TODO Comment work IN PROGRESS


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


def find_sets(spans):
    sets= []
    def backtrack(rest, current):
        if not rest:
            sets.append(current[:])
            return
        x, y = rest[0]
        for i in range(x + 1, y + 1):
            current.append([x, i])
            backtrack(rest[1:], current)
            current.pop()
    backtrack(spans, [])
    return sets


def combine_spans(sets):
    combinations = []
    def backtrack(rest, current):
        if not rest:
            combinations.append(current[:])
            return
        for s in sets[0]:
            current.extend(s)
            backtrack(rest[1:], current)
            for i in range(len(s)):
                current.pop()
    backtrack(sets, [])
    return combinations


def find_spans(spans):
    sets = [find_sets(spans)]
    combinations = combine_spans(sets)
    return combinations


def analyze_message(message):
    treated_message = ''
    tokens = message.split()
    token_list = analyze_tokens(tokens)
    treated_message = ' '.join(token_list)
    return treated_message


def analyze_tokens(tokens):
    treated_token = ''
    token_list = []
    for token in tokens:
        treated_list = []
        punctuation_separated = re.findall(r'[-_.,;!?]|[A-Za-z0-9]+|\\U[0-9a-fA-F]+', token)
        for element in punctuation_separated:
            # TODO if element represents an interjection then identify the interjection and do not encode, maybe tag the element so as to escape the next treatment in case interjection is included in vocabulary TO DO
            # TODO check if token can be tagged with UH or not too TO DO
            if (element.lower() in words.words('en') and element.lower() != 'yeah') or element.isdigit():
                element = encode_word(element)
            # TODO check if token can be tagged with UH or not too TO DO
            elif element.lower() not in words.words('en') and element.lower() != 'yeah':
                element = identify_word(element, token)
            treated_list.append(element)
            treated_token = ''.join(treated_list)
        token_list.append(treated_token)
    return token_list


def encode_word(element):
    word = []
    for character in element:
        if character.isupper():
            symbol = 'Z'
        elif character.isdigit():
            symbol = 'y'
        else:
            symbol = 'z'
        character = symbol
        word.append(character)
    encoded_word = ''.join(word)
    return encoded_word


def identify_word(element, token):
    number_repeats = len(re.findall(r'([a-zA-Z])\1{1,}', element))
    repeated_characters = re.search(r'([a-zA-Z])\1{1,}', element)
    unique_alphabetic = re.search(r'([a-zA-Z])(?!\1)(?![\d\W])', element)
    if repeated_characters and number_repeats == 1:
        return one_repetition(repeated_characters, element)
    elif repeated_characters and number_repeats > 1:
        return multiple_repetitions(element, token)
    elif not repeated_characters and unique_alphabetic:
        return encode_word(element)
    else:
        return element


def one_repetition(repeated_characters, element):
    start, end = repeated_characters.span()
    sliced_word = element
    sliced_index = end - 1
    # TODO check if token can be tagged with UH or not too TO DO
    while sliced_word.lower() not in words.words('en') and sliced_word.lower() != 'yeah' and re.search(r'([a-zA-Z])\1{1,}', sliced_word):
        sliced_word = element[:sliced_index] + element[end:]
        sliced_index -= 1
    s, e = sliced_index, end
    # TODO check if token can be tagged with UH or not too TO DO
    if sliced_word.lower() != 'yeah':
        word = []
        for index, character in enumerate(element):
            if index not in range(s, e):
                if character.isupper():
                    symbol = 'Z'
                else:
                    symbol = 'z'
                character = symbol
            word.append(character)
        encoded_word = ''.join(word)
        return encoded_word
    return element


def multiple_repetitions(element, token):
    spans = []
    repeated_sequences = re.finditer(r'([a-zA-Z])\1{1,}', token)
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
        results.append({'word': joined, 'spans': combination})
    longest_word = ''
    final_spans = ''
    for option in results:
        if option['word'].lower() in words.words('en') and len(option['word']) > len(longest_word):
            longest_word = option['word']
            final_spans = option['spans']
    if len(longest_word) > 0:
        word = []
        for index, character in enumerate(element):
            for i, combination in enumerate(final_spans):
                if i < len(spans) - 1:
                    next = spans[i + 1]
                if (index < spans[0][0] or index > spans[-1][-1]) or (index in range(combination[0], combination[1])) or (index >= spans[i][-1] and index < next[0]):
                    if character.isupper():
                        character = 'Z'
                    else:
                        character = 'z'
            word.append(character)
        encoded_word = ''.join(word)
        return encoded_word
    else:
        print('not in vocabulary')
        # TODO Reduce repetitions to 2 TO DO
        # TODO Check interjections TO DO
        # TODO Check repetitions of unicode characters too TO DO
        # TODO If not in vocabulary match then just encode non-repeated characters TO DO
        return element

def main():
    # MESSAGE TO BE REPLACED WITH MESSAGE_LIST WHEN FUNCTIONAL:
    message = 'Yeah, yeah yeahhh Adammmm, Adam will-you send mE a Lnnkkk \\U0001f603 3409'
    # Initiate list to store message data:
    message_list = []
    # Initiate dictionary to store author data:
    author_dict = {}
    # Execute function to read chat text file and output message dictionary list:
    read_chat(author_dict, message_list)
    # TODO create a function for this stage of the process and consider that I do not need so many variables since I could just reassign TO DO

    # INTERJECTIONS WORK
    interjections = []
    text = word_tokenize(message)
    # Tagset is universal if you want X otherwise UH will show
    tagged = pos_tag(text, tagset='universal')
    # TODO go through and if there is a case in which it is X or UH then use this tag; save to list to check against - so you could go over the entire message file to locate anything that could be considered UH/X before and store in list TO DO
    for token, tag in tagged:
        if tag == 'UH' and token not in interjections:
            interjections.append(token)
    treated_message = analyze_message(message)
    print(treated_message)
    # TODO check whether it matches interjections first IN PROGRESS

if __name__ == '__main__':
    main()