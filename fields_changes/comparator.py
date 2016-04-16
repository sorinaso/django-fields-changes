import inspect
import django

class ComparatorError(Exception):
    pass

def normal_comparison(original_value, new_value):
    if original_value != new_value:
        return { 'old_value': original_value, 'new_value': new_value }

def no_comparison(original_value, new_value):
        pass

field_comparison = { }

# Hago instropeccion en los campos de django asumiendo por practica que un ==
# funciona en estos como comparacion varida de contenido en lso atirbutos.
for symbol in django.db.models.fields.__dict__.values():
    if inspect.isclass(symbol) and \
       issubclass(symbol, django.db.models.fields.Field):
        field_comparison[symbol] = normal_comparison

def add_rule(field_type, func):
    """
    Agrega una regla de comparacion
    `field_type`: Tipo campo a comparar
    `func`: Funcion de comparacion.
    """
    field_comparison[field_type] = func

def compare(instance, field_name, old_value, new_value):
    """
    Compara un valor viejo con un valor nuevo teniendo en cuenta el tipo
    de campo.
    `instance`: Instancia del campo.
    `field_name`: Nombre del campo
    `old_value`: Valor viejo.
    `new_value`: Valor nuevo.
    """
    f_class = instance.__class__._meta.get_field_by_name(field_name)[0].__class__

    if field_comparison.has_key(f_class):
        return field_comparison[f_class](old_value, new_value)
    else:
        raise ComparatorError("Tipo de campo %s no soportado en el "
                              "modelo %s atributo %s" %
                              (f_class, instance.__class__, field_name))


