from django.contrib.auth import get_user_model
from resources.models import StudyGroup, Friendship, Message, Course, Tag
from users.models import UserProfile

User = get_user_model()

# Count seeded test users
test_users = ['alice_wonder', 'bob_builder', 'carol_coder', 'david_data', 
              'emma_engineer', 'frank_fullstack', 'grace_gamer', 'henry_hacker',
              'iris_innovator', 'jack_junior']
user_count = User.objects.filter(username__in=test_users).count()

print("=" * 60)
print("DATABASE VERIFICATION")
print("=" * 60)
print(f"✓ Test Users: {user_count}/10")
print(f"✓ User Profiles: {UserProfile.objects.filter(user__username__in=test_users).count()}/10")
print(f"✓ Study Groups: {StudyGroup.objects.count()}")
print(f"✓ Friendships: {Friendship.objects.filter(status='accepted').count()}")
print(f"✓ Group Messages: {Message.objects.count()}")
print(f"✓ Courses: {Course.objects.count()}")
print(f"✓ Tags: {Tag.objects.count()}")

print("\n" + "=" * 60)
print("SAMPLE DATA")
print("=" * 60)

# Show first user
if user_count > 0:
    alice = User.objects.get(username='alice_wonder')
    print(f"\nUser: {alice.username}")
    print(f"  Name: {alice.get_full_name()}")
    print(f"  Email: {alice.email}")
    print(f"  Course: {alice.course}")
    print(f"  Year: {alice.year}")
    print(f"  Bio: {alice.profile.bio[:50]}...")
    print(f"  Program: {alice.profile.program_of_study}")

# Show groups alice is in
alice_groups = StudyGroup.objects.filter(members=alice)
print(f"\nAlice's Groups ({alice_groups.count()}):")
for group in alice_groups:
    print(f"  - {group.name} ({group.members.count()} members)")

# Show alice's friends
alice_friendships = Friendship.objects.filter(
    from_user=alice, status='accepted'
)
print(f"\nAlice's Friends ({alice_friendships.count()}):")
for friendship in alice_friendships:
    print(f"  - {friendship.to_user.username}")

print("\n" + "=" * 60)
