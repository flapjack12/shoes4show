from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from shoes4show.forms import ItemForm, UserForm
from shoes4show.models import Item, Review, UserProfile, user_directory_path


class ModelTests(TestCase):
    def test_item_save_generates_slug(self):
        item = Item.objects.create(
            name="Red Boots",
            description="A stylish pair of boots",
            price=79.99,
            category="BO",
        )

        self.assertEqual(item.slug, "red-boots")

    def test_model_string_representations(self):
        item = Item.objects.create(
            name="White Sneakers",
            description="Classic sneakers",
            price=49.99,
            category="SN",
        )
        review = Review.objects.create(item=item, title="Great shoe", url="https://example.com/r1")
        user = User.objects.create_user(username="alice", password="SecretPass123!")
        profile = UserProfile.objects.create(user=user)

        self.assertEqual(str(item), "White Sneakers")
        self.assertEqual(str(review), "Great shoe")
        self.assertEqual(str(profile), "alice")

    def test_user_directory_path_builds_expected_location(self):
        instance = SimpleNamespace(user=SimpleNamespace(username="tester"))

        path = user_directory_path(instance, "avatar.png")

        self.assertEqual(path, "tester/profilepic/profile.png")


class FormTests(TestCase):
    def test_user_form_is_valid_with_matching_passwords(self):
        form = UserForm(
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "SafePass123!",
                "password2": "SafePass123!",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_item_form_is_valid_with_required_fields(self):
        image = SimpleUploadedFile(
            "shoe.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/gif",
        )
        form = ItemForm(
            data={
                "name": "Blue Heels",
                "description": "Elegant heels",
                "price": "59.99",
                "category": "HE",
                "views": "0",
                "likes": "0",
            },
            files={"image": image},
        )

        self.assertTrue(form.is_valid(), form.errors)


class PublicViewTests(TestCase):
    def setUp(self):
        self.item1 = Item.objects.create(
            name="Item One",
            description="First",
            price=10.00,
            likes=5,
            category="SN",
        )
        self.item2 = Item.objects.create(
            name="Item Two",
            description="Second",
            price=20.00,
            likes=8,
            category="BO",
        )
        Review.objects.create(item=self.item1, title="R1", url="https://example.com/1", views=1)
        Review.objects.create(item=self.item2, title="R2", url="https://example.com/2", views=9)

    def test_index_renders_popular_items_and_reviews(self):
        response = self.client.get(reverse("shoes4show:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shoes4show/index.html")
        self.assertEqual(response.context["items"][0], self.item2)
        self.assertEqual(response.context["reviews"][0].title, "R2")

    def test_show_listing_with_existing_slug(self):
        response = self.client.get(reverse("shoes4show:show_listing", kwargs={"shoe_slug": self.item1.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shoes4show/listing.html")
        self.assertEqual(response.context["shoe"], self.item1)

    def test_show_listing_with_missing_slug(self):
        response = self.client.get(reverse("shoes4show:show_listing", kwargs={"shoe_slug": "missing-shoe"}))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["shoe"])

    def test_show_listings_returns_all_items(self):
        response = self.client.get(reverse("shoes4show:show_listings"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shoes4show/listings.html")
        self.assertEqual(response.context["shoes"].count(), 2)

    def test_show_listings_by_category_filters_items(self):
        response = self.client.get(
            reverse("shoes4show:show_listings_by_category", kwargs={"category_name_slug": "BO"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shoes4show/listings.html")
        self.assertEqual(response.context["shoes"].count(), 1)
        self.assertEqual(response.context["shoes"][0], self.item2)
        self.assertEqual(response.context["category"], "Boots")

    def test_static_pages_render(self):
        for name in ["about", "contact_us", "site_map", "shoe_size_conversion"]:
            response = self.client.get(reverse(f"shoes4show:{name}"))
            self.assertEqual(response.status_code, 200)


class AuthenticationAndProtectedViewTests(TestCase):
    def setUp(self):
        self.password = "LoginPass123!"
        self.user = User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password=self.password,
        )

    def test_register_creates_user_profile_and_logs_user_in(self):
        response = self.client.post(
            reverse("shoes4show:register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "SafePass123!",
                "password2": "SafePass123!",
            },
        )

        self.assertRedirects(response, reverse("shoes4show:account"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        created_user = User.objects.get(username="newuser")
        self.assertTrue(UserProfile.objects.filter(user=created_user).exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_when_authenticated_redirects_to_account(self):
        self.client.login(username="loginuser", password=self.password)

        response = self.client.get(reverse("shoes4show:register"))

        self.assertRedirects(response, reverse("shoes4show:account"))

    def test_login_with_valid_credentials_redirects_to_account(self):
        response = self.client.post(
            reverse("shoes4show:login"),
            {"username": "loginuser", "password": self.password},
        )

        self.assertRedirects(response, reverse("shoes4show:account"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_invalid_credentials_shows_error(self):
        response = self.client.post(
            reverse("shoes4show:login"),
            {"username": "loginuser", "password": "wrong-pass"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_account_and_restricted_require_authentication(self):
        account_response = self.client.get(reverse("shoes4show:account"))
        restricted_response = self.client.get(reverse("shoes4show:restricted"))

        self.assertEqual(account_response.status_code, 302)
        self.assertIn(reverse("shoes4show:login"), account_response.url)
        self.assertEqual(restricted_response.status_code, 302)
        self.assertIn(reverse("shoes4show:login"), restricted_response.url)

    def test_logout_clears_session_and_redirects_to_index(self):
        self.client.login(username="loginuser", password=self.password)

        response = self.client.get(reverse("shoes4show:logout"))

        self.assertRedirects(response, reverse("shoes4show:index"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_add_listing_requires_login(self):
        response = self.client.get(reverse("shoes4show:add_listing"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("shoes4show:login"), response.url)

    def test_add_listing_with_missing_required_fields_does_not_create_item(self):
        self.client.login(username="loginuser", password=self.password)

        response = self.client.post(
            reverse("shoes4show:add_listing"),
            {
                "name": "Fresh Kicks",
                "description": "Brand new pair",
                "price": "99.99",
                "category": "SN",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Item.objects.filter(name="Fresh Kicks").exists())


class SearchViewTests(TestCase):
    @patch("shoes4show.views.run_query")
    def test_search_context_when_trigram_used(self, mock_run_query):
        mock_run_query.return_value = ([], True, "shoee", "shoe", ["shoee", "none", "none"])

        response = self.client.get(reverse("shoes4show:search"), {"query": "shoee"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shoes4show/listings.html")
        self.assertTrue(response.context["used_trigram"])
        self.assertEqual(response.context["new_word"], "shoe")

    @patch("shoes4show.views.run_query")
    def test_search_context_when_trigram_not_used(self, mock_run_query):
        mock_run_query.return_value = ([], False, "shoe", "", ["shoe", "none", "none"])

        response = self.client.get(reverse("shoes4show:search"), {"query": "shoe"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shoes4show/listings.html")
        self.assertNotIn("used_trigram", response.context)
        self.assertEqual(response.context["old_word"], "shoe")
