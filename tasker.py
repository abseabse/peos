# Version: 42
# Date: 13.1.18
# Time: 15:10 GMT+5


# IMPORTS
import sqlite3
import sys
import re


# GLOBAL VARIABLES
testmode = 1    # if value == 1, then doctest blocks will be executed, 
                # otherwise not
command_list = ['add', 'quit', 'get', 'tags', 'rm']
    # list of commands available, used in command_check_dictionary()


# FUNCTIONS
# table functions
def create_tables(cursor, connection):
    # sevice function that creates tables in database 
    # or skips if the tables already exist.
    # tests are in tests.py
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
            ID_note integer primary key, 
            note text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tags (
            ID_tag integer primary key, 
            tag text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS notes_tags (
            ID_note integer not null,
            ID_tag integer not null,
            foreign key (ID_note) references notes(ID_note),
            foreign key (ID_tag) references tags(ID_tag),
            primary key (ID_note, ID_tag))''')
    connection.commit()

# main functions 
def chief_function(cursor, connection, input_string):
    # service function that parses user input 
    # and launches as appropriate command.
    #TODO think about adding tests, see issue #32
    input_dictionary = convert_input_to_dictionary(input_string)
    if command_check_dictionary(input_dictionary) == False:
        print('Error: Wrong input string. To quit type: tasker quit')
    else:
        command = input_dictionary['command']
        if command == 'quit':
            tasker_quit(input_dictionary)
        if command == 'add':
            tasker_add(cursor, connection, input_dictionary)
        if command == 'get':
            tasker_get(cursor, connection, input_dictionary)
        if command == 'tags':
            tasker_tags(cursor, connection, input_dictionary)
        if command == 'rm':
            tasker_rm(cursor, connection, input_dictionary)

def tasker_add(cursor, connection, input_dictionary):
    # function that adds new note.
    # tests are in tests.py
    if tasker_add_check(input_dictionary) is False:
        raise Warning('Shit has happened')
    try:
        cursor.execute("""insert into notes VALUES (Null, ?)""", 
                (input_dictionary['note'],))
        connection.commit()
        note_id_for_insertion = last_record_id(cursor, connection, 'notes')
        current_tags = return_tag_dictionary(cursor, connection)
        for tag in input_dictionary['tags']:
            if tag in current_tags:
                # there is [0] in the line below as return_tag_id() returns 
                # tuple (while integer is needed).
                tag_id_for_insertion = return_tag_id(
                        cursor, connection, tag)[0]
            else:
                cursor.execute("""insert into tags VALUES (Null, ?)""", 
                        (tag,)
                        )
                tag_id_for_insertion = last_record_id(
                        cursor, connection, 'tags'
                        )
            cursor.execute("""insert into notes_tags VALUES (?, ?)""", 
                    (note_id_for_insertion, tag_id_for_insertion)
                    )
            connection.commit()
    except Warning:
        return('Error: Shit has happened')

def tasker_get(cursor, connection, input_dictionary):
    # function that returns list of notes with tags from input.
    # tests are in tests.py
    list_of_notes_ID =  return_tags_intersection(
            cursor, connection, input_dictionary['tags']
            )
    if (input_dictionary['tags'] == []) and (list_of_notes_ID == []):
        result = cursor.execute('''SELECT * FROM notes''')
    else:
        # TODO four lines under this comment is somewhat messy. 
        # Perhaps, need to rewrite, see issue #47
        a = ""
        for item in list_of_notes_ID:
            a = a + str(item) + ", "
        a = a[:-2]
        result = cursor.execute(
                '''SELECT * FROM notes WHERE ID_note IN 
                ({list_to_apply})'''.format(list_to_apply=a)
                )
    # TODO remove mess in the function's end, see issue #44
    result_dictionary = {}
    for item in result:
        print(item[0], "-", item[1])
        result_dictionary[item[0]] = item[1]
    return result_dictionary

def tasker_rm(cursor, connection, input_dictionary):
    # function, that removes a note or a bunch of notes.
    # tests are in tests.py
    for item in input_dictionary['IDs']:
        # print(str(item)) # debugging
        cursor.execute(
                '''DELETE FROM notes_tags WHERE (ID_note = ?)''', 
                str(item)  
                )
        cursor.execute(
                '''DELETE FROM notes WHERE (ID_note = ?)''', 
                str(item)  
                )
        connection.commit()

def tasker_quit(input_dictionary):
    # function to quit.
    ask = input_dictionary['note']
    if ask == 'y':
        sys.exit()
    else:
        user_command = input('Are you sure to quit? [y] [n] \n')
        if user_command == 'y':
            sys.exit()


def tasker_tags(cursor, connection, input_dictionary):
    # function that returns a list of all the tags 
    # with notes quanitity accordingly.
    # tests are in tests.py
    # TODO remove mess in the function's end, see issue #44
    list_of_tags = return_tag_dictionary(cursor, connection)
    for key, value in list_of_tags.items():
        print(key+": ", value) 
    return list_of_tags

# auxiliary functions
def return_tags_intersection(cursor, connection, tag_list):
    # an auxiliary function that returns list of notes 
    # (in form of notes IDs) with the tag list provided.
    # tests are in tests.py
    common_list = []
    for tag in tag_list:
        notes_list =  return_notes(cursor, connection, tag)
        if notes_list == []:
            return []
        elif common_list == []:
            # there might be a problem: changes in notes_list can affect
            # common_list. TODO that thing should be tested.
            common_list = notes_list
        else:
            common_list = list(set(common_list)&set(notes_list))
            if common_list == []:
                return []
    return common_list

def return_notes(cursor, connection, tag):
    # an auxiliary function that returns list of notes with the tag provided
    # tests are in tests.py
    tag_id = return_tag_id(cursor, connection, tag)
    if tag_id is None:
        return []
    else:
        notes_cursor = cursor.execute(
                '''SELECT ID_note from notes_tags WHERE (ID_tag = ?)''', 
                (tag_id)
                )
        auxiliary_list = []
        for item in notes_cursor:
            auxiliary_list.append(item[0])
        connection.commit()
        return auxiliary_list

def tasker_add_check(input_dictionary):
    # an auxiliary function that perform input check for tasker_add()
    # tests are in tests.py
    # Step 0: checks if input contains necessary keys 'beginning', 'command'
    # are in the previous more general function - command_check_dictionary()
    # Step 1: check if note is entered
    if input_dictionary['note'] == '':
        return False
    # Step 2: check if at least one tag is entered
    if input_dictionary['tags'] == []:
        return False
    return True

def return_tag_dictionary(cursor, connection):
    # an auxiliary function that returns dictionary of tags.
    # tests are in tests.py
    list_of_tags = cursor.execute("""SELECT tag, count(*) 
            FROM notes_tags LEFT JOIN tags ON tags.ID_tag=notes_tags.ID_tag 
            GROUP BY notes_tags.ID_tag""")
    resulting_dictionary = {}
    for item, value in list_of_tags:
        resulting_dictionary[item] = value
    return(resulting_dictionary)

def return_tag_id(cursor, connection, tag):
    # an auxiliary function that returns tag ID for tag specified.
    # tests are in tests.py
    tag_id = cursor.execute(
            """SELECT ID_tag FROM tags WHERE (tag = ?)""", (tag,)
            )
    for item in tag_id:
        return item

def command_check_dictionary(input_dictionary):
    # an auxiliary function that performs initial check for chief_function().
    # tests are in tests.py
    # The first step: check if the type of the input is a dictionary
    if type(input_dictionary) != type({}):
        return(False)
    # The second step: check if the input contains all necessary elements:
    #   - beginning
    #   - command
    #   - note
    #   - tags
    if 'beginning' not in input_dictionary:
        return(False)
    if 'command' not in input_dictionary:
        return(False)
    if 'note' not in input_dictionary:
        return(False)
    if 'tags' not in input_dictionary:
        return(False)
    # The third step: check if input contains specific beginning 'tasker'
    if input_dictionary['beginning'] != 'tasker':
        return(False)
    # the fourth step: check if input contains actual command
    if input_dictionary['command'] not in command_list:
        return(False)
    return(True)

def last_record(cursor, connection, table):
    # an auxiliary function that returns the last record from table 
    # specified. Used indirectly in tasker_add().
    #TODO deal with possible sql-injection in the function, see issue 22
    #TODO write tests, see issue 23
    resulting_last_record = cursor.execute("""select * from {table_name} 
            where ROWID = (SELECT MAX(ROWID) from {table_name})""".format
            (table_name=table))
    return(resulting_last_record)

def last_record_id(cursor, connection, table):
    # an auxiliary function that returns the last record from table 
    # specified. Used directly in tasker_add().
    last_record_cursor = last_record(cursor, connection, table)
    for item in last_record_cursor:
        return(item[0])

def return_tags(text):
    # an auxiliary function, that returns list of tags from string. 
    # Used directly in convert_input_to_dictionary().
    # tests are in tests.py
    initial_list = text.split(',')
    return_list = []
    for tag in initial_list:
        if tag.isspace() == True or tag == '':
            pass
        else:
            tag_cleared_from_hashtags = re.sub('[#]', '', tag)
            return_list.append(tag_cleared_from_hashtags.strip())
    return(return_list)

def no_hash_check(input_string):
    # an auxiliary function, that determines if there is at least one 
    # hash sybol in input string. Used in convert_input_to_dictionary().
    check = re.compile('''[#]''')
    if len(check.findall(input_string)) == 0:
        return True
    else:
        return False

def convert_input_to_dictionary(input_string):
    # an auxiliary function, that converts user input to dictionary. 
    # Used directly in chief_function().
    # tests are in tests.py
    resulting_dictionary = {}
    if no_hash_check(input_string) == True:
        leading_string = input_string.strip().split(' ', 1)
        trailing_string = ''
    else:
        leading_string = input_string.split('#', 1)[0].strip().split(' ', 1)
        trailing_string = input_string.split('#', 1)[1]
    additional_list = []
    for item in leading_string:
        if len(item.split()) == 1:
            additional_list.append(item)
        else:
            auxiliary_list = item.split(' ', 1)
            for further_item in auxiliary_list:
                additional_list.append(str(further_item))
    resulting_dictionary['beginning'] = additional_list[0]
    resulting_dictionary['command'] = ''
    resulting_dictionary['note'] = ''
    resulting_dictionary['tags'] = []
    resulting_dictionary['IDs'] = []
    if len(additional_list) > 1:
        resulting_dictionary['command'] = additional_list[1]
    if len(additional_list) > 2:
        if check_if_note_contains_only_IDs(additional_list[2]) == False:
            resulting_dictionary['note'] = additional_list[2]          
        else:
            resulting_dictionary['IDs'] = return_IDs(additional_list[2])
    if no_hash_check(input_string) == False:
        resulting_dictionary['tags'] = return_tags(trailing_string)
    return(resulting_dictionary)

def return_IDs(input_string):
    # an auxiliary function that returns a list of ID's (notes or tags).
    # the function is vulnerable for inputs like '1d', each item 
    # after splitting the input_string should be convertable to integer
    # otherwise it will be skipped.
    # Used directly in convert_input_to_dictionary().
    # tests are in tests.py
    clean_list = []
    messy_list = input_string.split(',')
    check1 = re.compile('''\s*[\d+]\s*''')
    check2 = re.compile('''^\d+$''')
    for item in messy_list:
        check1_result = check1.match(item)
        if check1_result is not None:
            messy_item = item.strip()
            check2_result = check2.match(messy_item)
            if check2_result is not None:
                clean_item = int(messy_item)
                clean_list.append(clean_item)
    return clean_list

def check_if_note_contains_only_IDs(input_string):
    # an auxiliary function that checks if the input string contains 
    # notes only.
    # Used directly in convert_input_to_dictionary().
    # tests are in tests.py
    initial_list = input_string.split(",")
    initial_list_is_correct = False
    for item in initial_list:
        check1 = re.compile('''\s*[\d+]\s*''')
        check2 = re.compile('''\s*[\d+]\s+\S+''')
        check1_result = check1.match(item)
        check2_result = check2.match(item)
        if (check1_result is not None) and (check2_result is None):
            initial_list_is_correct = True
    if initial_list_is_correct:
        return True
    else:
        return False        

def initial_input_check(input_string):
    # The upper layer function, that checks if the input 
    # is correct in overall.
    # Used directly in the main cycle.
    # tests are in tests.py
    check1 = re.compile('''
            (\w+\s*)+           # looking for at least one initial word;
            [#]                 # looking for a hash symbol;
            \s+                 # looking for at least one whitespace 
                                # after hash symbol;
            \w+                 # looking for at least one word after 
                                # hash symbol (i.e. tag).
            ''', re.VERBOSE)

    check2 = re.compile('''
            (\w+\s*)+           # looking for at least one initial word
            ''', re.VERBOSE)
    check1_result = check1.match(input_string)
    check2_result = check2.match(input_string)
    if (check1_result is not None) or (check2_result is not None):
        return True
    else:
        return False

# auxiliary functions for test purpose only (used only in doctests and
# unittests)
def clear_all(cursor, connection):
    # nuclear-type function that erases all the entered notes and tags
    # tests are in tests.py
    cursor.execute('''DELETE FROM notes_tags''')
    cursor.execute('''DELETE FROM notes''')
    cursor.execute('''DELETE from tags''')
    connection.commit()

def drop_tables(cursor, connection):
    # nuclear-type function that drops all the tables in the database.
    # (need to perform tests in test.py module).
    cursor.execute('''DROP TABLE notes_tags''')
    cursor.execute('''DROP TABLE notes''')
    cursor.execute('''DROP TABLE tags''')
    connection.commit()


# TEST CYCLE
if __name__ == '__main__':
    if testmode == 1:
        # TODO remove doubling of the code 
        # (the same lines are in the main cycle). See issue #39.
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('''pragma foreign_keys = on''')
        create_tables(c, conn)
        quit = 1 
        import doctest
        doctest.testmod()


# MAIN CYCLE
if __name__ == '__main__':
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute('''pragma foreign_keys = on''')
    create_tables(c, conn)
    quit = 1
    while quit == 1:
        user_command = input('Enter command: ')
        if initial_input_check(user_command) == True: 
            chief_function(c, conn, user_command)
        else:
            print('gogakal')
