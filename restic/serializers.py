"""
Serializers logic.
"""
class Serializer(object):
    """
    Generic serializer.

    A serializer is an interface between Restic and your data (models).

    Serializer defines how the read, create, update and delete processes are
    handled for this model.

    Serializers are very important to Restic: he is going to use them
    as data sources.

    Serializer knows nothing about your data structures and/or your database,
    so to fully implement a CRUD logic for your model, you'll need to override
    the following four methods:

    * ``serialize()`` - should return a JSON-serializable
      representation of data in ``self.instance`` attribute.
    * ``create(data)`` - should create new model from ``data`` argument and
      store it in your database, file, global variable or whatever.
    * ``update(data)`` - should change existing model located
      in ``self.instance`` atribute by read new values
      from ``data`` argument.
    * ``destroy()`` - should delete the model that is located
      in ``self.instance`` from your database, file etc.
    """
    # TODO: Implement model serializers
    # TODO: Implement serializer fields & validation
    def __init__(self, instance=None, many=False):
        self.instance = instance
        self.many = many

    def serialize(self):
        """
        Return a representation for this model.

        If ``many`` was set to True, return ``list``.
        Otherwise return ``dict``.
        """
        raise NotImplementedError()

    def create(self, data):
        """
        Perform create logic for attached model.
        """
        raise NotImplementedError()

    def update(self, data):
        """
        Perform update logic for attached model.
        """
        raise NotImplementedError()

    def destroy(self):
        """
        Perform destroy logic for attached model.
        """
        raise NotImplementedError()

    def do_create(self, data):
        """
        Create a model and update instance value.
        """
        self.instance = self.create(data)

    def do_update(self, data):
        """
        Update a model.
        """
        self.update(data)

    def do_destroy(self):
        """
        Destroy a model and set instance value to ``None``.
        """
        self.destroy()
        self.instance = None
