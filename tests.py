# Version: 12
# Date: 13.1.18
# Time: 4:02 GMT+5


# IMPORTS
import unittest
import tasker
import sqlite3


# CREATING MOCK DATABASE, CONNECTION AND CURSOR FOR TESTING PURPOSES
test_connection = sqlite3.connect(":memory:")
test_cursor = test_connection.cursor()
test_cursor.execute('''pragma foreign_keys = on''')


# TEST BLOCK
class TestTables(unittest.TestCase):
    # tests for create_tables() in tasker.py
    
    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_table_notes(self):
    # test if table notes is functioning
        test_cursor.execute("insert into notes VALUES (1, 'gogakal')")
        test_connection.commit()

    def test_table_notes_ID_note_is_a_primary_key(self):
    # test if in table notes ID_note is a primary key
        test_cursor.execute("insert into notes VALUES(1, 'gogakal')")
        with self.assertRaises(sqlite3.IntegrityError):
            test_cursor.execute("insert into notes VALUES(1, 'gogakal2')")
        test_connection.commit()

    def test_table_tags(self):
    # test if table tags is functioning
        test_cursor.execute("insert into tags VALUES (1, 'o kale')")
        test_connection.commit()

    def test_table_tags_ID_tag_is_a_primary_key(self):
    # test if in table tags ID_tag is a primary key
        test_cursor.execute("insert into tags VALUES (1, 'o kale')")
        with self.assertRaises(sqlite3.IntegrityError):
            test_cursor.execute("insert into tags VALUES (1, 'o fekale')")
        test_connection.commit()

    def test_table_notes_tags_is_functioning(self):
    # tests if the table notes_tags is functioning
        test_cursor.execute("""insert into notes VALUES (1, 'goga')""")
        test_cursor.execute("""insert into tags VALUES (2, 'kal')""")
        test_cursor.execute("""insert into notes_tags VALUES (1, 2)""")
        test_connection.commit()

    def test_table_notes_tags_not_null_constraint(self):
    # tests if in table notes_tags both attributes goes with
    # not null constraint
        with self.assertRaises(sqlite3.IntegrityError):
            test_cursor.execute("""insert into notes_tags VALUES (null, null)""")
        test_connection.commit()

    def test_table_notes_tags_foreign_keys(self):
    # tests if both attributes in the table notes_tags are foreign keys
        with self.assertRaises(sqlite3.IntegrityError):
            test_cursor.execute("""insert into notes_tags VALUES (1, 2)""")
        test_connection.commit()

    def test_table_notes_tags_complex_primary_key(self):
        with self.assertRaises(sqlite3.IntegrityError):
            test_cursor.execute("""insert into notes VALUES (1, 'goga')""")
            test_cursor.execute("""insert into tags VALUES (2, 'kal')""")
            test_cursor.execute("""insert into notes_tags VALUES (1, 2)""")
            test_cursor.execute("""insert into notes_tags VALUES (1, 2)""")
        test_connection.commit()


class Test_initial_input_check(unittest.TestCase):
    # tests for initial_input_check in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        self.assertTrue(
                tasker.initial_input_check('tasker gogakal # ronyal, iskal')
                )

    def test_two(self):
        self.assertTrue(
                tasker.initial_input_check('tasker gogakal  ronyal, iskal')
                )

    def test_three(self):
        self.assertTrue(
                tasker.initial_input_check('tasker quit')
                )

    def test_four(self):
        self.assertFalse(
                tasker.initial_input_check('')
                )


class Test_tasker_add(unittest.TestCase):
    # tests for tasker_add() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        tasker.tasker_add(test_cursor, test_connection,
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal', 'is kal', 'o kale']}
                )
        self.assertEqual(
                tasker.return_tag_dictionary(test_cursor, test_connection), {'ronyal': 1, 'iskal': 1, 'is kal': 1, 'o kale': 1}
                )

    def test_two(self):
        with self.assertRaises(Warning): 
            tasker.tasker_add(test_cursor, test_connection,
                    {'beginning': 'tasker', 
                     'command': 'add', 
                     'note': 'gogakal', 
                     'tags': []}
                    )

    def test_three(self):
        with self.assertRaises(Warning): 
            tasker.tasker_add(test_cursor, test_connection,
                    {'beginning': 'tasker', 
                     'command': 'add', 
                     'note': '', 
                     'tags': ['ronyal', 'iskal', 'is kal']}
                    )


