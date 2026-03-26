import json
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
        user = User.objects.create_user(username="alice", password="SecretPass123!")
        profile = UserProfile.objects.create(user=user)
        review = Review.objects.create(
            item=item,
            user=user,
            title="Great shoe",
            review_text="Very comfortable.",
            rating=5,
            url="https://example.com/r1",
        )

        self.assertEqual(str(item), "White Sneakers")
        self.assertEqual(str(review), "Great shoe (5)")
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
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@example.com",
                "password1": "SafePass123!",
                "password2": "SafePass123!",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_user_form_is_invalid_when_passwords_do_not_match(self):
        form = UserForm(
            data={
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@example.com",
                "password1": "SafePass123!",
                "password2": "DifferentPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_user_form_is_invalid_when_required_fields_missing(self):
        form = UserForm(
            data={
                "username": "",
                "first_name": "",
                "last_name": "",
                "email": "",
                "password1": "",
                "password2": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("email", form.errors)

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
            },
            files={"image": image},
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_item_form_is_invalid_without_required_image(self):
        form = ItemForm(
            data={
                "name": "Blue Heels",
                "description": "Elegant heels",
                "price": "59.99",
                "category": "HE",
                "views": "0",
            },
            files={},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)


class PublicViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="SafePass123!")
        UserProfile.objects.create(user=self.user)
        image1 = SimpleUploadedFile(
            "item-one.gif",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/gif",
        )
        image2 = SimpleUploadedFile(
            "item-two.gif",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/gif",
        )
        self.item1 = Item.objects.create(
            name="Item One",
            description="First",
            image=image1,
            price=10.00,
            views=3,
            category="SN",
            uploaded_by=self.user,
        )
        self.item2 = Item.objects.create(
            name="Item Two",
            description="Second",
            image=image2,
            price=20.00,
            views=9,
            category="BO",
            uploaded_by=self.user,
        )
        Review.objects.create(
            item=self.item1,
            user=self.user,
            title="R1",
            review_text="Good pair",
            rating=4,
            url="https://example.com/1",
            views=1,
        )
        Review.objects.create(
            item=self.item2,
            user=self.user,
            title="R2",
            review_text="Excellent pair",
            rating=5,
            url="https://example.com/2",
            views=9,
        )

    def test_index_renders_popular_items(self):
        response = self.client.get(reverse("shoes4show:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shoes4show/index.html")
        self.assertEqual(list(response.context["items"][0]), [self.item2, self.item1])
        self.assertEqual(list(response.context["items"][1]), [])
        self.assertEqual(list(response.context["items"][2]), [])

    def test_show_listing_with_existing_slug(self):
        original_views = self.item1.views
        response = self.client.get(reverse("shoes4show:show_listing", kwargs={"shoe_slug": self.item1.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shoes4show/listing.html")
        self.assertEqual(response.context["shoe"], self.item1)
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.views, original_views + 1)

    def test_show_listing_with_missing_slug(self):
        response = self.client.get(reverse("shoes4show:show_listing", kwargs={"shoe_slug": "missing-shoe"}))

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["shoe"])

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
        UserProfile.objects.create(user=self.user)

    def test_register_creates_user_profile_and_logs_user_in(self):
        response = self.client.post(
            reverse("shoes4show:register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
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

    def test_register_with_mismatched_passwords_does_not_create_user(self):
        response = self.client.post(
            reverse("shoes4show:register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "newuser@example.com",
                "password1": "SafePass123!",
                "password2": "DifferentPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())
        self.assertContains(response, "Please correct the errors below.")

    def test_register_with_missing_required_fields_does_not_create_user(self):
        response = self.client.post(
            reverse("shoes4show:register"),
            {
                "username": "",
                "first_name": "",
                "last_name": "",
                "email": "",
                "password1": "",
                "password2": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="").count(), 0)
        self.assertContains(response, "Please correct the errors below.")

    def test_register_with_duplicate_username_does_not_create_second_user(self):
        response = self.client.post(
            reverse("shoes4show:register"),
            {
                "username": "loginuser",
                "first_name": "Another",
                "last_name": "User",
                "email": "another@example.com",
                "password1": "SafePass123!",
                "password2": "SafePass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="loginuser").count(), 1)
        self.assertContains(response, "Please correct the errors below.")

    def test_register_with_weak_password_does_not_create_user(self):
        response = self.client.post(
            reverse("shoes4show:register"),
            {
                "username": "weakpassuser",
                "first_name": "Weak",
                "last_name": "Password",
                "email": "weakpass@example.com",
                "password1": "12345678",
                "password2": "12345678",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="weakpassuser").exists())
        self.assertContains(response, "Please correct the errors below.")

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

    def test_login_with_empty_credentials_shows_error(self):
        response = self.client.post(
            reverse("shoes4show:login"),
            {"username": "", "password": ""},
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


class ReviewAndRatingViewTests(TestCase):
    def setUp(self):
        self.password = "ReviewPass123!"
        self.user = User.objects.create_user(
            username="reviewuser",
            email="reviewuser@example.com",
            password=self.password,
        )
        UserProfile.objects.create(user=self.user)
        image = SimpleUploadedFile(
            "review-item.gif",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/gif",
        )
        self.item = Item.objects.create(
            name="Review Item",
            description="Item used for review tests",
            image=image,
            price=70.00,
            category="SN",
            uploaded_by=self.user,
        )

    def test_add_review_requires_login(self):
        response = self.client.post(
            reverse("shoes4show:add_review", kwargs={"shoe_slug": self.item.slug}),
            {"review_text": "Nice", "rating": 5},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("shoes4show:login"), response.url)

    def test_add_review_creates_review_for_valid_form(self):
        self.client.login(username="reviewuser", password=self.password)
        response = self.client.post(
            reverse("shoes4show:add_review", kwargs={"shoe_slug": self.item.slug}),
            {"review_text": "Great fit", "rating": 5},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(item=self.item, user=self.user).count(), 1)
        created_review = Review.objects.get(item=self.item, user=self.user)
        self.assertEqual(created_review.review_text, "Great fit")
        self.assertEqual(created_review.rating, 5)

    def test_add_review_invalid_form_does_not_create_review(self):
        self.client.login(username="reviewuser", password=self.password)
        response = self.client.post(
            reverse("shoes4show:add_review", kwargs={"shoe_slug": self.item.slug}),
            {"review_text": "", "rating": 5},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(item=self.item, user=self.user).count(), 0)

    def test_add_rating_creates_review_with_blank_text_when_missing(self):
        self.client.login(username="reviewuser", password=self.password)
        response = self.client.post(
            reverse("shoes4show:add_rating", kwargs={"shoe_slug": self.item.slug}),
            data=json.dumps({"rating": 4}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"rating": 4})
        created_review = Review.objects.get(item=self.item, user=self.user)
        self.assertEqual(created_review.rating, 4)
        self.assertEqual(created_review.review_text, "")

    def test_add_rating_updates_existing_review_rating(self):
        self.client.login(username="reviewuser", password=self.password)
        Review.objects.create(
            item=self.item,
            user=self.user,
            title="Existing",
            review_text="Old text",
            rating=2,
        )

        response = self.client.post(
            reverse("shoes4show:add_rating", kwargs={"shoe_slug": self.item.slug}),
            data=json.dumps({"rating": 5}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        updated_review = Review.objects.get(item=self.item, user=self.user)
        self.assertEqual(updated_review.rating, 5)
        self.assertEqual(updated_review.review_text, "Old text")

    def test_add_rating_with_invalid_json_returns_400(self):
        self.client.login(username="reviewuser", password=self.password)
        response = self.client.post(
            reverse("shoes4show:add_rating", kwargs={"shoe_slug": self.item.slug}),
            data="not-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.filter(item=self.item, user=self.user).count(), 0)

    def test_add_rating_with_out_of_range_value_returns_400(self):
        self.client.login(username="reviewuser", password=self.password)
        response = self.client.post(
            reverse("shoes4show:add_rating", kwargs={"shoe_slug": self.item.slug}),
            data=json.dumps({"rating": 6}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.filter(item=self.item, user=self.user).count(), 0)


class ReviewerBadgeSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="badgeuser", password="BadgePass123!")
        self.profile = UserProfile.objects.create(user=self.user)
        image = SimpleUploadedFile(
            "badge-item.gif",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/gif",
        )
        self.item = Item.objects.create(
            name="Badge Item",
            description="Item used for badge threshold tests",
            image=image,
            price=12.00,
            category="SN",
            uploaded_by=self.user,
        )

    def test_reviewer_badge_stays_false_below_threshold(self):
        for idx in range(99):
            Review.objects.create(
                item=self.item,
                user=self.user,
                title=f"R{idx}",
                review_text="review text",
                rating=5,
            )

        self.profile.refresh_from_db()
        self.assertFalse(self.profile.reviewer_badge)

    def test_reviewer_badge_turns_true_at_threshold(self):
        for idx in range(100):
            Review.objects.create(
                item=self.item,
                user=self.user,
                title=f"R{idx}",
                review_text="review text",
                rating=5,
            )

        self.profile.refresh_from_db()
        self.assertTrue(self.profile.reviewer_badge)


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

    @patch("shoes4show.views.run_query")
    def test_search_annotates_average_rating_and_review_count_from_queryset(self, mock_run_query):
        user = User.objects.create_user(username="searchuser", password="SearchPass123!")
        UserProfile.objects.create(user=user)
        image1 = SimpleUploadedFile(
            "search-item-1.gif",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/gif",
        )
        image2 = SimpleUploadedFile(
            "search-item-2.gif",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b",
            content_type="image/gif",
        )
        item1 = Item.objects.create(
            name="Search Item One",
            description="First search item",
            image=image1,
            price=15.00,
            category="SN",
            uploaded_by=user,
        )
        item2 = Item.objects.create(
            name="Search Item Two",
            description="Second search item",
            image=image2,
            price=18.00,
            category="BO",
            uploaded_by=user,
        )
        Review.objects.create(item=item1, user=user, review_text="good", rating=4)
        Review.objects.create(item=item1, user=user, review_text="great", rating=5)

        mock_run_query.return_value = (Item.objects.filter(id__in=[item1.id, item2.id]), False, "shoe", "", ["shoe", "none", "none"])

        response = self.client.get(reverse("shoes4show:search"), {"query": "shoe"})

        self.assertEqual(response.status_code, 200)
        result_list = list(response.context["result_list"])
        result_by_name = {item.name: item for item in result_list}
        self.assertEqual(result_by_name["Search Item One"].average_rating, 4)
        self.assertEqual(result_by_name["Search Item One"].review_count, 2)
        self.assertEqual(result_by_name["Search Item Two"].average_rating, 0)
        self.assertEqual(result_by_name["Search Item Two"].review_count, 0)
