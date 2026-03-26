from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review, UserProfile


@receiver(post_save,sender=Review)
def award_reviewer_badge(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        profile = UserProfile.objects.get(user=user)

        review_count = Review.objects.filter(user=user).count()

        if review_count >= 100 and not profile.reviewer_badge:
            profile.reviewer_badge = True
            profile.save()
