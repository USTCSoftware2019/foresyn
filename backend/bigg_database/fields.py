from django.db import models
from django.core.exceptions import ValidationError

import json


class JSONField(models.TextField):

    description = "JSON"

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return json.loads(value)

    def to_python(self, value):
        if value is None or not isinstance(value, str):
            return value
        else:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError

    def get_prep_value(self, value):
        return json.dumps(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)
