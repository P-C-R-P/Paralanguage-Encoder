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
def analyze_message(message):
    # Split message into tokens:
    tokens = message.split()
    # Pass tokens to function to analyse and return encoded tokens as list:
    token_list = analyze_tokens(tokens)
    # Join tokens in token list with whitespace again:
    treated_message = ' '.join(token_list)
    # Return encoded message:
    return treated_message


# TODO if element represents an interjection then identify the interjection and do not encode, maybe tag the element so as to escape the next treatment in case interjection is included in vocabulary TO DO
# TODO check if token can be tagged with UH or not too TO DO


# Define function that goes over tokens in list, identifying in and out of vocabulary tokens and encoding them:
def analyze_tokens(tokens):
    # Initiate treated token as empty string to allow it to be accessed from outside of for loop:
    treated_token = ''
    # Initiate empty list for encoded tokens:
    token_list = []
    # Loop over tokens in token list:
    for token in tokens:
        # Initiate list for treated punctuation-separated tokens:
        treated_list = []
        # Use find all to further split on punctuation and maintain special characters as one token:
        punctuation_separated = re.findall(r'[-_.,;!?]|[A-Za-z0-9]+|\\U[0-9a-fA-F]+', token)
        # Loop over punctuation-separated tokens:
        for element in punctuation_separated:
            # If punctuation-separated token is in vocabulary according to nltk or it represents a digit:
            if (element.lower() in words.words('en') and element.lower() != 'yeah') or element.isdigit():
                # Immediately encode element:
                element = encode_word(element)
            # Otherwise if punctuation-separated token is not in vocabulary:
            elif element.lower() not in words.words('en') and element.lower() != 'yeah':
                # Attempt to identify and encode token:
                element = identify_word(element, token)
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
            symbol = 'Z'
        # Otherwise if character is number:
        elif character.isdigit():
            # Symbol is different:
            symbol = 'y'
        # Otherwise symbol is lowercase:
        else:
            symbol = 'z'
        # Character is replaced with symbol:
        character = symbol
        # Append encoded character to word list:
        word.append(character)
    # Join encoded word together:
    encoded_word = ''.join(word)
    # Return encoded word:
    return encoded_word


# Define function to attempt to identify and encode tokens that are out of vocabulary:
def identify_word(element, token):
    # Use regular expressions to find number of repeats, repeated characters, and check if token is purely alphabetic:
    number_repeats = len(re.findall(r'([a-zA-Z])\1{1,}', element))
    repeated_characters = re.search(r'([a-zA-Z])\1{1,}', element)
    unique_alphabetic = re.search(r'([a-zA-Z])(?!\1)(?![\d\W])', element)
    # If only one character is repeated:
    if repeated_characters and number_repeats == 1:
        # Call and return function for tokens with one repetition:
        return identify_single(repeated_characters, element)
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


# TODO check if token can be tagged with UH or not too TO DO
# TODO check if while loop/if statement works when there is a single repeat but word is out of vocabulary (encode) TO DO


# Define function to identify if out of vocabulary word with single repeated character is in vocabulary and encode:
def identify_single(repeated_characters, element):
    # Find start and end index of repeated character:
    start, end = repeated_characters.span()
    # Assign given token to new variable for slicing:
    sliced_word = element
    # Assign index repeating last instance of repeated character to variable:
    sliced_index = end - 1
    # While sliced token is not in vocabulary and repeated characters still exist in token:
    while sliced_word.lower() not in words.words('en') and sliced_word.lower() != 'yeah' and re.search(r'([a-zA-Z])\1{1,}', sliced_word):
        # Further slice word to get rid of one instance of repeated character:
        sliced_word = element[:sliced_index] + element[end:]
        # Decrease index at which to slice word on next iteration:
        sliced_index -= 1
    # Define final start and end index that make word in vocabulary word after removal of repeats:
    s, e = sliced_index, end
    # TEMPORARY:
    if sliced_word.lower() != 'yeah':
        # Initiate empty list to store characters of given token:
        word = []
        # Loop over characters in given token with associated index position:
        for index, character in enumerate(element):
            # If index not in given range of repeated characters to remove to form in vocabulary word:
            if index not in range(s, e):
                # If character is uppercase:
                if character.isupper():
                    # Symbol is uppercase:
                    symbol = 'Z'
                # Otherwise symbol is lowercase:
                else:
                    symbol = 'z'
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


# TODO Reduce repetitions to 2 TO DO
# TODO Check interjections TO DO
# TODO Check repetitions of unicode characters too TO DO
# TODO If not in vocabulary match then just encode non-repeated characters TO DO


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
        # Append dictionary with potential word and its associated spans to results list:
        results.append({'word': joined, 'spans': combination})
    # Initiate longest in vocabulary word as empty string:
    longest_word = ''
    # Initiate successful spans to slice for longest word as empty string:
    final_spans = ''
    # Loop over potential options in results list:
    for option in results:
        # If given word is in vocabulary and its length is greater than current token:
        if option['word'].lower() in words.words('en') and len(option['word']) > len(longest_word):
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
                if (index < spans[0][0] or index > spans[-1][-1]) or (index in range(combination[0], combination[1])) or (index >= spans[i][-1] and index < next[0]):
                    # If character is uppercase:
                    if character.isupper():
                        # Character replaced by uppercase symbol:
                        character = 'Z'
                    # Character replaced by symbol:
                    else:
                        character = 'z'
            # Append encoded character to word list:
            word.append(character)
        # Join encoded characters to form encoded word:
        encoded_word = ''.join(word)
        # Return encoded word:
        return encoded_word
    # TEMPORARY:
    else:
        # TEMPORARY:
        print('not in vocabulary')
        return element


# TODO go through and if there is a case in which it is X or UH then use this tag; save to list to check against - so you could go over the entire message file to locate anything that could be considered UH/X before and store in list TO DO
# TODO create a function for this stage of the process and consider that I do not need so many variables since I could just reassign TO DO
# TODO check whether it matches interjections first IN PROGRESS


def main():
    # TEMPORARY:
    message = 'Yeah, yeah yeahhh Adammmm, Adam will-you send mE a liiiinkkkk \\U0001f603 3409'
    # Initiate list to store message data:
    message_list = []
    # Initiate dictionary to store author data:
    author_dict = {}
    # Execute function to read chat text file and output message dictionary list:
    read_chat(author_dict, message_list)
    # Assign result of identifying and encoding message to treated message variable:
    treated_message = analyze_message(message)
    # TEMPORARY:
    print(treated_message)

    # INTERJECTIONS WORK:
    # interjections = []
    # text = word_tokenize(message)
    # Tagset is universal if you want X otherwise UH will show
    # tagged = pos_tag(text, tagset='universal')
    # for token, tag in tagged:
    #     if tag == 'UH' and token not in interjections:
    #         interjections.append(token)


if __name__ == '__main__':
    main()