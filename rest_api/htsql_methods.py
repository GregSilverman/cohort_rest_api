# load extensions

from htsql.core.fmt.emit import emit

from app import connection


def get_data_json(arg):

    rows = connection.produce(arg)

    with connection:
        return ''.join(emit('x-htsql/json', rows))


def get_data(arg):

    rows =  connection.produce(arg)

    for row in rows:
        return "%s" % row.name


