# Version: 63
# Date: 13.02.18
# Time: 21:24 GMT+5


# IMPORTS
import sqlite3
import sys
import re
import curses


# GLOBAL VARIABLES
testmode = 1    # if value == 1, then doctest blocks will be executed, 
                # otherwise not
command_list = ['add', 'quit', 'get', 'tags', 'rm', 'ch', 'export']
    # list of commands available, used in command_check_dictionary()
export_file = 'notes.txt' # filename to export notes

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
    # Used directly in the main cycle.
    # tests are in tests.py
    # TODO not all tests can be completed: for commands tasker_get() and
    # tasker_tags() I use curses and stdscr is not initialized in tests.py
    # so these tests are omitted. Don't know how to implement them, will
    # do later. See issue #81
    input_dictionary = convert_input_to_dictionary(input_string)
    if command_check_dictionary(input_dictionary) == False:
        return None
    else:
        command = input_dictionary['command']
        if command == 'quit':
            tasker_quit(input_dictionary)
            return True
        if command == 'add':
            tasker_add(cursor, connection, input_dictionary)
        if command == 'get':
            return tasker_get(cursor, connection, input_dictionary)
        if command == 'tags':
            return tasker_tags(cursor, connection, input_dictionary)
        if command == 'rm':
            tasker_rm(cursor, connection, input_dictionary)
        if command == 'ch':
            tasker_ch(cursor, connection, input_dictionary)
        if command == 'export':
            tasker_export(cursor, connection)
            return True

def tasker_add(cursor, connection, input_dictionary):
    # function that adds new note.
    # tests are in tests.py
    if tasker_add_check(input_dictionary) is False:
        print('Not enough parameters are entered')
        return('Error')
    else:
        try:
            if input_dictionary['note'] != '':
                cursor.execute("""insert into notes VALUES (Null, ?)""", 
                        (input_dictionary['note'],))
                connection.commit()
                note_id_for_insertion = (last_record_id_notes(
                                            cursor, 
                                            connection),)
                tags_for_insertion = input_dictionary['tags']
                add_tags_to_note(
                        cursor, 
                        connection, 
                        note_id_for_insertion,
                        tags_for_insertion
                        )
            else:
                add_tags(cursor, connection, input_dictionary['tags'])
        except Warning:
            return('Error in tasker_add()')

def tasker_get(cursor, connection, input_dictionary):
    # function that returns list of notes with tags from input.
    # tests are in tests.py
    list_of_notes_ID =  return_tags_intersection(
            cursor, connection, input_dictionary['tags']
            )
    if (input_dictionary['tags'] == []) and (list_of_notes_ID == []):
        result = cursor.execute('''SELECT * FROM notes''')
    else:
        a = ""
        for item in list_of_notes_ID:
            a = a + str(item) + ", "
        a = a[:-2]
        result = cursor.execute(
                '''SELECT * FROM notes WHERE ID_note IN 
                ({list_to_apply})'''.format(list_to_apply=a)
                )
    result_dictionary = {}
    for item in result:
        result_dictionary[str(item[0])] = item[1]
    return result_dictionary

def tasker_rm(cursor, connection, input_dictionary):
    # function, that removes a note or a bunch of notes.
    # tests are in tests.py
    for item in input_dictionary['IDs']:
        cursor.execute(
                '''DELETE FROM notes_tags WHERE (ID_note = ?)''', 
                (str(item),)  
                )
        cursor.execute(
                '''DELETE FROM notes WHERE (ID_note = ?)''', 
                (str(item),)  
                )
        connection.commit()

def tasker_quit(input_dictionary):
    # function to quit.
    ask = input_dictionary['note']
    if ask == 'y':
        sys.exit()
    else:
        command_win.addstr(2,0, 'Are you sure to quit? [y] [n]')
        current_cursor_position = curses.getsyx()
        user_command = command_win.getstr(current_cursor_position[0]+1, 0)
        if user_command.decode() == 'y':
            curses.endwin()
            sys.exit()

def tasker_tags(cursor, connection, input_dictionary):
    # function that returns a list of all the tags 
    # with notes quanitity accordingly.
    # tests are in tests.py
    list_of_used_tags = return_used_tag_dictionary(cursor, connection)
    dictionary_of_tags = {}
    for key, value in list_of_used_tags.items():
        dictionary_of_tags[key] = str(value)
    cursor_tags = cursor.execute("""SELECT tag from tags""")
    for item in cursor_tags:
        if item[0] not in list_of_used_tags:
            dictionary_of_tags[item[0]] = '0'
    return dictionary_of_tags

