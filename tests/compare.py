import re


def compare_postgresql_dumps(dump1, dump2):
    """
    Compare two postgresql dumps.

    :param dump1: path to postgresql dump to compare.
    :param dump2: path to postgresql dump to compare.
    """
    # read the expected non-empty non-comment lines
    expected_lines = []
    with open(dump1, 'r') as expected:
        for line in expected.readlines():
            if not line.startswith('--') and not re.match(r'^\s*$', line):
                expected_lines.append(line)

    # compare the dump with the expected result
    with open(dump2, 'r') as test:
        c = 0
        for i, line in enumerate(test.readlines()):
            if not line.startswith('--') and not re.match(r'^\s*$', line):
                assert line == expected_lines[c]
                c += 1


def compare_databases(expected_cur, test_cur):
    """
    Compare all tables of expected database with the expected database.

    :param expected_cur: cursor for the database with the expected data
    :param test_cur: cursor for the database to be tested
    """
    expected_cur.execute(
        "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
    tables = expected_cur.fetchall()

    if len(tables) == 0:
        test_cur.execute(
            "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
        test_tables = test_cur.fetchall()
        assert len(test_tables) == 0

    for table in tables:
        table = table[0]
        expected_cur.execute("SELECT * FROM {};".format(table))
        expected_result = expected_cur.fetchall()

        test_cur.execute("SELECT * FROM {};".format(table))
        result = test_cur.fetchall()

        assert expected_result == result
