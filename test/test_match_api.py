from neomodel import (StructuredNode, StringProperty, IntegerProperty, RelationshipFrom,
        RelationshipTo, StructuredRel, DateTimeProperty)
from neomodel.match import NodeSet, QueryBuilder, Traversal
from datetime import datetime


class SupplierRel(StructuredRel):
    since = DateTimeProperty(default=datetime.now)


class Supplier(StructuredNode):
    name = StringProperty()
    delivery_cost = IntegerProperty()
    coffees = RelationshipTo('Coffee', 'SUPPLIES')


class Coffee(StructuredNode):
    name = StringProperty()
    price = IntegerProperty()
    suppliers = RelationshipFrom(Supplier, 'SUPPLIES', model=SupplierRel)


def test_filter_exclude_via_labels():
    Coffee(name='Java', price=99).save()

    node_set = NodeSet(Coffee)
    qb = QueryBuilder(node_set)

    results = qb.execute()

    assert '(coffee:Coffee)' in qb._ast['match']
    assert 'result_class' in qb._ast
    assert len(results) == 1
    assert isinstance(results[0], Coffee)
    assert results[0].name == 'Java'

    # with filter and exclude
    node_set = node_set.filter(price__gt=2).exclude(price__gt=6, name='Java')
    qb = QueryBuilder(node_set)
    qb.execute()
    assert '(coffee:Coffee)' in qb._ast['match']
    assert 'NOT' in qb._ast['where'][0]


def test_simple_has_via_label():
    ns = NodeSet(Coffee).has(suppliers=True)
    qb = QueryBuilder(ns)
    qb.execute()
    assert 'SUPPLIES' in qb._ast['where'][0]

    ns = NodeSet(Coffee).has(suppliers=False)
    qb = QueryBuilder(ns)
    qb.execute()
    assert 'NOT' in qb._ast['where'][0]


def test_simple_traverse():
    latte = Coffee(name="Latte").save()
    traversal = Traversal(source=latte,
        key='suppliers',
        definition=Coffee.suppliers.definition).match(since__lt=datetime.now())

    qb = QueryBuilder(NodeSet(source=traversal))
    qb.execute()