def tasker_ch(cursor, connection, input_dictionary):
    # function that changes the note and its tags if specified
    # tests are in tests.py
    if initial_check_tasker_ch(
            cursor, connection, input_dictionary
            ) == False:
        print('Initial check for tasker ch failed')    
    else:
        try:
            # Step 0: Change the text of the note
            if input_dictionary['extra note'] != '':
                tuple_to_substitute = (
                    input_dictionary['extra note'], 
                    str(input_dictionary['IDs'][0])
                    )
                cursor.execute(
                    '''UPDATE notes set note = (?) WHERE ID_note = (?)''', 
                    (tuple_to_substitute))
                connection.commit()
            # Step 1: Change the tags of the note
            if input_dictionary['hashtag'] == 1:
                note_id = input_dictionary['IDs']
                # Step 1.1: Delete all the tags if they are 
                # not provided at all
                if input_dictionary['tags'] == []:
                    cursor.execute('''DELETE FROM notes_tags 
                                      WHERE ID_note = (?)''', note_id)
                    connection.commit()
                else:
                    # Step 1.2: select odd tags
                    tags_to_delete = []
                    tuple_of_tags = cursor.execute(
                    '''SELECT tag FROM notes_tags 
                       LEFT JOIN tags 
                       ON tags.ID_tag = notes_tags.ID_tag
                       WHERE notes_tags.ID_note = (?)''', 
                       note_id).fetchall()
                    for item in tuple_of_tags:
                        if item[0] not in input_dictionary['tags']:
                            tags_to_delete.append(item[0])
                    # Step 1.3: delete odd tags
                    delete_tags_from_note(
                            cursor, 
                            connection, 
                            note_id, 
                            tags_to_delete
                            )
                    # Step 1.3: add new tags
                    add_tags_to_note(
                            cursor, 
                            connection, 
                            note_id, 
                            input_dictionary['tags']
                            )
            else:
                pass
        except Warning:
            print('Error in tasker_ch')

def tasker_export(cursor, connection):
    # function that export all the notes to txt.file
    # TODO write tests for tasker_export(), see issue #77
    notes_to_export = tasker_get(cursor, connection, {'tags': []})
    with open (export_file, 'w') as notes_export_file:
        for item in notes_to_export:
            string_to_write = item + ' ' + notes_to_export[item] + '\n'
            notes_export_file.write(string_to_write)

# AUXILIARY FUNCTIONS
def add_tags(cursor, connection, tags):
    # function that enters new tags into table tags. Tags already entered
    # are omitted. Used directly in tasker_add()
    # tests are in tests.py
    # Step 0: get the list of tags not in the base
    cursor_tags = cursor.execute("""SELECT tag from tags""")
    auxiliary_list = []
    for item in cursor_tags:
        auxiliary_list.append(item[0])
    list_difference = list(set(tags) - set(auxiliary_list))
    for item in list_difference:
        cursor.execute("""INSERT INTO tags VALUES (Null, ?)""", (item,))
        connection.commit()

def add_tags_to_note(cursor, connection, note_id, tags):
    # an auxiliary function that adds tags to the note specified.
    # Used directly in tasker_add() and tasker_ch().
    # tests are in tests.py
    # Step 1: form lists of tags to add
    tags_to_add = []
    tuple_of_tags = cursor.execute(
    '''SELECT tag FROM notes_tags 
       LEFT JOIN tags 
       ON tags.ID_tag = notes_tags.ID_tag
       WHERE notes_tags.ID_note = (?)''', note_id).fetchall()
    for tag in tags:
        if (tag,) not in tuple_of_tags:
            tags_to_add.append(tag)
    # Step 2: add new tags
    for tag in tags_to_add:
        # Step 2.1: check if tag is completely new and
        # add it to table tags in that case
        current_tags_in_base = []
        list_of_tags = cursor.execute("""SELECT tag from tags""")
        for item in list_of_tags:
            current_tags_in_base.append(item[0])
        if tag in current_tags_in_base:
            pass
        else:
            cursor.execute('''
                INSERT INTO tags
                VALUES (Null, ?)''', (tag,))
            connection.commit()
        # Step 2.2: connect the note to the tag
        tag_id_to_add = return_tag_id(
                        cursor, connection, tag)
        tuple_to_add = (str(note_id[0]), str(tag_id_to_add[0]))
        cursor.execute('''
            INSERT INTO notes_tags
            VALUES (?, ?)''', tuple_to_add)
        connection.commit()