class Test_tasker_add_check(unittest.TestCase):
    # tests for tasker_add_check() in tasker.py
    
    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        self.assertTrue(
                tasker.tasker_add_check(
                    {'beginning': 'tasker', 
                     'command': 'add', 
                     'note': 'gogakal', 
                     'tags': ['ronyal', 'iskal', 'is kal']})
                )
    
    def test_two(self):
        self.assertFalse(
                tasker.tasker_add_check(
                    {'beginning': 'tasker', 
                     'command': 'add', 
                     'note': '', 
                     'tags': ['ronyal', 'iskal', 'is kal']})
                )
    
    def test_three(self):
        self.assertFalse(
                tasker.tasker_add_check(
                    {'beginning': 'tasker', 
                     'command': 'add', 
                     'note': 'gogakal', 
                     'tags': []})
                )


class Test_return_tag_dictionary(unittest.TestCase):
    # tests for return_tag_dictionary() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        self.assertEqual(
                tasker.return_tag_dictionary(test_cursor, test_connection), 
                {}
                )

    def test_two(self):
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['iskal', 'ronyal', 'is kal']}
                )
        self.assertEqual(
                tasker.return_tag_dictionary(test_cursor, test_connection),
                {'ronyal': 1, 'iskal': 1, 'is kal': 1}
                )


class Test_return_tag_id(unittest.TestCase):
    # tests for return_tag_id() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['iskal', 'ronyal', 'is kal']}
                )
        self.assertEqual(
                tasker.return_tag_id(
                    test_cursor, test_connection, 'iskal'
                    ), 
                (1,)
                )
        self.assertEqual(
                tasker.return_tag_id(
                    test_cursor, test_connection, 'ronyal'
                    ), 
                (2,)
                )
        self.assertEqual(
                tasker.return_tag_id(
                    test_cursor, test_connection, 'is kal'
                    ), 
                (3,)
                )
        self.assertEqual(
                tasker.return_tag_id(
                    test_cursor, test_connection, 'is kal1'
                    ), 
                None
                )


class Test_command_check_dictionary(unittest.TestCase):
    # tests for command_check_dictionary() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        self.assertFalse(
                tasker.command_check_dictionary('gogakal # ronyal iskal')
                )

    def test_two(self):
        self.assertTrue(
                tasker.command_check_dictionary(
                    {'beginning': 'tasker', 
                     'command': 'add', 
                     'note': 'gogakal', 
                     'tags': ['ronyal', 'iskal', 'is kal']}
                    )
                ) 
    
    def test_three(self):
        self.assertFalse(
                tasker.command_check_dictionary(
                    {'beginning': 'add', 
                     'command': 'gogakal', 
                     'note': '', 
                     'tags': ['ronyal', 'iskal', 'is kal']}
                    )
                )

    def test_four(self):
        self.assertFalse(
                tasker.command_check_dictionary(
                    {'beginning': 'tasker', 
                     'command': 'add1', 
                     'note': 'gogakal', 
                     'tags': ['ronyal', 'iskal', 'is kal']}
                    )
                )


class Test_return_tags(unittest.TestCase):
    # tests for function return_tags() in tasker.py 
    
    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        self.assertEqual(
                tasker.return_tags('goga, mnogo ,,  , kal iskal, ne'), 
                ['goga', 'mnogo', 'kal iskal', 'ne']
                )

    def test_two(self):
        self.assertEqual(
                tasker.return_tags('goga, mnogo ,,  , kal iskal# ,# ne'), 
                ['goga', 'mnogo', 'kal iskal', 'ne']
                )

    def test_three(self):
        self.assertEqual(
                tasker.return_tags('ronyal, iskal, # is kal'), 
                ['ronyal', 'iskal', 'is kal']
                )


