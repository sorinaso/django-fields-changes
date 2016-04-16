from fields_changes import comparator

class DirtyFieldError(Exception):
    """Excepcion para campos sucios."""
    pass

class ChangedFields(dict):
    def new_value_or_default(self, field, default=None):
        """Devuelve el nuevo valor o un default(conveniencia)."""
        return (self.has_key(field) or default) and self[field]['new_value']

    def has_old_value(self, field):
        """Tiene el campo un valor antiguo?."""
        return self.has_key(field) and self[field].has_key('old_value')

    def has_new_value(self, field):
        """Tiene el campo un valor nuevo?."""
        return self.has_key(field) and self[field].has_key('new_value')

    def has_changed(self, field, old_value=None, new_value=None):
        """Cambio el campo?."""
        has_changed = self.has_old_value(field) and self.has_new_value(field) and \
            (self.new_value(field) != self.old_value(field))

        if not has_changed: return False

        if old_value:
            has_changed = has_changed and self.value_was(field, old_value)

        if new_value:
            has_changed = has_changed and self.value_is(field, new_value)

        return has_changed

    def field_names(self):
        """Devuelve una lista con los nombres campos cambiados."""
        return self.keys()

    def only_has_changed(self, field, old_value=None, new_value=None):
        """Solo ha cambiado tal campo."""
        return self.field_names() == [field] and \
               self.has_changed(field, old_value, new_value)

    def diff(self, fields, left=True):
        """
        Devuelve la diferencia entre los nombres de los campos cambiados y
        los nombres de los campos dados.
        `fields`: Campos  comparar
        `left`: Si la diferencia es "left" entocnes devuelve los que fueron
                cambiados y no fueron dados sino al reves.
        """
        if left:
            return list(set(self.field_names()) - set(fields))
        else:
            return list(set(fields) - set(self.field_names()))

    def new_value(self, field):
        """Valor nuevo."""
        if not self.has_new_value(field):
            raise DirtyFieldError('El campo %s no tiene valor nuevo' % field)

        return self[field]['new_value']

    def old_value(self, field):
        """Valor antiguo."""
        if not self.has_old_value(field):
            raise DirtyFieldError('El campo %s no tiene valor antiguo' % field)

        return self[field]['old_value']

    def value_was(self, field, value):
        """El valor del campo antiguo era `value`?."""
        if not self.has_old_value(field): return False

        if isinstance(value, (tuple, list)):
            return self.old_value(field) in value
        else:
            return self.old_value(field) == value

    def value_is(self, field, value):
        """El valor del campo nuevo es `value`?."""
        if not self.has_new_value(field): return False

        if isinstance(value, (tuple, list)):
            return self.new_value(field) in value
        else:
            return self.new_value(field) == value

    def value_is_or_was(self, field, value):
        """El valor del campo nuevo es o fue `value`?."""
        return self.value_is(field, value) or self.value_was(field, value)

    def was_none(self, field):
        """El valor del campo era None?."""
        return self.was(field, None)


class FieldsChangesMixin(object):
    def track_fields_changes(self):
        if not self.id:
            self._original_state = None
        else:
            self.reset_state()

        self.changed_fields = ChangedFields()

    def reset_state(self):
        self._original_state = self._as_dict()

    def reset_fields_changes(self):
        self.changed_fields = self.get_changed_fields()
        self.reset_state()
        
    def _as_dict(self):
        return dict([(f.name, getattr(self, f.name)) for f in self._meta.local_fields if not f.rel])

    @property
    def dirty_fields(self):
        """
        devuelve los campos "sucios" osea que difieren con
        los de la base de datos.
        """
        return self.get_changed_fields()

    def is_field_dirty(self, field):
        """El campo esta sucio?."""
        return self.dirty_fields.has_key(field)

    def get_changed_fields(self):
        new_state = self._as_dict()

        ret = ChangedFields()

        for f, value in new_state.iteritems():
            if self._original_state:
                change = comparator.compare(self, f,
                                            self._original_state[f], value)
                if change: ret[f] = change
            else:
                ret[f] = { 'new_value': new_state[f] }

        return ret

    def is_dirty(self):
        if not self.pk:
            return True
        return {} != self.dirty_fields()