def delete_tags_from_note(cursor, connection, note_id, tags):
    # an auxiliary function that adds tags to the note specified.
    # Used directly in tasker_ch().
    # tests are in tests.py
    # Step 1: form lists of tags to delete
    tags_to_delete = []
    tuple_of_tags = cursor.execute(
    '''SELECT tag FROM notes_tags 
       LEFT JOIN tags 
       ON tags.ID_tag = notes_tags.ID_tag
       WHERE notes_tags.ID_note = (?)''', note_id).fetchall()
    for item in tuple_of_tags:
        if item[0] in tags: # maybe to revert the function
            tags_to_delete.append(item[0])
    # Step 2: delete odd tags
    for tag in tags_to_delete:
        tag_id_to_delete = return_tag_id(
                            cursor, connection, tag)
        tuple_to_delete = (str(note_id[0]), str(tag_id_to_delete[0]))
        cursor.execute('''
            DELETE FROM notes_tags
            WHERE ID_note = (?)
            AND ID_tag = (?)''', tuple_to_delete)
        connection.commit()

def initial_check_tasker_ch(cursor, connection, input_dictionary):
    # auxiliary function for tasker_ch() that checks if all the 
    # necessary parameters are entered. Used directly in tasker_ch().
    # tests are in tests.py
    # Check, that ID is entered and its exactly one value (not many)
    if 'IDs' in input_dictionary:
        if len(input_dictionary['IDs']) != 1:
            return False 
    else:
        return False
    # Check if there is a note with the ID given
    note_id_to_seek = input_dictionary['IDs']
    cursor.execute('''SELECT * 
                      FROM notes 
                      WHERE ID_note = (?)''', note_id_to_seek)
    if cursor.fetchone() is None:
        return False
    # Check that key 'hashtag' exists
    if 'hashtag' not in input_dictionary:
        return False
    return True

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
            # common_list. TODO that thing should be tested, write additional
            # tests, see issue #82
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
    # an auxiliary function that perform input check for tasker_add().
    # Used in tasker_add().
    # tests are in tests.py
    # Step 0: checks if input contains necessary keys 'beginning', 'command'
    # are in the previous more general function - command_check_dictionary()
    # Step 1: check if note and tags are entered both
    if (input_dictionary['note'] == '') and (input_dictionary['tags'] == []):
        return False
    # Step 2: check if at least one tag is entered
    return True

def return_used_tag_dictionary(cursor, connection):
    # an auxiliary function that returns dictionary of tags.
    # Used directly in tasker_tags().
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

def last_record_notes(cursor, connection):
    # an auxiliary function that returns the last record from table 
    # notes. Used indirectly in tasker_add().
    resulting_last_record = cursor.execute("""select * from notes 
            where ROWID = (SELECT MAX(ROWID) from notes)""")
    return(resulting_last_record)

def last_record_id_notes(cursor, connection):
    # an auxiliary function that returns the last record from table 
    # notes. Used directly in tasker_add().
    last_record_cursor = last_record_notes(cursor, connection)
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
    resulting_dictionary['extra note'] = ''
    resulting_dictionary['tags'] = []
    resulting_dictionary['IDs'] = []
    resulting_dictionary['hashtag'] = 0
    if len(additional_list) > 1:
        resulting_dictionary['command'] = additional_list[1]
    if len(additional_list) > 2:
        if check_if_note_contains_only_IDs(additional_list[2]) == False:
            # transform input_dictionary if case of command 'ch' (changing
            # note)
            if resulting_dictionary['command'] == 'ch':
                splitted_note = additional_list[2].split(' ', 1)
                check1 = re.compile('''\d+''')
                check2 = re.compile('''\D+''')
                result_check1 = check1.search(splitted_note[0])
                result_check2 = check2.search(splitted_note[0])
                if (result_check1 is not None) and (
                        result_check2 is None):
                    resulting_dictionary['IDs'] = return_IDs(
                        splitted_note[0].strip()
                        )
                    resulting_dictionary['extra note'] = splitted_note[1]
                else:
                    resulting_dictionary['note'] = additional_list[2]
            else:
                resulting_dictionary['note'] = additional_list[2]          
        else:
            resulting_dictionary['IDs'] = return_IDs(additional_list[2])
    if no_hash_check(input_string) == False:
        resulting_dictionary['tags'] = return_tags(trailing_string)
        resulting_dictionary['hashtag'] = 1
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
    # Step 0: check if input string is empty
    check_string = input_string.strip()
    if check_string == '':
        return False 
    # Step 1: item examination if input string contains something
    initial_list = input_string.split(",") 
    at_least_one_incorrect_item = False
    at_least_one_integer = False
    check1 = re.compile('''\d+''')
    check2 = re.compile('''\D+''')
    for item in initial_list:
        clean_item = item.strip()
        if clean_item == '':
            pass
        else:
            check1_result = check1.search(clean_item)
            check2_result = check2.search(clean_item)
            if (check1_result is not None) and (check2_result is None):
                at_least_one_integer = True
            else:
                at_least_one_incorrect_item = True
    if at_least_one_incorrect_item:
        return False
    elif at_least_one_integer:
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