class Test_convert_input_to_dictionary(unittest.TestCase):
    # tests for function convert_input_to_dictionary() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        self.assertEqual(
                tasker.convert_input_to_dictionary(
                    'tasker add gogakal # ronyal, iskal , is kal'),
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal', 'is kal'],
                 'IDs': []
                 }
                )
    
    def test_two(self):
        self.assertEqual(
                tasker.convert_input_to_dictionary('tasker'),
                {'beginning': 'tasker', 
                 'command': '', 
                 'note': '', 
                 'tags': [],
                 'IDs': []
                 }
                )

    def test_three(self):
        self.assertEqual(
                tasker.convert_input_to_dictionary(
                    'tasker gogakal ronyal iskal'),
                {'beginning': 'tasker', 
                 'command': 'gogakal', 
                 'note': 'ronyal iskal', 
                 'tags': [],
                 'IDs': []
                 }
                )

    def test_four(self):
        self.assertEqual(
                tasker.convert_input_to_dictionary(
                    ' tasker add gogakal # ronyal, iskal , # is kal'),
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal', 'is kal'],
                 'IDs': []
                 }
                )


class Test_clear_all(unittest.TestCase):
    # tests for function clear_all() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal']
                 }
                )
        self.assertEqual(
                tasker.return_tag_dictionary(test_cursor, test_connection), 
                {'ronyal': 1}
                )
        tasker.clear_all(test_cursor, test_connection)
        self.assertEqual(
                tasker.return_tag_dictionary(test_cursor, test_connection), 
                {}
                )


class Test_return_notes(unittest.TestCase):
    # test for function return_notes() from tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal', 'is kal']}
                )
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['iskal', 'is kal']}
                )
        self.assertEqual(
                tasker.return_notes(
                    test_cursor, 
                    test_connection, 
                    'ronyal'
                    ), 
                [1])
        self.assertEqual(
                tasker.return_notes(
                    test_cursor, 
                    test_connection, 
                    'iskal'
                    ), 
                [1, 2])
        self.assertEqual(
                tasker.return_notes(
                    test_cursor, 
                    test_connection, 
                    'iskal1'
                    ), 
                [])

class Test_tasker_get(unittest.TestCase):
    # tests for function tasker_get() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal', 'is kal']}
                )
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'kak je tak', 
                 'tags': ['iskal', 'o kale']}
                )
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'vesma kal', 
                 'tags': ['ronyal', 'iskal', 'is kal', 'o kale']}
                )
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'pichal', 
                 'tags': ['ronyal']}
                )
        self.assertEqual(
                tasker.tasker_get(
                    test_cursor, 
                    test_connection, 
                    {'beginning': 'tasker', 
                     'command': 'get', 
                     'note': '', 
                     'tags': []}
                    ), 
                {1: 'gogakal', 2: 'kak je tak', 3: 'vesma kal', 4: 'pichal'}
                )
        self.assertEqual(
                tasker.tasker_get(
                    test_cursor, 
                    test_connection, 
                    {'beginning': 'tasker', 
                     'command': 'get', 
                     'note': '', 
                     'tags': ['ronyal', 'is kal']}
                    ), 
                {1: 'gogakal', 3: 'vesma kal'}
                )
        self.assertEqual(
                tasker.tasker_get(
                    test_cursor, 
                    test_connection, 
                    {'beginning': 'tasker', 
                     'command': 'get', 
                     'note': '', 
                     'tags': ['o kal']}
                    ), 
                {}
                )


class Test_tasker_tags(unittest.TestCase):
    # tests for function tasker_tags() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal', 'is kal']}
                )
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'kak je tak', 
                 'tags': ['iskal', 'o kale']}
                )
        self.assertEqual(
                tasker.tasker_tags(
                    test_cursor, 
                    test_connection,
                    {'beginning': 'tasker',
                     'command': 'get',
                     'note': '', 
                     'tags': []}, 
                    ),
                {'ronyal': 1, 'iskal': 2, 'is kal': 1, 'o kale': 1}
                )


