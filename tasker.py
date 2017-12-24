# Version: 21
# Date: 24.12.17
# Time: 12:02 GMT+5

# IMPORTS
import sqlite3
import sys
import re

# GLOBAL VARIABLES
testmode = 1    # if value == 1, then test block will be executed, 
                # otherwise not
command_list = ['add', 'quit']  # list of commands available,
                                # used in command_check_dictionary()


conn = sqlite3.connect('example.db')
c = conn.cursor()
c.execute('''pragma foreign_keys = on''')

# CREATING TABLES
c.execute('''CREATE TABLE IF NOT EXISTS notes (
        ID_note integer primary key, 
        note text)''')
c.execute('''CREATE TABLE IF NOT EXISTS tags (
        ID_tag integer primary key, 
        tag text)''')
c.execute('''CREATE TABLE IF NOT EXISTS notes_tags (
        ID_note integer not null,
        ID_tag integer not null,
        foreign key (ID_note) references notes(ID_note),
        foreign key (ID_tag) references tags(ID_tag),
        primary key (ID_note, ID_tag))''')
conn.commit()

# TEST BLOCK FOR TABLES
# test 1: table notes is functioning
if testmode == 1:
    try:
        c.execute("insert into notes VALUES (1, 'gogakal')")
        conn.commit()
    except:
        print('test 1 failed')
    else:
        c.execute("delete from notes")
        conn.commit()
        print('test 1 passed')

# test 2: in table notes ID_note is a primary key
if testmode == 1:
    try:
        c.execute("insert into notes VALUES(1, 'gogakal')")
        c.execute("insert into notes VALUES(1, 'gogakal2')")
        conn.commit()
    except:
        c.execute("delete from notes")
        print('test 2 passed')
    else:
        c.execute("delete from notes")
        conn.commit()
        print('test 2 failed')

# test 3: table tags is functioning
if testmode == 1:
    try:
        c.execute("insert into tags VALUES (1, 'o kale')")
        conn.commit()
    except:
        print('test 3 failed')
    else:
        c.execute("delete from tags")
        conn.commit()
        print('test 3 passed')

# test 4: in table tags ID_tag is a primary key
if testmode == 1:
    try:
        c.execute("insert into tags VALUES ('1, 'o kale')")
        c.execute("insert into tags VALUES ('1, 'o fekale')")
        conn.commit()
    except:
        print('test 4 passed')
    else:
        c.execute("delete from tags")
        conn.commit()
        print('test 4 failed')

# test 5: in table notes_tags both attributes goes with not null constraint
if testmode == 1:
    try:
        c.execute("""insert into notes_tags VALUES (null, null)""")
        conn.commit()
    except:
        print('test 5 passed')
    else:
        c.execute("delete from notes_tags")
        conn.commit()
        print('test 5 failed')

# test 6: table notes_tags is working in overall

if testmode == 1:
    try:
        c.execute("""insert into notes VALUES (1, 'goga')""")
        c.execute("""insert into tags VALUES (2, 'kal')""")
        c.execute("""insert into notes_tags VALUES (1, 2)""")
    except:
        print('test 6 failed')
    else:
        c.execute("delete from notes_tags")
        c.execute("delete from notes")
        c.execute("delete from tags")
        conn.commit()
        print('test 6 passed')

# test 7: in table notes_tags both attributes are foreign keys
if testmode == 1:
    try:
        c.execute("""insert into notes_tags VALUES (1, 2)""")
        conn.commit()
    except:
        print('test 7 passed')
    else:
        c.execute("delete from notes_tags")
        conn.commit()
        print('test 7 failed')

# test 8: in table notes_tags both attributes form a complex primary key
if testmode == 1:
    try:
        c.execute("""insert into notes VALUES (1, 'goga')""")
        c.execute("""insert into tags VALUES (2, 'kal')""")
        c.execute("""insert into notes_tags VALUES (1, 2)""")
        c.execute("""insert into notes_tags VALUES (1, 2)""")
        conn.commit()
    except:
        print('test 8 passed')
    else:
        c.execute("delete from notes_tags")
        c.execute("delete from notes")
        c.execute("delete from tags")
        print('test 8 failed')
        conn.commit()

