from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates UserProfile for all users who don\'t have one'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = users_without_profile.count()
        
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            self.stdout.write(f'Created profile for {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} user profiles')
        )
