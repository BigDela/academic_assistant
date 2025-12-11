"""
Django management command to seed the database with realistic test data.
Usage: python manage.py seed_data [--clear]
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from resources.models import Course, Tag, StudyGroup, Document, Friendship, Message
from users.models import UserProfile
import random
from datetime import datetime, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing test data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        with transaction.atomic():
            # Seed in order of dependencies
            tags = self.seed_tags()
            courses = self.seed_courses()
            users = self.seed_users()
            self.seed_user_profiles(users)
            groups = self.seed_study_groups(users, courses)
            self.seed_friendships(users)
            self.seed_group_messages(users, groups)
            
        self.stdout.write(self.style.SUCCESS('✅ Database seeding completed successfully!'))
        self.print_summary(users, courses, groups, tags)

    def clear_data(self):
        """Clear test data (preserve superusers)"""
        # Delete test users (not superusers)
        User.objects.filter(is_superuser=False, username__startswith='test_').delete()
        Course.objects.filter(name__contains='Test').delete()
        Tag.objects.filter(name__startswith='test_').delete()
        StudyGroup.objects.filter(name__contains='Test').delete()
        self.stdout.write(self.style.SUCCESS('Test data cleared'))

    def seed_tags(self):
        """Create interest tags for users"""
        tag_names = [
            'Python', 'JavaScript', 'Machine Learning', 'Web Development',
            'Data Science', 'Mobile Development', 'Cybersecurity', 'Cloud Computing',
            'AI', 'Databases', 'Algorithms', 'UI/UX', 'DevOps', 'Gaming'
        ]
        
        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(name=name)
            tags.append(tag)
            if created:
                self.stdout.write(f'  Created tag: {name}')
        
        return tags

    def seed_courses(self):
        """Create sample courses"""
        courses_data = [
            {'name': 'Introduction to Programming', 'description': 'Learn fundamentals of programming with Python'},
            {'name': 'Data Structures and Algorithms', 'description': 'Master core data structures and algorithmic thinking'},
            {'name': 'Web Development Fundamentals', 'description': 'Build modern web applications with HTML, CSS, JavaScript'},
            {'name': 'Database Management Systems', 'description': 'Design and implement relational databases'},
            {'name': 'Software Engineering Principles', 'description': 'Learn professional software development practices'},
        ]
        
        courses = []
        for data in courses_data:
            course, created = Course.objects.get_or_create(
                name=data['name'],
                defaults={'name': data['name']}
            )
            courses.append(course)
            if created:
                self.stdout.write(f'  Created course: {data["name"]}')
        
        return courses

    def seed_users(self):
        """Create 10 diverse test users"""
        users_data = [
            {
                'username': 'alice_wonder',
                'first_name': 'Alice',
                'last_name': 'Wonder',
                'email': 'alice@example.com',
                'course': 'CS',
                'year': '400',
                'bio': 'Senior CS student passionate about AI and machine learning. Love collaborating on challenging projects!',
                'program': 'Computer Science',
            },
            {
                'username': 'bob_builder',
                'first_name': 'Bob',
                'last_name': 'Builder',
                'email': 'bob@example.com',
                'course': 'ENG',
                'year': '300',
                'bio': 'Engineering enthusiast who enjoys building practical solutions. Always up for a study session!',
                'program': 'Software Engineering',
            },
            {
                'username': 'carol_coder',
                'first_name': 'Carol',
                'last_name': 'Coder',
                'email': 'carol@example.com',
                'course': 'CS',
                'year': '200',
                'bio': 'Web development and UI/UX designer. Looking for study partners for frontend projects.',
                'program': 'Computer Science',
            },
            {
                'username': 'david_data',
                'first_name': 'David',
                'last_name': 'Data',
                'email': 'david@example.com',
                'course': 'CS',
                'year': '400',
                'bio': 'Data science and analytics nerd. Let\'s visualize some data together!',
                'program': 'Data Science',
            },
            {
                'username': 'emma_engineer',
                'first_name': 'Emma',
                'last_name': 'Engineer',
                'email': 'emma@example.com',
                'course': 'ENG',
                'year': '300',
                'bio': 'Robotics and embedded systems enthusiast. Building the future one circuit at a time.',
                'program': 'Software Engineering',
            },
            {
                'username': 'frank_fullstack',
                'first_name': 'Frank',
                'last_name': 'Fullstack',
                'email': 'frank@example.com',
                'course': 'CS',
                'year': '300',
                'bio': 'Full-stack developer who loves both frontend and backend. React and Django are my jam!',
                'program': 'Computer Science',
            },
            {
                'username': 'grace_gamer',
                'first_name': 'Grace',
                'last_name': 'Gamer',
                'email': 'grace@example.com',
                'course': 'CS',
                'year': '200',
                'bio': 'Game development student. Currently working on a 2D platformer. Let\'s code and game!',
                'program': 'Computer Science',
            },
            {
                'username': 'henry_hacker',
                'first_name': 'Henry',
                'last_name': 'Hacker',
                'email': 'henry@example.com',
                'course': 'CS',
                'year': '400',
                'bio': 'Cybersecurity researcher. Interested in ethical hacking and network security.',
                'program': 'Information Technology',
            },
            {
                'username': 'iris_innovator',
                'first_name': 'Iris',
                'last_name': 'Innovator',
                'email': 'iris@example.com',
                'course': 'BUS',
                'year': '100',
                'bio': 'Business student learning to code. Interested in tech entrepreneurship and startups.',
                'program': 'Business Administration',
            },
            {
                'username': 'jack_junior',
                'first_name': 'Jack',
                'last_name': 'Junior',
                'email': 'jack@example.com',
                'course': 'ENG',
                'year': '100',
                'bio': 'First-year engineering student eager to learn. Excited about software development!',
                'program': 'Software Engineering',
            },
        ]
        
        users = []
        for data in users_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'email': data['email'],
                    'course': data['course'],
                    'year': data['year'],
                }
            )
            
            if created:
                user.set_password('testpass123')  # Default password for all test users
                user.save()
                self.stdout.write(f'  Created user: {data["username"]}')
            
            # Store program and bio for profile creation
            user._seed_program = data['program']
            user._seed_bio = data['bio']
            users.append(user)
        
        return users

    def seed_user_profiles(self, users):
        """Create profiles for seeded users"""
        all_tags = list(Tag.objects.all())
        
        for user in users:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'bio': user._seed_bio,
                    'program_of_study': user._seed_program,
                    'year_level': dict(User.YEAR_CHOICES).get(user.year, ''),
                    'theme_preference': random.choice(['light', 'dark']),
                }
            )
            
            if created:
                self.stdout.write(f'  Created profile for: {user.username}')

    def seed_study_groups(self, users, courses):
        """Create 5 diverse study groups"""
        groups_data = [
            {
                'name': 'Python Wizards 🐍',
                'description': 'Master Python programming together! We cover everything from basics to advanced topics like async programming and data science libraries.',
                'course': courses[0],  # Introduction to Programming
                'creator_index': 0,  # alice_wonder
                'member_indices': [0, 1, 2, 5, 6],  # 5 members
            },
            {
                'name': 'Algorithm Masters 🧠',
                'description': 'Tackle challenging algorithms and data structures. Prepare for coding interviews and competitive programming together!',
                'course': courses[1],  # Data Structures and Algorithms
                'creator_index': 3,  # david_data
                'member_indices': [0, 3, 5, 7],  # 4 members
            },
            {
                'name': 'Web Dev Squad 🌐',
                'description': 'Building modern web applications with React, Django, and more. Share projects, debug together, and learn best practices.',
                'course': courses[2],  # Web Development Fundamentals
                'creator_index': 2,  # carol_coder
                'member_indices': [2, 5, 6, 1, 4, 9],  # 6 members
            },
            {
                'name': 'Database Designers 💾',
                'description': 'Learn SQL, NoSQL, and database design patterns. Work on real-world database projects and optimization techniques.',
                'course': courses[3],  # Database Management Systems
                'creator_index': 1,  # bob_builder
                'member_indices': [1, 3, 4, 5],  # 4 members
            },
            {
                'name': 'Software Engineering Best Practices 🛠️',
                'description': 'Focus on clean code, design patterns, testing, and agile methodologies. Build production-ready software!',
                'course': courses[4],  # Software Engineering Principles
                'creator_index': 4,  # emma_engineer
                'member_indices': [1, 4, 5, 7, 9],  # 5 members
            },
        ]
        
        groups = []
        for data in groups_data:
            creator = users[data['creator_index']]
            
            group, created = StudyGroup.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'creator': creator,
                }
            )
            
            if created:
                # Add members
                for idx in data['member_indices']:
                    group.members.add(users[idx])
                
                # Creator is also an admin
                group.admins.add(creator)
                
                self.stdout.write(f'  Created group: {data["name"]} ({len(data["member_indices"])} members)')
            
            groups.append(group)
        
        return groups

    def seed_friendships(self, users):
        """Create friendships between some users"""
        friendship_pairs = [
            (0, 3),  # alice_wonder <-> david_data (both CS 400)
            (0, 7),  # alice_wonder <-> henry_hacker (both CS 400)
            (2, 5),  # carol_coder <-> frank_fullstack (CS students)
            (2, 6),  # carol_coder <-> grace_gamer (both CS 200)
            (1, 4),  # bob_builder <-> emma_engineer (both ENG 300)
            (1, 9),  # bob_builder <-> jack_junior (both ENG)
            (5, 7),  # frank_fullstack <-> henry_hacker (CS students)
        ]
        
        friendships_created = 0
        for idx1, idx2 in friendship_pairs:
            user1, user2 = users[idx1], users[idx2]
            
            # Create friendship if it doesn't exist
            if not Friendship.objects.filter(from_user=user1, to_user=user2).exists() and \
               not Friendship.objects.filter(from_user=user2, to_user=user1).exists():
                Friendship.objects.create(
                    from_user=user1,
                    to_user=user2,
                    status='accepted',
                )
                friendships_created += 1
        
        self.stdout.write(f'  Created {friendships_created} friendships')

    def seed_group_messages(self, users, groups):
        """Create sample messages in study groups"""
        message_templates = [
            "Hey everyone! Looking forward to studying together 📚",
            "Anyone free to meet this weekend for a study session?",
            "I found this great resource that might help: [link]",
            "Can someone explain the concept we covered last week?",
            "Great session today! Thanks for the help 🙌",
            "Who's ready for the upcoming exam?",
            "I've uploaded some notes to the group. Check them out!",
            "Does anyone have experience with the latest assignment?",
        ]
        
        messages_created = 0
        for group in groups:
            group_members = list(group.members.all())
            
            # Create 3-5 random messages per group
            num_messages = random.randint(3, 5)
            for i in range(num_messages):
                message_user = random.choice(group_members)
                message_text = random.choice(message_templates)
                
                Message.objects.create(
                    group=group,
                    user=message_user,
                    content=message_text,
                )
                messages_created += 1
        
        self.stdout.write(f'  Created {messages_created} group messages')

    def print_summary(self, users, courses, groups, tags):
        """Print a summary of seeded data"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('SEEDING SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'👥 Users created: {len(users)}')
        self.stdout.write(f'📚 Courses created: {len(courses)}')
        self.stdout.write(f'👥 Study groups created: {len(groups)}')
        self.stdout.write(f'🏷️  Tags created: {len(tags)}')
        self.stdout.write('\n' + self.style.WARNING('TEST USER CREDENTIALS:'))
        self.stdout.write('  Username: alice_wonder (or any other seeded username)')
        self.stdout.write('  Password: testpass123')
        self.stdout.write('\n' + self.style.WARNING('AVAILABLE TEST USERS:'))
        for user in users:
            self.stdout.write(f'  - {user.username} ({user.course} - {user.year} Level)')
        self.stdout.write('='*60 + '\n')
