from datetime import datetime

from sanic import Sanic
from sanic.response import json

from restic import exceptions
from restic.viewsets import ModelViewSet
from restic.serializers import (
    Serializer,
    Field,
    SerializerMethodField,
    NaiveDateTimeField
)

MODELS = []

def reset():
    MODELS[:] = [
        {'id': 1, 'name': 'Foo', 'date_created': datetime.now()},
        {'id': 2, 'name': 'Foo', 'date_created': datetime.now()}
    ]

reset()


class ItemSerializer(Serializer):
    id = Field(read_only=True)
    name = Field(required=True)
    title = SerializerMethodField()
    date_created = NaiveDateTimeField()

    def get_title(self, model):
        return 'Item {}: {}'.format(
            model['id'],
            model['name']
        )

    def create(self, validated_data):
        model = dict(validated_data)
        try:
            model['id'] = max([model['id'] for model in MODELS]) + 1
        except ValueError:
            model['id'] = 1
        model['date_created'] = datetime.now()
        MODELS.append(model)
        return model

    def update(self, validated_data):
        self.instance['name'] = validated_data.get('name', self.instance['name'])
        self.instance['date_created'] = validated_data.get('date_created', self.instance['date_created'])

    def destroy(self):
        MODELS.remove(self.instance)


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11000, debug=True)
