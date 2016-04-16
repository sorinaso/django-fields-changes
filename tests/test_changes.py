"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import types
from django.db import models

from django.test import TestCase
from fields_changes.models import FieldsChangesMixin
from fields_changes.models import ChangedFields

class TestfieldChangesModel(models.Model, FieldsChangesMixin):
    def __init__(self, *args, **kwargs):
        super(TestfieldChangesModel, self).__init__(*args, **kwargs)
        self.track_fields_changes()

    def pre_save(self):
        pass

    def post_save(self, was_created):
        pass

    def save(self, *args, **kwargs):
        self.pre_save()
        super(TestfieldChangesModel, self).save()
        self.reset_fields_changes()
        self.post_save(None)

    test = models.CharField(max_length=25)
    test2 = models.IntegerField()


class DirtyFieldsTest(TestCase):
    def test_dirty(self):
        c = TestfieldChangesModel(test="test", test2=2)

        def pre_save(self):
            self.test_pre_save_dirty_fields = self.dirty_fields

        def post_save(self, was_created):
            self.test_post_save_changed_fields = self.changed_fields

        c.pre_save = types.MethodType(pre_save, c)
        c.post_save = types.MethodType(post_save, c)

        self.assertDictEqual(c.dirty_fields, {
            'test': { 'new_value': 'test' },
            'test2': { 'new_value': 2 },
            'id': { 'new_value': None }
        })
        self.assertDictEqual(c.changed_fields, {})

        c.save()
        self.assertDictEqual(c.test_pre_save_dirty_fields, {
            'test': { 'new_value': 'test' },
            'test2': { 'new_value': 2 },
            'id': { 'new_value': None}
        })
        self.assertDictEqual(c.test_post_save_changed_fields, {
            'test': { 'new_value': 'test' },
            'test2': { 'new_value': 2 },
            'id': { 'new_value': 1}
        })
        self.assertDictEqual(c.dirty_fields,{})


        c_old_test = c.test
        c.test = "test_changed"
        c.save()
        self.assertDictEqual(c.test_pre_save_dirty_fields, {
            'test': { 'old_value': c_old_test, 'new_value': c.test }
        })
        self.assertDictEqual(c.test_post_save_changed_fields, {
            'test': { 'old_value': c_old_test, 'new_value': c.test }
        })

        c_old_test = c.test
        c.test = "test_changed2"
        c_old_test2 = c.test2
        c.test2 = 4
        c.save()
        self.assertDictEqual(c.test_pre_save_dirty_fields, {
            'test': { 'old_value': c_old_test, 'new_value': c.test },
            'test2': { 'old_value': c_old_test2, 'new_value': c.test2 }
        })
        self.assertDictEqual(c.test_post_save_changed_fields, {
            'test': { 'old_value': c_old_test, 'new_value': c.test },
            'test2': { 'old_value': c_old_test2, 'new_value': c.test2 }
        })

class ChangedFieldsTest(TestCase):
    def setUp(self):
        self.changed_fields = ChangedFields({
            'field1' : {
                'new_value': 'new_value1',
                'old_value': 'old_value1'
            },
            'field2' : {
                'new_value': 'new_value2',
                'old_value': 'old_value2'
            }
        })

    def test_diff(self):
        """Testea que se haga bien un diff."""
        self.assertListEqual(self.changed_fields.diff(['field1']), ['field2'])
        self.assertListEqual(self.changed_fields.diff(['field1', 'field3'], left=False), ['field3'])

    def test_field_names(self):
        self.assertItemsEqual(self.changed_fields.field_names(), ['field1', 'field2'])

    def test_has_changed(self):
        self.assertTrue(self.changed_fields.has_changed('field1',
                        old_value='old_value1', new_value='new_value1'))
        self.assertTrue(self.changed_fields.has_changed('field1',
                        old_value=('old_value1', 'old_value2'), new_value=('new_value1','new_value2')))
        self.assertFalse(self.changed_fields.has_changed('field1',
                        old_value='old_value1', new_value='new_value2'))
        self.assertFalse(self.changed_fields.has_changed('field1',
                        old_value='old_value2', new_value='new_value1'))
        self.assertFalse(self.changed_fields.has_changed('field1',
                        old_value='old_value2', new_value='new_value2'))
        self.assertFalse(self.changed_fields.has_changed('field1',
                        old_value=('old_value2', 'old_value3'), new_value=('new_value2', 'new_value3')))

    def test_only_has_changed(self):
        self.assertFalse(self.changed_fields.only_has_changed('field2'))
        self.assertFalse(self.changed_fields.only_has_changed('field2',
            old_value='old_value2', new_value='new_value2'))
        self.assertFalse(self.changed_fields.only_has_changed('field2',
            old_value='old_value2', new_value='new_value3'))

        del self.changed_fields['field1']

        self.assertTrue(self.changed_fields.only_has_changed('field2'))
        self.assertTrue(self.changed_fields.only_has_changed('field2',
            old_value='old_value2', new_value='new_value2'))
        self.assertTrue(self.changed_fields.only_has_changed('field2',
            old_value=('old_value2', 'old_value3'), new_value=('new_value2', 'new_value3')))
        self.assertFalse(self.changed_fields.only_has_changed('field2',
            old_value='old_value2', new_value='new_value3'))
