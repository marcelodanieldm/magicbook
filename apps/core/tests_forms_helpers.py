"""Unit tests for forms: RegisterForm, ProjectCreateForm and helper utilities."""

from django.test import TestCase
from django.contrib.auth.models import User

from apps.accounts.forms import RegisterForm
from apps.core.forms import ProjectCreateForm
from apps.core.views import _extract_base_price, _first_text, _find_first_image_url, _market_context
from apps.core.models import Project, OfferStructure


# ─────────────────────────────────────────────
# RegisterForm
# ─────────────────────────────────────────────

class RegisterFormTests(TestCase):

    def _valid_data(self, **overrides):
        base = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
        }
        base.update(overrides)
        return base

    def test_valid_form_is_valid(self):
        form = RegisterForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_mismatched_passwords_are_invalid(self):
        form = RegisterForm(data=self._valid_data(password_confirm='different'))
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_duplicate_username_is_invalid(self):
        User.objects.create_user(username='newuser', password='x')
        form = RegisterForm(data=self._valid_data())
        self.assertFalse(form.is_valid())

    def test_save_hashes_password(self):
        form = RegisterForm(data=self._valid_data())
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.check_password('securepass123'))
        self.assertNotEqual(user.password, 'securepass123')

    def test_empty_email_is_allowed(self):
        # email is optional on User model by default
        form = RegisterForm(data=self._valid_data(email=''))
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_email_format_is_rejected(self):
        form = RegisterForm(data=self._valid_data(email='not-an-email'))
        self.assertFalse(form.is_valid())


# ─────────────────────────────────────────────
# ProjectCreateForm
# ─────────────────────────────────────────────

class ProjectCreateFormTests(TestCase):

    def _valid_data(self, **overrides):
        base = {
            'niche_input': 'Quiero vender un curso de cocina vegana',
            'brand_voice': 'mentor',
            'ai_model': 'gpt-4o',
            'primary_market': 'LATAM',
            'target_markets': ['LATAM'],
        }
        base.update(overrides)
        return base

    def test_valid_form_is_valid(self):
        form = ProjectCreateForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_niche_input_is_invalid(self):
        data = self._valid_data()
        data.pop('niche_input')
        form = ProjectCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('niche_input', form.errors)

    def test_invalid_brand_voice_is_rejected(self):
        form = ProjectCreateForm(data=self._valid_data(brand_voice='unknown_voice'))
        self.assertFalse(form.is_valid())

    def test_invalid_ai_model_is_rejected(self):
        form = ProjectCreateForm(data=self._valid_data(ai_model='gpt-99'))
        self.assertFalse(form.is_valid())

    def test_clean_target_markets_adds_primary_market(self):
        """Primary market should always be injected into target_markets."""
        form = ProjectCreateForm(data=self._valid_data(
            primary_market='MX',
            target_markets=['AR'],  # MX not included
        ))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn('MX', form.cleaned_data['target_markets'])

    def test_target_markets_empty_still_includes_primary(self):
        form = ProjectCreateForm(data=self._valid_data(
            primary_market='CO',
            target_markets=[],
        ))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn('CO', form.cleaned_data['target_markets'])

    def test_all_brand_voice_choices_are_valid(self):
        for voice, _ in [('mentor', ''), ('friend', ''), ('scientist', ''), ('coach', ''), ('expert', '')]:
            form = ProjectCreateForm(data=self._valid_data(brand_voice=voice))
            self.assertTrue(form.is_valid(), f"Voice '{voice}' should be valid. Errors: {form.errors}")


# ─────────────────────────────────────────────
# _extract_base_price helper
# ─────────────────────────────────────────────