# test_last: clearing tables
if testmode == 1:
    c.execute("delete from notes_tags")
    c.execute("delete from notes")
    c.execute("delete from tags")
    conn.commit()


# FUNCTIONS
# main functions
def initial_input_check(input_string):
    # The upper layer function, that checks if input is correct in overall.
    """
    >>> initial_input_check('tasker gogakal # ronyal, iskal')
    True

    >>> initial_input_check('tasker gogakal  ronyal, iskal')
    True

    >>> initial_input_check('tasker quit')
    True

    >>> initial_input_check('')
    False
    """
    check1 = re.compile('''
            (\w+\s*)+           # looking for at least one initial word
            [#]                 # looking for a hash symbol
            \s+                 # looking for at least one whitespace after hash symbol
            \w+                 # looking for at least one word after hash symbol (i.e. tag)
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

    
def chief_function(input_string):
    input_dictionary = convert_input_to_dictionary(input_string)
    if command_check_dictionary(input_dictionary) == False:
        print('Error: Wrong input string. To quit type: tasker quit')
    else:
        command = input_dictionary['command']
        if command == 'add':
            tasker_add(input_dictionary)
        if command == 'quit':
            tasker_quit(ask=1)


def tasker_add(input_dictionary):
    """
    >>> tasker_add({'beginning': 'tasker', 'command': 'add', 'note': 'gogakal', 'tags': ['ronyal', 'iskal', 'is kal']})
   
    >>> tasker_add({'beginning': 'tasker', 'command': 'add', 'note': 'gogakal', 'tags': []})
    'Error in task entered'

    >>> tasker_add({'beginning': 'tasker', 'command': 'add', 'note': '', 'tags': ['ronyal', 'iskal', 'is kal']})
    'Error in task entered'
    """
    if tasker_add_check(input_dictionary) is False:
        return('Error in task entered')  
    try:
        c.execute("""insert into notes VALUES (Null, ?)""", (input_dictionary['command'],))
        note_id_for_insertion = last_record_id('notes')
        for tag in input_dictionary['tags']:
            c.execute("""insert into tags VALUES (Null, ?)""", (tag,))
            tag_id_for_insertion = last_record_id('tags')
            c.execute("""insert into notes_tags VALUES (?, ?)""", 
                    (note_id_for_insertion, tag_id_for_insertion))
        a = c.execute("""SELECT * from notes""")
    except Warning:
        return('Error: Shit has happened')

def tasker_quit(ask=0):
    """
    1>>> tasker_quit(1)
    1Are you sure to quit? [y] [n] \n
    """
    if ask == 1:
        user_command = input('Are you sure to quit? [y] [n] \n')
        if user_command == 'y':
            sys.exit()
    else:
        sys.exit()



# auxiliary functions
def tasker_add_check(input_dictionary):
    """
    >>> tasker_add_check({'beginning': 'tasker', 'command': 'add', 'note': 'gogakal', 'tags': ['ronyal', 'iskal', 'is kal']})
    True

    >>> tasker_add_check({'beginning': 'tasker', 'command': 'add', 'note': '', 'tags': ['ronyal', 'iskal', 'is kal']})
    False

    >>> tasker_add_check({'beginning': 'tasker', 'command': 'add', 'note': 'gogakal', 'tags': []})
    False
    """
    # Step 0: checks if input contains necessary keys 'beginning', 'command'
    # are in the previous more general function - command_check_dictionary()
    # Step 1: check if note is entered
    if input_dictionary['note'] == '':
        return False
    # Step 2: check if at least one tag is entered
    if input_dictionary['tags'] == []:
        return False
    return True

def tasker_tags():
    #TODO write tests, see issue 20
    list_of_tags = c.execute("""SELECT tag FROM tags""")
    resulting_dictionary = {}
    for tag in list_of_tags:
        tag_id = return_tag_id(tag)
        number_of_notes = c.execute("""SELECT COUNT(*) FROM notes_tags WHERE                                        (ID_tag = ?)""", (tag_id))
        for item in number_of_notes:
            resulting_dictionary[tag[0]] = item[0]
    return(resulting_dictionary)
        
def return_tag_id(tag):
    #TODO write tests, see issue 21
    tag_id = c.execute("""SELECT ID_tag FROM tags WHERE (tag = ?)""", (tag))
    for item in tag_id:
        return(item)

def remove_doubled_tags(list_of_tags):
    """
    >>> remove_doubled_tags(['kal'])
    ['kal']

    >>> remove_doubled_tags(['kal', 'kal'])
    ['kal']

    """
    return list(set(list_of_tags))

def command_check_dictionary(input_dictionary):
    """
    >>> command_check_dictionary('gogakal # ronyal iskal')
    False

    >>> command_check_dictionary({'beginning': 'tasker', 'command': 'add', 'note': 'gogakal', 'tags': ['ronyal', 'iskal', 'is kal']})
    True

    >>> command_check_dictionary({'beginning': 'add', 'command': 'gogakal', 'note': '', 'tags': ['ronyal', 'iskal', 'is kal']})
    False

    >>> command_check_dictionary({'beginning': 'tasker', 'command': 'add1', 'note': 'gogakal', 'tags': ['ronyal', 'iskal', 'is kal']})
    False
    """
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

def last_record(table):
    #TODO deal with possible sql-injection in the function, see issue 22
    #TODO write tests, see issue 23
    resulting_last_record = c.execute("""select * from {table_name} 
            where ROWID = (SELECT MAX(ROWID) from {table_name})""".format
            (table_name=table))
    return(resulting_last_record)

def last_record_id(table):
    last_record_cursor = last_record(table)
    for item in last_record_cursor:
        return(item[0])

def return_tags(text):
    """
    >>> return_tags('goga, mnogo ,,  , kal iskal, ne')
    ['goga', 'mnogo', 'kal iskal', 'ne']

    >>> return_tags('goga, mnogo ,,  , kal iskal# ,# ne')
    ['goga', 'mnogo', 'kal iskal', 'ne']

    >>> return_tags('ronyal, iskal, # is kal')
    ['ronyal', 'iskal', 'is kal']
    """
    initial_list = text.split(',')
    return_list = []
    for tag in initial_list:
        if tag.isspace() == True or tag == '':
            pass
        else:
            tag_cleared_from_hashtags = re.sub('[#]', '', tag)
            return_list.append(tag_cleared_from_hashtags.strip())
    return(return_list)

def only_one_hash_check(input_string):
    #TODO merge with no_hash_check(), see issue 24
    check = re.compile('''[#]''')
    if len(check.findall(input_string)) == 1:
        return True
    else:
        return False

def no_hash_check(input_string):
    check = re.compile('''[#]''')
    if len(check.findall(input_string)) == 0:
        return True
    else:
        return False


def convert_input_to_dictionary(input_string):
    # the checks behind work poor as dictionaries are not sorted objects, so the order of keys is random. So I've triggered tests off
    """
    #>>> convert_input_to_dictionary('tasker add gogakal # ronyal, iskal , is kal')
    {'beginning': 'tasker', 'command': 'add', 'note': 'gogakal', 'tags': ['ronyal', 'iskal', 'is kal']}

    #>>> convert_input_to_dictionary('tasker')
    {'beginning': 'tasker', 'command': '', 'note': '', 'tags': []}

    #>>> convert_input_to_dictionary('tasker gogakal ronyal iskal')
    {'beginning': 'tasker', 'command': 'gogakal', 'note': 'ronyal iskal', 'tags': []}

    #>>> convert_input_to_dictionary(' tasker add gogakal # ronyal, iskal , # is kal')
    {'beginning': 'tasker', 'command': 'add', 'note': 'gogakal', 'tags': ['ronyal', 'iskal', 'is kal']}
    """
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
    if len(additional_list) > 1:
        resulting_dictionary['command'] = additional_list[1]
        resulting_dictionary['note'] = ''
        resulting_dictionary['tags'] = []
    if len(additional_list) > 2:
        resulting_dictionary['note'] = additional_list[2]
        resulting_dictionary['tags'] = []
    if no_hash_check(input_string) == False:
        resulting_dictionary['tags'] = return_tags(trailing_string)
    return(resulting_dictionary)

# TEST CYCLE
if __name__ == '__main__':
    if testmode == 1:
        import doctest
        doctest.testmod()


# MAIN CYCLE
    quit = 1
    while quit == 1:
        user_command = input('Enter command: ')
        if initial_input_check(user_command) == True: 
            chief_function(user_command)
        else:
            print('gogakal')
