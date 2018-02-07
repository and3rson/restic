"""
Viewsets logic.
"""
# pylint: disable=invalid-name
# pylint: disable=abstract-method
from json import loads

from sanic.response import json
from sanic.blueprints import Blueprint

from restic import exceptions


class GenericViewSet(object):
    """
    Generic viewset.

    This class allows you to perform operations on lists and their
    individual items.

    HTTP methods are mapped to class method names as follows:

    * ``GET /.../`` - list
    * ``POST /.../`` - create
    * ``GET /.../<pk>`` - retrieve
    * ``PUT /.../<pk>`` - update
    * ``PATCH /.../<pk>`` - update_partial
    * ``DELETE /.../<pk>`` - destroy

    These class method names are also called "handler functions".

    A "handler function" is a method that handles specific method for
    specific path.

    `<pk>` equals to `'<PK:int>'` by default. You can change it by overriding
    the :py:attr:`~.GenericViewSet.PK_PATTERN` class attribute for your
    viewset. For possible values see Sanic routing documentation.

    If a view that inherits this class does not define some methods, they will
    be disallowed. If someone will attempt to call them, a
    ``405 Method Not Allowed`` response will be returned.

    If you need to define CRUD for your models, see :class:`.ModelViewSet` and
    :class:`.ReadOnlyModelViewSet` classes.
    """
    LIST_ACTIONS = dict(
        GET='list',
        POST='create'
    )
    ITEM_ACTIONS = dict(
        GET='retrieve',
        PUT='update',
        PATCH='update_partial',
        DELETE='destroy'
    )
    PK_PATTERN = '<pk:int>'

    def __init__(self, request):
        self.request = request

    def get_data(self):
        """
        Parse request JSON data.
        """
        # TODO: Handle parse errors.
        return loads(self.request.body)

    @classmethod
    def create_blueprint(cls, name):
        """
        Assemble & return a blueprint that represents this viewset.

        This blueprint can then be used in your app like this:

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
        """
        blueprint = Blueprint(name)
        for list_method, list_action in cls.LIST_ACTIONS.items():
            blueprint.add_route(
                cls._create_dispatcher(list_action),
                '/',
                methods=[list_method]
            )
        for item_method, item_action in cls.ITEM_ACTIONS.items():
            blueprint.add_route(
                cls._create_dispatcher(item_action),
                '/' + cls.PK_PATTERN,
                methods=[item_method]
            )
        return blueprint

    def get_handler(self, action):
        """
        Return a handler function for this action or ``None`` if no handler
        is defined.
        """
        return getattr(self, action, None)

    @classmethod
    def _create_dispatcher(cls, action):
        """
        Create and return request dispatcher.
        """
        def dispatcher(request, *args, **kwargs):
            """
            Handle request into proper handler functions.
            """
            try:
                viewset = cls(request)
                handler = viewset.get_handler(action)
                if handler is not None:
                    handler = getattr(viewset, action)
                    return handler(*args, **kwargs)
                raise exceptions.MethodNotAllowed()
            except exceptions.APIException as error:
                return json(dict(
                    message=error.message,
                    details=error.details
                ), status=error.status)
        return dispatcher


class GenericModelViewSet(GenericViewSet):
    """
    Generic class for implementing model-based viewsets.
    """
    def get_serializer_class(self):  # pragma: no cover
        """
        Return :class:`~restic.serializers.Serializer` class for this viewset.
        """
        raise NotImplementedError()

    def get_models(self):  # pragma: no cover
        """
        Return a list of models.
        """
        raise NotImplementedError()

    def get_model(self, pk):  # pragma: no cover
        """
        Return a single model matched by ID.
        Return ``None`` if model is not found.
        """
        raise NotImplementedError()

    def get_model_or_404(self, pk):
        """
        Return a single model matched by ID.
        Raise :py:class:`~exceptions.NotFound` exception if model is not found.
        """
        model = self.get_model(pk)
        if model is None:
            raise exceptions.NotFound(
                'Model with such primary key was not found.'
            )
        return model


class ListModelMixin(object):
    """
    A mixin that allows ModelViewSet to list models.

    An example of ``list`` is: ``GET /items/``
    """
    def list(self):
        """
        Get a list of models and return their representation in a
        json response.
        """
        models = self.get_models()
        serializer = self.get_serializer_class()(models, many=True)
        return json(serializer.serialize())


class CreateModelMixin(object):
    """
    A mixin that allows ModelViewSet to create models.

    An example of ``create`` is: ``POST /items/``
    """
    def create(self):
        """
        Create a new model and return its representation in a json response.
        """
        serializer = self.get_serializer_class()()
        serializer.do_create(self.get_data())
        return json(serializer.serialize(), status=201)


class RetrieveModelMixin(object):
    """
    A mixin that allows ModelViewSet to retrieve models.

    An example of ``retrieve`` is: ``GET /items/5``
    """
    def retrieve(self, pk):
        """
        Get an existing model and return its representation in a
        json response.
        """
        model = self.get_model_or_404(pk)
        serializer = self.get_serializer_class()(model, many=False)
        return json(serializer.serialize())


class UpdateModelMixin(object):
    """
    A mixin that allows ModelViewSet to update models.

    An example of ``update`` is: ``PUT /items/5`` or ``PATCH /items/5``
    """
    def update(self, pk):
        """
        Update an existing model and return its modified representation in a
        json response.
        """
        model = self.get_model_or_404(pk)
        serializer = self.get_serializer_class()(model)
        serializer.do_update(self.get_data())
        return json(serializer.serialize())

    def update_partial(self, pk):
        """
        Alias for :py:meth:`~.UpdateModelMixin.update`
        """
        return self.update(pk)


class DestroyModelMixin(object):
    """
    A mixin that allows ModelViewSet to retrieve models.

    An example of ``retrieve`` is: ``DELETE /items/5``
    """
    def destroy(self, pk):
        """
        Delete an existing model and return an empty json response.
        """
        model = self.get_model_or_404(pk)
        serializer = self.get_serializer_class()(model)
        serializer.do_destroy()
        return json(None, status=204)


class ReadOnlyModelViewSet(
        GenericModelViewSet,
        ListModelMixin,
        RetrieveModelMixin
):
    """
    Viewset for models that cannot be modified.
    """
    pass


class ModelViewSet(
        GenericModelViewSet,
        ListModelMixin,
        CreateModelMixin,
        RetrieveModelMixin,
        UpdateModelMixin,
        DestroyModelMixin
):
    """
    Fully featured CRUD viewset for models with.
    """
    pass