class ExtractBasePriceTests(TestCase):

    def test_returns_default_when_offer_is_none(self):
        self.assertEqual(_extract_base_price(None), '$27 USD')

    def test_returns_your_investment_when_set(self):
        offer = OfferStructure()
        offer.your_investment = '$97 USD'
        offer.price_points = []
        self.assertEqual(_extract_base_price(offer), '$97 USD')

    def test_returns_price_from_price_points_when_no_investment(self):
        offer = OfferStructure()
        offer.your_investment = ''
        offer.price_points = [{'price': '47'}]
        self.assertEqual(_extract_base_price(offer), '$47 USD')

    def test_returns_default_when_no_price_info(self):
        offer = OfferStructure()
        offer.your_investment = ''
        offer.price_points = []
        self.assertEqual(_extract_base_price(offer), '$27 USD')

    def test_returns_default_when_price_points_missing_price_key(self):
        offer = OfferStructure()
        offer.your_investment = ''
        offer.price_points = [{'label': 'Basic'}]
        self.assertEqual(_extract_base_price(offer), '$27 USD')


# ─────────────────────────────────────────────
# _first_text helper
# ─────────────────────────────────────────────

class FirstTextTests(TestCase):

    def test_plain_string(self):
        self.assertEqual(_first_text('hello'), 'hello')

    def test_empty_string_returns_empty(self):
        self.assertEqual(_first_text(''), '')

    def test_list_of_strings_returns_first_nonempty(self):
        self.assertEqual(_first_text(['', 'world']), 'world')

    def test_nested_dict_extracts_title(self):
        self.assertEqual(_first_text({'title': 'My Title'}), 'My Title')

    def test_nested_dict_extracts_name_when_no_title(self):
        self.assertEqual(_first_text({'name': 'My Name'}), 'My Name')

    def test_deeply_nested_structure(self):
        result = _first_text({'data': [{'title': 'Deep'}]})
        self.assertEqual(result, 'Deep')

    def test_none_returns_empty(self):
        self.assertEqual(_first_text(None), '')

    def test_integer_returns_empty(self):
        self.assertEqual(_first_text(42), '')


# ─────────────────────────────────────────────
# _find_first_image_url helper
# ─────────────────────────────────────────────

class FindFirstImageUrlTests(TestCase):

    PNG_URL = 'https://example.com/image.png'
    JPG_URL = 'https://example.com/photo.jpg'

    def test_plain_string_url(self):
        self.assertEqual(_find_first_image_url(self.PNG_URL), self.PNG_URL)

    def test_non_image_url_returns_empty(self):
        self.assertEqual(_find_first_image_url('https://example.com/page'), '')

    def test_dict_with_image_key(self):
        self.assertEqual(_find_first_image_url({'image': self.JPG_URL}), self.JPG_URL)

    def test_dict_with_thumbnail_key(self):
        self.assertEqual(_find_first_image_url({'thumbnail': self.PNG_URL}), self.PNG_URL)

    def test_list_of_dicts(self):
        result = _find_first_image_url([
            {'title': 'no image'},
            {'image': self.JPG_URL},
        ])
        self.assertEqual(result, self.JPG_URL)

    def test_nested_structure(self):
        data = {'results': [{'assets': {'image_url': self.PNG_URL}}]}
        self.assertEqual(_find_first_image_url(data), self.PNG_URL)

    def test_empty_dict_returns_empty(self):
        self.assertEqual(_find_first_image_url({}), '')

    def test_none_returns_empty(self):
        self.assertEqual(_find_first_image_url(None), '')


# ─────────────────────────────────────────────
# _market_context helper
# ─────────────────────────────────────────────

class MarketContextTests(TestCase):

    def _make_project_obj(self, primary, targets):
        """Create an unsaved Project-like object for testing the helper."""
        user = User.objects.create_user(username=f'mktuser_{primary}_{len(targets)}', password='x')
        p = Project(user=user, niche_input='test', primary_market=primary, target_markets=targets)
        return p

    def test_uses_target_markets_when_set(self):
        p = self._make_project_obj('MX', ['MX', 'AR'])
        self.assertEqual(_market_context(p), 'MX, AR')

    def test_falls_back_to_primary_market_when_targets_empty(self):
        p = self._make_project_obj('CO', [])
        self.assertEqual(_market_context(p), 'CO')
