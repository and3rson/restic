Restic
======

A loose & flexible REST framework for Sanic. Inspired by Django REST Framework.

In a nutshell
=============

Simple example
--------------

.. code-block:: python

    from sanic import Sanic
    from sanic.response import json

    from restic import exceptions
    from restic.viewsets import GenericViewSet

    CATS = [
        {'id': 1, 'name': 'Kitty One'},
        {'id': 2, 'name': 'Kitty Two'}
    ]

    class ItemsViewSet(GenericViewSet):
        def list(self):
            return json(CATS)

        def retrieve(self, pk):
            cats = [cat for cat in CATS if cat['id'] == pk]
            if not cats:
                raise exceptions.NotFound('Cat not found :V')
            return json(cats[0])


    app = Sanic('my_app')
    app.blueprint(
        ItemsViewSet.create_blueprint('cats'),
        url_prefix='/cats'
    )
    app.run(host='0.0.0.0', port=8000, debug=True)

Using Serializer and ModelViewSet
---------------------------------

.. code-block:: python

    from sanic import Sanic
    from sanic.response import json

    from restic import exceptions
    from restic.viewsets import ModelViewSet
    from restic.serializers import Serializer

    MODELS = [{'id': 1, 'name': 'Foo'}, {'id': 2, 'name': 'Foo'}]


    class ItemSerializer(Serializer):
        def create(self, data):
            model = dict(data)
            try:
                model['id'] = max([model['id'] for model in MODELS]) + 1
            except ValueError:
                model['id'] = 1
            MODELS.append(model)
            return model

        def update(self, data):
            self.instance['name'] = data['name']

        def destroy(self):
            MODELS.remove(self.instance)

        def serialize(self):
            return self.instance


    class ItemsViewSet(ModelViewSet):
        def get_serializer_class(self):
            return ItemSerializer

        def get_models(self):
            return MODELS

        def get_model(self, pk):
            matches = [model for model in self.get_models() if model['id'] == pk]
            if matches:
                return matches[0]


    app = Sanic('my_app')
    app.blueprint(ItemsViewSet.create_blueprint('items'), url_prefix='/items')
    for route in app.router.routes_all:
        print(route)  # Display all routes
    app.run(host='0.0.0.0', port=8000, debug=True)


Documentation
=============

Coming soon.
