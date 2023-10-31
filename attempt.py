import re
# import spacy
# import nltk
# from nltk.tokenize import TreebankWordTokenizer as twt


def main():
    chat = r'test-chat.txt'

    dict_list = []
    error_list = []
    author_list = []

    # Regular expression patterns associated with date, time, author name and message to extract these data from text
    # file
    date_regex = r'^[0-9]{2}\/[0-9]{2}\/[0-9]{4}(?=,\s)'
    time_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s)[0-9]{2}:[0-9]{2}(?=\s-\s)'
    author_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s[0-9]{2}:[0-9]{2}\s-\s)[A-Z][a-z]+[\s]+[A-Z][a-z]+(?=:\s)'
    message_regex = r'(?<=:\s).*$'

    # Function to search for date regular expression in text file and return true or false if there is match
    def date_function(text):
        match = re.search(date_regex, text)
        if match:
            return True
        else:
            return False

    # Function to search for time regular expression in text file and return true or false if there is match
    def time_function(text):
        match = re.search(time_regex, text)
        if match:
            return True
        else:
            return False

    # Function to search for author name regular expression in text file and return true or false if there is match
    def author_function(text):
        match = re.search(author_regex, text)
        if match:
            return True
        else:
            return False

    # Function to search for message regular expression in text file and return true or false if there is match
    def message_function(text):
        match = re.search(message_regex, text)
        if match:
            return True
        else:
            return False

    # Function to split text associated with author name by colon and return true or false if length of author name is 2
    def author_split(text):
        text = text.split(': ', 1)
        if len(text) == 2:
            return True
        else:
            return False

    # Function to split text associated with date, time, message and author by dash, comma, colon and index position
    # and return list of dictionaries
    def line_split(text):
        text = text.split(' - ')
        timestamp = text[0]
        date, time = timestamp.split(', ')
        message = ' '.join(text[1:])
        if author_split(message):
            split = message.split(': ')
            author = split[0]
            message = ' '.join(split[1:])
        else:
            author = 'WhatsApp'
        new_dict = {'date': date, 'time': time,
                    'author': author, 'message': message}
        dict_list.append(new_dict)

    # Open text file, read lines and for each line, if date, time, author and message functions return true,
    # run line split function, otherwise append to error list
    with open(chat, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
        for line in lines:
            if date_function(line) and time_function(line) and author_function(line) and message_function(line):
                line_split(line)
            else:
                error_list.append(line)

    # For each dictionary in list, check whether author value is in author list, if not append author value to author
    # list, then rename author value according to index position in author list
    for d in dict_list:
        name = d['author']
        if name not in author_list:
            author_list.append(name)
        for i in range(len(author_list)):
            if name == author_list[i] and name != 'WhatsApp':
                d['author'] = 'Speaker ' + str(i + 1)

    # THINGS TO DO NEXT:
    # - Use and split author list by space, if value in author list appears in message, replace with number of λ to
    # match speaker length
    # - Organise messages into separate arrays according to speaker
    # - Join all messages together into single string for each speaker
    # - For each speaker's messages tag words according to linguistic feature
    # - If word is not linguistic feature, append to list of para/extra features
    # - If word is linguistic feature, replace word with upper and lowercase λ

    with open(chat, 'w', encoding='utf-8-sig') as file:
        print(dict_list, file=file)


if __name__ == "__main__":
    main()

def test_spacy():
    # Load SpaCy natural language model:
    model = spacy.load('en_core_web_sm')
    # Initiate empty list to store paralanguage features:
    features = []
    # An example message for testing purposes:
    example_message = 'yeah, Philippa, send me a linkkk :pray:'
    # Use SpaCy NLP model to tokenize message:
    tokens = model(example_message)
    # Go through tokens:
    for token in tokens:
        # Check whether the tokens extracted from NLP model exist as words within English as defined by NLTK:
        if token.text.lower() not in words.words('en'):
            # If they do not exist then append them to the list of potential paralanguage tokens:
            features.append(token.text)
    # Execute function to read chat text file and output message dictionary list:
    read_chat()
    print(features)


emoji_regex = r':[A-Za-z_-]+:'
test = 'Ignore this message, :pray: :) 🙂😊'
test = unidecode(emoji.demojize(test))
result = re.search(emoji_regex, test)
print(result)

# TODO Identify :emojis:
# TODO Split into tokens
# TODO Tag names, numbers, emojis, punctuation
# TODO Identify interjections with nltk (UH)
# TODO Find words -> view list of non-words to identify gaps in coverage
# Split on whitespace - create list of key-value pairs for each word/token and assign tag to those we want?
# Identify and tag emojis using regex :description:
# Split into tokens after this part if necessary
# Identify punctuation as aspect of paralanguage
# Identify interjections using nltk/spacy
# Identify miscellaneous language features using tokenization to view list of unattributed features
# Encode the rest of the text file as needed
# Connect example to list of dictionaries
# Think about machine learning for better understanding of paralanguage features
# Think about previous research project
# Save all features at the end to optimise future use

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
                    symbol = 'Z'
                # Otherwise:
                else:
                    # Assign lowercase symbol:
                    symbol = 'z'
                # Change character to appropriate symbol:
                message_list[index] = symbol
    # Rejoin message list to form string:
    message = ''.join(message_list)
    # Return altered string:
    return message



# Define function to remove any numbers from message passed to it:
def remove_numbers(message):
    # Substitute any numeric character with symbol:
    return re.sub(r'\d', 'z', message)


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
    alphabetic_regex = r'[^a-zA-Z]'
    # Split message on whitespace into 'tokens':
    tokens = split_text(message)
    # Loop over each token:
    for token in tokens:
        # Focus on alphabetic characters and ignore/clean others:
        clean_token = re.sub(alphabetic_regex, '', token)
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

    # Initiate list to store names:
    names_list = []

    # Retrieve all names in all messages first before going over messages to anonymise
    retrieve_names(author_dict, names_list, message)
    # Treated message is anonymized with numbers removed:
    message = anonymise_message(names_list, message)

    # Execute function to convert emojis and decode line to remove accents; assign to variable:
    line_decoded = decode_text(line)


# Define function to convert emojis and decode line to remove accents:
def decode_text(line):
    # Convert emojis and decode line to remove accents:
    return unidecode(emoji.demojize(line))

    if not rest:
        combinations.append(list(combination))
        return

    for i in range(len(rest)):
        current = rest[i]
        if not current or current[1] > combination[-1]:
            combination.append(current)
            rest.pop(i)
            backtracking_algorithm(combinations, combination, rest)
            combination.pop()
            rest.insert(i, current)

    # for i in range(len(token)):
    #     match = re.search(r'([a-zA-Z])\1{1,}', token)
    #     if match:
    #         start, end = match.span()
    #         print(start, end)
    #         sliced_word = token[:end-i] + token[end:]
    #         # new_word = token[:i] + token[i:i+start] + token[i+end:]
    #         print(sliced_word)
    #         result = backtracking_algorithm(sliced_word)
    #         if result:
    #             return result


# TODO Encode based on word and spans found (i.e. xiiiixkkkk) DONE
# TODO Put into functions to make code cleaner DONE
# TODO Cope with multiple repetitions DONE
# TODO account for situations in which there are multiple characters that are repeated DONE
# TODO check why names are not matching ADAM but are matching ADAMMMMM DONE
# TODO encode if it doesn't match DONE
# TODO I'm going to need to take inspiration from n-queens backtracking algorithm for multiple repetitions DONE
# TODO Split or tokenise to treat each message DONE
# TODO Function to take the default case (something considered in vocabulary by nltk or spacy) and encode with upper and lowercase symbol DONE
# TODO Algorithm to go through repetitions in out of vocabulary word to identify if removing repetitions makes word in-vocabulary DONE
# TODO If removing all repetitions is not fruitful, call that word a word and conceal except repetitions DONE
# TODO If there is no interjection match then codify aspects which are not repeated DONE
# TODO Ensure emojis and emoticons remain DONE
# TODO elif out of vocabulary and has repetitions continue to remove repeated character until in vocabulary and if still out of vocabulary mask all characters which do not represent repetitions DONE# TODO Encode based on word and spans found (i.e. xiiiixkkkk) DONE
# TODO Put into functions to make code cleaner DONE
# TODO Cope with multiple repetitions DONE
# TODO account for situations in which there are multiple characters that are repeated DONE
# TODO check why names are not matching ADAM but are matching ADAMMMMM DONE
# TODO encode if it doesn't match DONE
# TODO I'm going to need to take inspiration from n-queens backtracking algorithm for multiple repetitions DONE
# TODO Split or tokenise to treat each message DONE
# TODO Function to take the default case (something considered in vocabulary by nltk or spacy) and encode with upper and lowercase symbol DONE
# TODO Algorithm to go through repetitions in out of vocabulary word to identify if removing repetitions makes word in-vocabulary DONE
# TODO If removing all repetitions is not fruitful, call that word a word and conceal except repetitions DONE
# TODO If there is no interjection match then codify aspects which are not repeated DONE
# TODO Ensure emojis and emoticons remain DONE
# TODO elif out of vocabulary and has repetitions continue to remove repeated character until in vocabulary and if still out of vocabulary mask all characters which do not represent repetitions DONE