class Test_tasker_rm(unittest.TestCase):
    # tests for function tasker_rm() in tasker.py
    # TODO write the tests after the function will be 
    # completed, see issue #45.
    
    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)
   
    def test_one(self):
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal', 'is kal'],
                 'IDs':[]}
                )
        tasker.tasker_add(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'kak je tak', 
                 'tags': ['iskal', 'o kale', 'is kal'],
                 'IDs':[]}
                )
        tasker.tasker_rm(
                test_cursor, 
                test_connection, 
                {'beginning': 'tasker', 
                 'command': 'tasker_rm', 
                 'note': '', 
                 'tags': [],
                 'IDs':[1]}
                )
        self.assertEqual(
                tasker.tasker_get(
                    test_cursor, 
                    test_connection, 
                    {'beginning': 'tasker', 
                     'command': 'get', 
                     'note': '', 
                     'tags': ['iskal']}
                    ), 
                {2: 'kak je tak'}
                )


class Test_return_IDs(unittest.TestCase):
    # tests for function return_IDs() in tasker.py
    
    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        self.assertEqual(
                tasker.return_IDs('1, 2 , ,,,  3   ,  ,,4'),
                [1, 2, 3, 4]
                )

    def test_two(self):
        self.assertEqual(
                tasker.return_IDs('1a, 2 , ,,,  3   ,  ,,4'),
                [2, 3, 4]
                )

    def test_three(self):
        self.assertEqual(
                tasker.return_IDs('1 1, 2 , ,,,  3   ,  ,,4'),
                [2, 3, 4]
                )

    def test_four(self):
        self.assertEqual(
                tasker.return_IDs(''),
                []
                )

    def test_five(self):
        self.assertEqual(
                tasker.return_IDs(' 1.1 , 2'),
                [2]
                )


class Test_check_if_note_contains_only_IDs(unittest.TestCase):
    # tests for function check_if_note_contains_only_IDs() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        self.assertEqual(
                tasker.check_if_note_contains_only_IDs('1'),
                True
                )

    def test_two(self):
        self.assertEqual(
                tasker.check_if_note_contains_only_IDs(''),
                False
                )

    def test_three(self):
        self.assertEqual(
                tasker.check_if_note_contains_only_IDs('1, 2 ,, 3'),
                True
                )

    def test_four(self):
        self.assertEqual(
                tasker.check_if_note_contains_only_IDs('1 December'),
                False
                )


class Test_return_tag_intersection(unittest.TestCase):
    # tests for function return_tags_intersection() in tasker.py

    def setUp(self):
        tasker.create_tables(test_cursor, test_connection)

    def tearDown(self):
        tasker.drop_tables(test_cursor, test_connection)

    def test_one(self):
        tasker.tasker_add(test_cursor, test_connection,
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal']}
                )
        tasker.tasker_add(test_cursor, test_connection,
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'vesma', 
                 'tags': ['ronyal', 'iskal', 'is kal']}
                )
        self.assertEqual(
                tasker.return_tags_intersection(
                    test_cursor,
                    test_connection,
                    ['ronyal']),
                [1, 2]
                )
        self.assertEqual(
                tasker.return_tags_intersection(
                    test_cursor,
                    test_connection,
                    ['is kal']),
                [2]
                )
        self.assertEqual(
                tasker.return_tags_intersection(
                    test_cursor,
                    test_connection,
                    []),
                []
                )
        self.assertEqual(
                tasker.return_tags_intersection(
                    test_cursor,
                    test_connection,
                    ['a vot i da']),
                []
                )
        self.assertEqual(
                tasker.return_tags_intersection(
                    test_cursor,
                    test_connection,
                    ['ronyal', 'iskal']),
                [1, 2]
                )
        self.assertEqual(
                tasker.return_tags_intersection(
                    test_cursor,
                    test_connection,
                    ['ronyal', 'iskal', 'vse ploha']),
                []
                )
     
        
# MAIN CYCLE
if __name__ == '__main__':
    unittest.main()