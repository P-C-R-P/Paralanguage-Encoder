import re

chat = r'test.txt'

dict_list = []
error_list = []

date_regex = r'^[0-9]{2}\/[0-9]{2}\/[0-9]{4}(?=,\s)'
time_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s)[0-9]{2}:[0-9]{2}(?=\s-\s)'
author_regex = r'(?<=^[0-9]{2}\/[0-9]{2}\/[0-9]{4},\s[0-9]{2}:[0-9]{2}\s-\s)[A-Z][a-z]+[\s]+[A-Z][a-z]+(?=:\s)'
message_regex = r'(?<=:\s).*$'


def date_function(text):
    match = re.search(date_regex, text)
    if match:
        return True
    else:
        return False


def time_function(text):
    match = re.search(time_regex, text)
    if match:
        return True
    else:
        return False
    
    
def author_function(text):
    match = re.search(author_regex, text)
    if match:
        return True
    else:
        return False

def message_function(text):
    match = re.search(message_regex, text)
    if match:
        return True
    else:
        return False


def author_split(text):
    text = text.split(': ', 1)
    if len(text) == 2:
        return True
    else:
        return False


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


with open(chat, 'r', encoding='utf-8-sig') as file:
    lines = file.readlines()
    for line in lines:
        if date_function(line) and time_function(line) and author_function(line) and message_function(line):
            line_split(line)
        else:
            error_list.append(line)

print(dict_list)
print(error_list)