def slicing(string_to_slice, restriction):
    # auxiliary function to print dictionaries. 
    # Used in the main cycle directly.
    # this function requires the global paremeter 'strings'
    # to be executed properly
    if len(string_to_slice) < restriction:
        if string_to_slice != '':
            strings.append(string_to_slice)
    else:
        strings.append(string_to_slice[:restriction])
        slicing(string_to_slice[restriction:], restriction)


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


# MAIN CYCLE
if __name__ == '__main__':
    conn = sqlite3.connect('example.db')
    c = conn.cursor()
    c.execute('''pragma foreign_keys = on''')
    create_tables(c, conn)
    quit = 1
    current_cursor_position_y = 0
    max_cursor_position_y = 24
    stdscr = curses.initscr()
    command_win = curses.newwin(
                        5, 80, 
                        0, 0)
    # TEST CYCLE
    if testmode == 1:
        import doctest
        doctest.testmod()
        command_win.addstr('press any key to leave testmod')
        command_win.getkey()
    

    while quit == 1:
        curses.curs_set(1)
        # Step 0: Requesting input 
        command_win.clear()
        command_win.addstr(0, 0, 'Enter command:')
        byte_user_command = command_win.getstr(1, 0)
        user_command = byte_user_command.decode()
        current_cursor_position_y += 2
        if initial_input_check(user_command) == True:
            result = chief_function(c, conn, user_command)
            if result == None: # branch for functions that returns None,
                               # see chief_function() for details.
                command_win.addstr(3, 0,
                        'Wrong input. To quit type: tasker quit')
                command_win.refresh()
                command_win.getkey()
            elif type(result) == type({}):
                # branch for functions that return dictionaries.
                # Step 0: initializing variables and windows used for 
                # output.
                # stdscr.refresh()
                lines_max = 20
                start_line_for_win = 5 
                first_win = curses.newwin(
                        lines_max, 20, 
                        start_line_for_win, 0)
                second_win = curses.newwin(
                        lines_max, 20, 
                        start_line_for_win, 21)
                # Legend:
                # 1. Number of lines
                # 2. Number of columns (width)
                # 3. Begin y
                # 4. Begin x
                current_cursor_position_y = 0
                for item in result:
                    # Step 1: define number of lines in output
                    strings = []
                    slicing(item, 20)
                    lines_counter = len(strings)
                    strings = []
                    slicing(result[item], 20)
                    if len(strings) > lines_counter:
                        lines_counter = len(strings)
                    # Step 1.0: Check if allowed number of strings reached
                    #           and refresh the screen accordingly
                    if (current_cursor_position_y + 
                       lines_counter) >= lines_max-1:
                        first_win.refresh()
                        second_win.refresh()
                        command_win.addstr(
                            3, 
                            0, 
                            str('press any key to continue...'))
                        command_win.getkey()
                        # The addstr under deletes the 'press any key ...' 
                        # on the screen. Ugly.
                        command_win.addstr(
                            3, 
                            0, 
                            str('                            '))
                        first_win.clear()
                        second_win.clear()
                        current_cursor_position_y = 0
                    # Step 2: adding strings to the first column
                    strings = []
                    slicing(item, 20)
                    current_line_number = 0
                    for resulting_item in strings:
                        first_win.addstr(
                            current_cursor_position_y+current_line_number, 0,
                            resulting_item)
                        current_line_number += 1
                    # Step 2.0: adding empty strings if number of 
                    #           added lines is smaller than the maximum 
                    #           lines number
                    # TODO that piece of code is a bit ugly, 
                    # maybe, rewrite it? See issue #83
                    while current_line_number < lines_counter:
                        first_win.addstr(' '*20)        
                        current_line_number += 1
                    # Step 3: adding strings to the second column
                    strings = []
                    slicing(result[item], 20)
                    current_line_number = 0
                    for resulting_item in strings:
                        second_win.addstr(
                            current_cursor_position_y+current_line_number, 
                            0, 
                            resulting_item)
                        current_line_number += 1
                    # Step 3.0: adding empty strings if 
                    #           number of added lines is smaller
                    #           than the maximum lines number
                    while current_line_number < lines_counter:
                        second_win.addstr(' '*20)
                        current_line_number += 1
                    # Step 4: updating counter of initial position y 
                    #         for the next value not to override current
                    current_cursor_position_y += lines_counter
                first_win.refresh()
                second_win.refresh()
                curses.curs_set(0)
                command_win.refresh()
                command_win.getkey()

            else:
                pass    # TODO the place for future list-of-the-lists code
                        # see issue #84.
        else:
            command_win.addstr(3, 0, 
                    'Wrong input. To quit type: tasker quit')
            command_win.getkey()
