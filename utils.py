__author__ = 'yupeng'

from objects import Table
import re

_default_tables = ['overview', 'ratings', 'network_n_platforms', 'memory', 'body_n_design',
                   'screen_n_display', 'call_management', 'camera_n_features', 'multimedia',
                   'data_connectivity_n_internet', 'application_support', 'communication_n_tracking',
                   'battery_n_power_usage']

_initial_col_names = ['id', 'brand']
_initial_col_types = ['TEXT PRIMARY KEY', 'TEXT']


def get_table_frame_info(db_cursor, table_name):
    '''
    :param db_cursor: cursor object for a database
    :param table_name: a name of table, string
    :return: Table object
    '''
    col_name_list = _initial_col_names
    col_type_list = _initial_col_types

    db_cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="%s"' % table_name)
    if db_cursor.fetchone():
        db_cursor.execute('PRAGMA table_info(%s)' % table_name)
        info = db_cursor.fetchall()

        col_name_list = [tuple[1] for tuple in info]
        col_type_list = [(tuple[2] + ' PRIMARY KEY' if tuple[-1] else tuple[2]) for tuple in info]

    return Table(table_name, col_name_list, col_type_list)

def get_table_name_list(db_cursor):
    '''
    :param db_cursor:
    :return:
    '''
    db_cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    name_list = [name[0] for name in db_cursor.fetchall()]
    if not name_list:
        name_list = _default_tables

    return _default_tables

def valid_col_name(name):
    name = re.sub('"', '', re.sub('\\s+', '_', name.strip().lower()))
    if len(name) == 0:
        return ''
    if (not name[0].isalpha()) and name[0] != '_':
        name = '_'+name
    return name

def valid_table_name(name):
    name = re.sub('\(.*?\)', '', name).strip().lower().replace(' ', '_').replace('&', 'n')
    if len(name) == 0:
        return ''
    if (not name[0].isalpha and name[0] != '_'):
        name = '_'+name
    return name