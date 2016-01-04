from __future__ import absolute_import

import json

from ...sql import elements
from ... import types as sqltypes
from ... import util


class JSON(sqltypes.JSON):
    """MySQL JSON type.

    MySQL supports JSON as of version 5.7.  Note that MariaDB does **not**
    support JSON at the time of this writing.

    The :class:`.mysql.JSON` type supports persistence of JSON values
    as well as the core index operations provided by :class:`.types.JSON`
    datatype, by adapting the operations to render the ``JSON_EXTRACT``
    function at the database level.

    .. versionadded:: 1.1

    """
    def bind_processor(self, dialect):
        json_serializer = dialect._json_serializer or json.dumps
        if util.py2k:
            encoding = dialect.encoding
        else:
            encoding = None

        def process(value):
            if value is self.NULL:
                value = None
            elif isinstance(value, elements.Null) or (
                value is None and self.none_as_null
            ):
                return None
            if encoding:
                return json_serializer(value).encode(encoding)
            else:
                return json_serializer(value)

        return process

    def result_processor(self, dialect, coltype):
        json_deserializer = dialect._json_deserializer or json.loads
        if util.py2k:
            encoding = dialect.encoding
        else:
            encoding = None

        def process(value):
            if value is None:
                return None
            if encoding:
                value = value.decode(encoding)
            return json_deserializer(value)
        return process


class JSONIndexType(sqltypes.JSON.JSONIndexType):
    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, int):
                return "$.[%s]" % value
            else:
                return "$.%s" % value

        return process


class JSONPathType(sqltypes.JSON.JSONPathType):
    def bind_processor(self, dialect):
        def process(value):
            return "$.%s" % (
                ".".join([
                    "[%s]" % elem if isinstance(elem, int)
                    else "%s" % elem for elem in value
                ])
            )

        return process
