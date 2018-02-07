"""
Serializers logic.
"""
from collections import Mapping

from restic.exceptions import BadRequest


class Field(object):
    """
    Generic serializer field.

    Represents a top-level field in serializer.

    Two methods can be overrided: :py:meth:`.Field.to_representation`
    and :py:meth:`.Field.to_internal_value`.

    Example usage:

    .. code-block:: python

        class CatSerializer(Serializer):
            name = Field()
            breed = Field()
    """
    def __init__(self, required=True, read_only=False):
        self.required = required
        self.read_only = read_only

    def get_model_value(self, model, name):
        """
        Return model field by name.

        Because model can be either dict-like object or an object,
        we check if we should use ``getattr`` or ``getitem`` to retrieve it.
        """
        if isinstance(model, Mapping):
            return model[name]
        return getattr(model, name)

    def set_model_value(self, model, name, value):
        """
        Set model field by name.

        Because model can be either dict-like object or an object,
        we check if we should use ``setattr`` or ``setitem`` to retrieve it.
        """
        if isinstance(model, Mapping):
            model[name] = value
        return setattr(model, name, value)

    def to_representation(self, serializer, model, name):
        """
        Return a representation of data in this field.

        Result should be a JSON-serializable data.

        For example: format ``datetime`` object in ``value``
        and return it as ``str``.
        """
        return self.get_model_value(model, name)

    def to_internal_value(self, serializer, model, name, data):
        """
        Parse user data and convert it into internal model value.

        Result will be set into model as an attribute or key.

        For example: parse ``data`` as timestamp and return it
        as ``datetime`` object.
        """
        if not self.read_only:
            self.set_model_value(model, name, data)


class SerializerMethodField(Field):
    """
    Method field.

    This field allows you to specify custom serialization function for
    related model. Value represented by this field is read-only.

    Function should be a member of a serializer where this field is defined.

    Default method name is ``'get_' + field_name``.

    Example usage:

    .. code-block:: python

        class ColorSerializer(Serializer):
            first_name = Field()
            last_name = Field()
            full_name = SerializerMethodField()

            def get_full_name(self, instance):
                return instance.first_name + instance.last_name
    """
    def __init__(self, method_name=None, required=False):
        self.method_name = method_name
        super(SerializerMethodField, self).__init__(
            required=required,
            read_only=True
        )

    def to_representation(self, serializer, model, name):
        """
        Return a result of calling ``method`` for attached instance.
        """
        method_name = self.method_name
        if method_name is None:
            method_name = 'get_' + name
        return getattr(serializer, method_name)(model)


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

    * ``create(data)`` - should create new model from ``data`` argument and
      store it in your database, file, global variable or whatever.
    * ``update(data)`` - should change existing model located
      in ``self.instance`` atribute by read new values
      from ``data`` argument.
    * ``destroy()`` - should delete the model that is located
      in ``self.instance`` from your database, file etc.

    You can also override ``serialize`` method to perform custom serialization
    logic on the entire instance.
    """
    # TODO: Implement model serializers
    # TODO: Implement serializer fields & validation
    def __init__(self, instance=None, many=False):
        self.instance = instance
        self.many = many

        self.fields = {}
        for name in dir(self):
            field = getattr(self, name)
            if isinstance(field, Field):
                self.fields[name] = field
        print(self.fields)

    def serialize(self):
        """
        Return JSON-serializable representation of the attached model
        or model list.
        """
        if self.many:
            return [
                self._serialize(model)
                for model
                in self.instance
            ]
        return self._serialize(self.instance)

    def _validate(self, data, allow_partial=False):
        """
        Process data through all the fields and return validated data.
        """
        validated_data = {}
        errors = {}
        for name, field in self.fields.items():
            if field.read_only:
                continue

            if not allow_partial:
                if field.required and name not in data:
                    errors[name] = 'This field is required.'

            if name not in data:
                continue

            validated_data[name] = data[name]

        if errors:
            raise BadRequest(message='Model validation failed', details=errors)

        return validated_data

    def _serialize(self, instance):
        """
        Serialize a single model.
        """
        return {
            name: field.to_representation(self, instance, name)
            for name, field
            in self.fields.items()
        }

    def create(self, validated_data):
        """
        Perform create logic for attached model.
        """
        raise NotImplementedError()

    def update(self, validated_data):
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
        validated_data = self._validate(data)
        self.instance = self.create(validated_data)

    def do_update(self, data):
        """
        Update a model.
        """
        validated_data = self._validate(data, allow_partial=True)
        self.update(validated_data)

    def do_destroy(self):
        """
        Destroy a model and set instance value to ``None``.
        """
        self.destroy()
        self.instance = None
