from django.apps import apps
from django.conf import settings
from django.test import TestCase, override_settings
from django.utils import translation

from localized_fields.fields import LocalizedField
from localized_fields.value import LocalizedValue

from .fake_model import get_fake_model


@override_settings(LOCALIZED_FIELDS_EXPERIMENTAL=True)
class LocalizedLookupsTestCase(TestCase):
    """Tests whether localized lookups properly work with."""

    TestModel1 = None

    @classmethod
    def setUpClass(cls):
        """Creates the test model in the database."""

        super(LocalizedLookupsTestCase, cls).setUpClass()

        # reload app as setting has changed
        config = apps.get_app_config("localized_fields")
        config.ready()

        cls.TestModel = get_fake_model({"text": LocalizedField()})

    def test_localized_lookup(self):
        """Tests whether localized lookup properly works."""

        self.TestModel.objects.create(
            text=LocalizedValue(dict(en="text_en", ro="text_ro", nl="text_nl"))
        )

        # assert that it properly lookups the currently active language
        for lang_code, _ in settings.LANGUAGES:
            translation.activate(lang_code)
            assert self.TestModel.objects.filter(
                text="text_" + lang_code
            ).exists()

        # ensure that the default language is used in case no
        # language is active at all
        translation.deactivate_all()
        assert self.TestModel.objects.filter(text="text_en").exists()

        # ensure that hstore lookups still work
        assert self.TestModel.objects.filter(text__ro="text_ro").exists()
