"""
Mixin defining common Studio functionality
"""

import datetime
import dateutil.parser

from xblock.fields import Scope, Field, Integer, XBlockMixin


class DateTuple(Field):
    """
    Field that stores datetime objects as time tuples
    """
    def from_json(self, value):
        return datetime.datetime(*value[0:6])

    def to_json(self, value):
        if value in [None, ""]:
            return None

        if isinstance(value, str): 
            value = dateutil.parser.parse(value)

        return list(value.timetuple())


class CmsBlockMixin(XBlockMixin):
    """
    Mixin with fields common to all blocks in Studio
    """
    published_date = DateTuple(help="Date when the module was published", scope=Scope.settings)
    published_by = Integer(help="Id of the user who published this module", scope=Scope.settings)
