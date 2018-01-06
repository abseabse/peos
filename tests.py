# Version: 1*
# Date: 6.1.18
# Time: 15:52 GMT+5


# IMPORTS
import unittest
import tasker
import sqlite3


# CREATING MOCK DATABASE, CONNECTION AND CURSOR FOR TESTING PURPOSES
conn = sqlite3.connect(":memory:")
c = conn.cursor()
c.execute('''pragma foreign_keys = on''')


# TEST BLOCK
class TestTables(unittest.TestCase):
# tests for create_tables() in tasker.py
    
    def setUp(self):
        tasker.create_tables(c, conn)

    def tearDown(self):
        tasker.drop_tables(c, conn)

    def test_table_notes(self):
    # test if table notes is functioning
        c.execute("insert into notes VALUES (1, 'gogakal')")
        conn.commit()

    def test_table_notes_ID_note_is_a_primary_key(self):
    # test if in table notes ID_note is a primary key
        c.execute("insert into notes VALUES(1, 'gogakal')")
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute("insert into notes VALUES(1, 'gogakal2')")
        conn.commit()

    def test_table_tags(self):
    # test if table tags is functioning
        c.execute("insert into tags VALUES (1, 'o kale')")
        conn.commit()

    def test_table_tags_ID_tag_is_a_primary_key(self):
    # test if in table tags ID_tag is a primary key
        c.execute("insert into tags VALUES (1, 'o kale')")
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute("insert into tags VALUES (1, 'o fekale')")
        conn.commit()

    def test_table_notes_tags_is_functioning(self):
    # tests if the table notes_tags is functioning
        c.execute("""insert into notes VALUES (1, 'goga')""")
        c.execute("""insert into tags VALUES (2, 'kal')""")
        c.execute("""insert into notes_tags VALUES (1, 2)""")
        conn.commit()

    def test_table_notes_tags_not_null_constraint(self):
    # tests if in table notes_tags both attributes goes with
    # not null constraint
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute("""insert into notes_tags VALUES (null, null)""")
        conn.commit()

    def test_table_notes_tags_foreign_keys(self):
    # tests if both attributes in the table notes_tags are foreign keys
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute("""insert into notes_tags VALUES (1, 2)""")
        conn.commit()

    def test_table_notes_tags_complex_primary_key(self):
        with self.assertRaises(sqlite3.IntegrityError):
            c.execute("""insert into notes VALUES (1, 'goga')""")
            c.execute("""insert into tags VALUES (2, 'kal')""")
            c.execute("""insert into notes_tags VALUES (1, 2)""")
            c.execute("""insert into notes_tags VALUES (1, 2)""")
        conn.commit()

class Test_initial_input_check(unittest.TestCase):
# tests for initial_input_check in tasker.py

    def setUp(self):
        tasker.create_tables(c, conn)

    def tearDown(self):
        tasker.drop_tables(c, conn)

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
        tasker.create_tables(c, conn)

    def tearDown(self):
        tasker.drop_tables(c, conn)

    def test_one(self):
        tasker.tasker_add(
                {'beginning': 'tasker', 
                 'command': 'add', 
                 'note': 'gogakal', 
                 'tags': ['ronyal', 'iskal', 'is kal']}
                )
        self.assertEqual(
                tasker.tasker_tags(), {'ronyal': 1, 'iskal': 1, 'is kal': 1}
                )

    def test_two(self):
        with self.assertRaises(Warning): 
            tasker.tasker_add(
                    {'beginning': 'tasker', 
                     'command': 'add', 
                     'note': 'gogakal', 
                     'tags': []}
                    )

    def test_three(self):
        with self.assertRaises(Warning): 
            tasker.tasker_add(
                    {'beginning': 'tasker', 
                     'command': 'add', 
                     'note': '', 
                     'tags': ['ronyal', 'iskal', 'is kal']}
                    )

class Test_tasker_add_check(unittest.TestCase):
    # tests for tasker_add_check() in tasker.py
    
    def setUp(self):
        tasker.create_tables(c, conn)

    def tearDown(self):
        tasker.drop_tables(c, conn)

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

class Test_tasker_tags(unittest.TestCase):

    def setUp(self):
        tasker.create_tables(c, conn)

    def tearDown(self):
        tasker.drop_tables(c, conn)

    def test_one(self):
        # FIXME there is a problem, somehow there is some information in 
        # temporary database for testing, that is not good at all.
        # The possible reason - each function adresses not the temporary
        # database but normal database instead. Need to check it.
        # See issue #34 
        self.assertEqual(tasker.tasker_tags(), {})

# MAIN CYCLE
if __name__ == '__main__':
    unittest.main()
