from django.db import models


def get_column_attrs(width):
    """ Creates the specified number of fields and adds them to a dict,
        suitable to be used as a model's attrs
    """
    attrs = dict(
        ('col_{}'.format(i), models.IntegerField(default=1))
        for i in range(0, width)
    )
    attrs['__module__'] = 'wide_tables.models'  # Needed internally by Django
    attrs['width'] = width  # Stored for later reference
    return attrs

# Dynamically define models with 10, 100, and 1000 columns, resp.
Small = type("Small", (models.Model,), get_column_attrs(10))
Medium = type("Medium", (models.Model,), get_column_attrs(100))
Large = type("Large", (models.Model,), get_column_attrs(1000))
