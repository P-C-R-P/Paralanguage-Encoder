import re
# import spacy
# import nltk
# from nltk.tokenize import TreebankWordTokenizer as twt


def main():
    chat = r'test.txt'

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
        new_dict = {'date': date, 'time': time, 'author': author, 'message': message}
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

    print(dict_list)


if __name__ == "__main__":
    main()
