# Version: 16
# Date: 20.12.17
# Time: 21:38 GMT+5

# IMPORTS
import sqlite3
import sys
import re

# GLOBAL VARIABLES
testmode = 1    # if value == 1, then test block will be executed, otherwise not
quit = 1


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
    if input_dictionary['beginning'] == 'tasker':
        command = input_dictionary['command']
        if command == 'add':
            # TODO change to passing input_dictionary to tasker add command instead of passing string
            tasker_add(input_dictionary)
        elif command == 'quit':
            tasker_quit(ask=1)
        else:
            print('No such a command!')
    else:
        print('Error!')


def tasker_add(input_dictionary):
    """
    >>> tasker_add('tasker # #')
    'Error: Wrong task name'
    """
    if command_check(task) is False:
        return('Error: Wrong task name')  
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
        return('Error: Shit have happened')

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
def tasker_tags():
    #TODO write tests
    list_of_tags = c.execute("""SELECT tag FROM tags""")
    resulting_dictionary = {}
    for tag in list_of_tags:
        tag_id = return_tag_id(tag)
        number_of_notes = c.execute("""SELECT COUNT(*) FROM notes_tags WHERE                                        (ID_tag = ?)""", (tag_id))
        for item in number_of_notes:
            resulting_dictionary[tag[0]] = item[0]
    return(resulting_dictionary)
        
def return_tag_id(tag):
    #TODO write a test
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

def command_check(command):
    #TODO there is a bug! see the test #2 (right command should be 'tasker add gogakal # ronyal, iskal' (missing word 'add'))
    """
    >>> command_check('gogakal # ronyal iskal')
    False

    >>> command_check('tasker gogakal # ronyal iskal')
    True
    
    >>> command_check('  tasker gogakal # ronyal iskal')
    True

    >>> command_check('  taskergogakal # ronyal iskal')
    False

    >>> command_check('  tasker   gogakal # ronyal iskal')
    True

    >>> command_check('  tasker   gogakal  gogakal   # ronyal iskal')
    True
    
    >>> command_check('  tasker   gogakal ## ronyal iskal')
    False

    >>> command_check('  tasker   gogakal # # ronyal iskal')
    False

    >>> command_check('  tasker   gogakal # ronyal, iskal')
    True

    >>> command_check('  tasker   gogakal # ronyal, iskal # kal')
    False

    >>> command_check('  tasker   gogakal #')
    False

    >>> command_check('  tasker   gogakal # ')
    False
    """
    check1 = re.compile('''[#]''')
    check2 = re.compile('''
            ^\s*                # skipping leading whitespaces
            tasker              # looking for the initial command
            \s+                 # skipping trailing whitespaces
            (\w*\s)+            # skipping note string 
            [#]{1}              # looking for one hash symbol 
            \s+                 # looking for trailing whitespaces
            \w                  # looking for at least 1 tag
            ''', re.VERBOSE)
    if (len(check1.findall(command))>1) or (check2.match(command) is None):
        return False
    else:
        return True


def last_record(table):
    #TODO deal with possible sql-injection in the function
    #TODO write a test
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
    #TODO merge with no_hash_check()
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
    # the checks behind work poor as dictionaries are not sorted objects, so the order of keys is random. So I've triggered them off
    """
    >>> convert_input_to_dictionary('tasker add gogakal # ronyal, iskal , is kal')
    {'beginning': 'tasker', 'command': 'add', 'note':'gogakal', 'tags': ['ronyal', 'iskal', 'is kal']}

    >>> convert_input_to_dictionary('tasker')
    {'beginning': 'tasker','command': '', 'note':'', 'tags': []}

    >>> convert_input_to_dictionary('tasker gogakal ronyal iskal')
    {'beginning': 'tasker', 'command': 'gogakal', 'note': 'ronyal iskal', 'tags': []}

    >>> convert_input_to_dictionary(' tasker add gogakal # ronyal, iskal , # is kal')
    {'beginning': 'tasker', 'command': 'add', 'note': 'gogakal', 'tags': ['ronyal', 'iskal', 'is kal']}
    """
    resulting_dictionary = {}
    if no_hash_check(input_string) == True:
        leading_list = input_string.split()
        resulting_dictionary['beginning'] = leading_list[0]
    else:
        list_separated_by_hash = input_string.strip().split('#', 1)
        leading_string = list_separated_by_hash[0]
        #FIXME the split below is corrupted (commmented out that line of code and try something new instead (up to the first if statement))
        # leading_list = leading_string.strip().split(' ', 1)
        leading_list = leading_string.strip().split(' ', 1)
        print('initial list ', leading_list)
        i = 0
        for item in leading_list:
            leading_list[0] = item.strip().split(' ', 1)
            i = i + 1
            # print('item', item)
        print('aftewards list ', leading_list)
        resulting_dictionary['beginning'] = leading_list[0]
    if len(leading_list) == 0:
        resulting_dictionary['command'] = ''
        resulting_dictionary['note'] = ''
    elif len(leading_list) == 1:
        resulting_dictionary['command'] = '' 
        resulting_dictionary['note'] = ''
    elif len(leading_list) == 2:
        resulting_dictionary['command'] = leading_list[1] 
        resulting_dictionary['note'] = ''
    else:
        resulting_dictionary['command'] = leading_list[1]
        resulting_dictionary['note'] = leading_list[2:]
    if no_hash_check(input_string) == False:
        trailing_string = list_separated_by_hash[1]
        resulting_dictionary['tags'] = return_tags(trailing_string)
    else:
        resulting_dictionary['tags'] = []
    return(resulting_dictionary)


# TEST CYCLE
if __name__ == '__main__':
    if testmode == 1:
        import doctest
        doctest.testmod()


# MAIN CYCLE
    while quit == 1:
        user_command = input('Enter command: ')
        if initial_input_check(user_command) == True:
            
            chief_function(user_command)
        else:
            print('gogakal')
