## 使用简易elastic query查询数据
# TODO json field字段过滤
"""
    SQLAlchemy-ElasticQuery
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    This extension allow you use the ElasticSearch syntax for search in SQLAlchemy.
    Get a query string and return a SQLAlchemy query

    Example query string:

        {
            "filter" : {
                "or" : {
                    "firstname" : {
                        "equals" : "Jhon"
                    },
                    "lastname" : "Galt",
                    "uid" : {
                        "like" : "111111"
                    }
                },
                "and" : {
                    "status" : "active",
                    "age" : {
                        "gt" : 18
                    }
                }
            },
            "sort" : {
                "firstname" : "asc",
                "age" : "desc"
            },
            "limit": 5,
            "offset": 2
        }

"""
import json
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql.schema import Table

""" Valid operators """
OPERATORS = {
    "like": lambda f, a: f.like(a),
    "equals": lambda f, a: f == a,
    "null": lambda f, a: f.is_(None) if a else f.isnot(None),
    "gt": lambda f, a: f > a,
    "gte": lambda f, a: f >= a,
    "lt": lambda f, a: f < a,
    "lte": lambda f, a: f <= a,
    "in": lambda f, a: f.in_(a),
    "not_in": lambda f, a: ~f.in_(a),
    "not_equal_to": lambda f, a: f != a,
}


class OperatorNotFound(Exception):
    pass


class ElasticQuery(object):
    """Magic method"""

    def __init__(self, db, model, query, enabled_fields=None):
        """Initializator of the class 'ElasticQuery'"""
        self.model = model
        self.query = json.loads(query)
        self.model_query = db.query(model)
        self.enabled_fields = enabled_fields

    def search(self):
        filters = self.query
        result = self.model_query
        keys = filters.keys()
        count = 0
        if "filter" in keys:
            result = self.parse_filter(filters["filter"])
        if "sort" in keys:
            result = result.order_by(*self.sort(filters["sort"]))
        # count = result.count()
        # page = self.page(
        #     result, filters.get("offset", None), filters.get("limit", None)
        # )

        # return result, count, page
        return result

    def page(self, query, offset, limit):
        def apply_page(query=query):
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query

        return apply_page

    def parse_filter(self, filters):
        """This method process the filters"""
        try:
            for filter_type, filter_value in filters.items():
                if filter_type == "or" or filter_type == "and":
                    conditions = []
                    for field in filters[filter_type]:
                        if self.is_field_allowed(field):
                            conditions.append(
                                self.create_query(
                                    self.parse_field(field, filter_value[field])
                                )
                            )
                    if filter_type == "or":
                        self.model_query = self.model_query.filter(or_(*conditions))
                    elif filter_type == "and":
                        self.model_query = self.model_query.filter(and_(*conditions))
                else:
                    if self.is_field_allowed(filter_type):
                        conditions = self.create_query(
                            self.parse_field(filter_type, filter_value)
                        )
                        self.model_query = self.model_query.filter(conditions)
        except OperatorNotFound:
            return self.model_query
        return self.model_query

    def parse_field(self, field, field_value):
        """Parse the operators and traduce: ES to SQLAlchemy operators"""
        if type(field_value) is dict:
            operator = list(field_value)[0]
            if self.verify_operator(operator) is False:
                raise OperatorNotFound()
            value = field_value[operator]
        elif type(field_value) is str:
            operator = u"equals"
            value = field_value
        else:
            raise OperatorNotFound()
        return field, operator, value

    @staticmethod
    def verify_operator(operator):
        """Verify if the operator is valid"""
        try:
            if hasattr(OPERATORS[operator], "__call__"):
                return True
            else:
                return False
        except ValueError:
            return False
        except KeyError:
            return False

    def is_field_allowed(self, field):
        if self.enabled_fields:
            return field in self.enabled_fields
        else:
            return True

    def create_query(self, attr):
        """Mix all values and make the query"""
        field = attr[0]
        operator = attr[1]
        value = attr[2]
        model = self.model

        if "." in field:
            field_items = field.split(".")

            attr = None
            for field_item in field_items:
                attr = getattr(model, field_item, None)
                if isinstance(attr.property, RelationshipProperty):
                    model = attr.property.mapper.class_
                    secondary = attr.property.secondary
                    if isinstance(secondary, Table):
                        self.model_query = self.model_query.join(secondary)
                    self.model_query = self.model_query.join(model)
                else:
                    break

            return OPERATORS[operator](attr, value)

        return OPERATORS[operator](getattr(model, field, None), value)

    def sort(self, sort):
        """Sort"""
        order = []
        for field, direction in sort.items():
            if direction == "asc":
                order.append(asc(getattr(self.model, field, None)))
            elif direction == "desc":
                order.append(desc(getattr(self.model, field, None)))
        return order
