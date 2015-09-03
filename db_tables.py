__author__ = 'yupeng'

from objects import Table

_initial_overview_col_names = ('id', 'brand', 'officially_announced', 'official_release',
                      'device_colors', 'price', 'overall_rating')
_initial_overview_col_types = ('TEXT PRIMARY KEY', 'TEXT', 'TEXT','TEXT', 'TEXT','TEXT','TEXT')

def get_table_frame_info(db_cursor, table_name):
    '''
    :param db_cursor: cursor object for a database
    :param table_name: a name of table, string
    :return: Table object
    '''
    col_name_list = []
    col_type_list = []
    try:
        col_name_list = eval('_initial_%s_col_names' % table_name)
        col_type_list = eval('_initial_%s_col_types' % table_name)
    except NameError:
        print "Table %s is not in the default table set" % table_name

    db_cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % table_name)
    if db_cursor.fetchone():
        db_cursor.execute('PRAGMA table_info(%s)' % table_name)
        info = db_cursor.fetchall()

        col_name_list = [tuple[1] for tuple in info]
        col_type_list = [(tuple[2] + ' PRIMARY KEY' if tuple[-1] else tuple[2]) for tuple in info]

    return Table(table_name, col_name_list, col_type_list)
