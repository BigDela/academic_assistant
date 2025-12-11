# Database Seeding Guide

## Overview
The `seed_data` management command populates the database with realistic test data for development and testing purposes.

## Usage

### Basic Seeding
```powershell
python manage.py seed_data
```

### Clear and Re-seed
```powershell
python manage.py seed_data --clear
```
The `--clear` flag removes existing test data before seeding (preserves superusers).

## What Gets Seeded

### 1. Users (10 diverse test accounts)
- **alice_wonder** - CS 400 (AI & ML enthusiast)
- **bob_builder** - ENG 300 (Software Engineering)
- **carol_coder** - CS 200 (Web Dev & UI/UX)
- **david_data** - CS 400 (Data Science)
- **emma_engineer** - ENG 300 (Robotics)
- **frank_fullstack** - CS 300 (Full-stack developer)
- **grace_gamer** - CS 200 (Game development)
- **henry_hacker** - CS 400 (Cybersecurity)
- **iris_innovator** - BUS 100 (Tech entrepreneurship)
- **jack_junior** - ENG 100 (First-year)

**Default Password:** `testpass123`

Each user has:
- Unique bio and interests
- Profile with program of study
- Course and year level
- Random theme preference

### 2. Courses (5 academic courses)
- Introduction to Programming
- Data Structures and Algorithms
- Web Development Fundamentals
- Database Management Systems
- Software Engineering Principles

### 3. Study Groups (5 active groups)
- **Python Wizards 🐍** - 5 members
- **Algorithm Masters 🧠** - 4 members
- **Web Dev Squad 🌐** - 6 members
- **Database Designers 💾** - 4 members
- **Software Engineering Best Practices 🛠️** - 5 members

Each group has:
- Description
- Creator/admin
- Multiple members
- Related course

### 4. Friendships (7 connections)
Pre-established friendships between users with similar interests:
- alice_wonder ↔ david_data (both CS 400)
- alice_wonder ↔ henry_hacker (both CS 400)
- carol_coder ↔ frank_fullstack (CS students)
- carol_coder ↔ grace_gamer (both CS 200)
- bob_builder ↔ emma_engineer (both ENG 300)
- bob_builder ↔ jack_junior (both ENG)
- frank_fullstack ↔ henry_hacker (CS students)

### 5. Group Messages (19-25 messages)
Each study group has 3-5 sample messages from members:
- Welcome messages
- Study session invitations
- Resource sharing
- Questions and discussions

### 6. Tags (14 interest tags)
Python, JavaScript, Machine Learning, Web Development, Data Science, Mobile Development, Cybersecurity, Cloud Computing, AI, Databases, Algorithms, UI/UX, DevOps, Gaming

## Testing the Discovery System

After seeding, you can test:

### Friend Discovery
1. Login as any test user (e.g., `alice_wonder` / `testpass123`)
2. Navigate to **Discover → Discover People**
3. See recommendations based on:
   - Same course (highest priority)
   - Same year (medium priority)
   - Same program (lower priority)
4. Accept/reject recommendations
5. Mutual acceptance creates friendship

### Group Discovery
1. Login as any test user
2. Navigate to **Discover → Discover Groups**
3. See group recommendations with match scores
4. Join groups (requires admin approval)
5. View requests in "My Join Requests"

### Group Admin Flow
1. Login as group creator (e.g., `alice_wonder` for Python Wizards)
2. Navigate to **Discover → Manage Join Requests**
3. Approve/reject join requests
4. New members get access to group chat

## Verification

Run the verification script:
```powershell
Get-Content verify_seed.py | python manage.py shell
```

Expected output:
```
✓ Test Users: 10/10
✓ User Profiles: 10/10
✓ Study Groups: 7 (5 seeded + 2 existing)
✓ Friendships: 8
✓ Group Messages: 33
✓ Courses: 5
✓ Tags: 14
```

## Re-running Safely

The seeding script is idempotent:
- Uses `get_or_create()` to avoid duplicates
- Checks for existing data before creating
- Can be run multiple times without errors

### Clear Before Re-seed
```powershell
python manage.py seed_data --clear
```
This removes only test users (usernames starting with test data patterns) and related data, preserving:
- Superuser accounts
- Production users
- Non-test courses/groups

## Integration with Features

The seeded data enables testing of:
- ✅ User discovery matching algorithm
- ✅ Friend request system
- ✅ Group join request workflow
- ✅ Admin approval flow
- ✅ Group chat functionality
- ✅ Private messaging (between friends)
- ✅ Profile viewing
- ✅ Course filtering
- ✅ Search functionality

## Notes

- All test users have the same password: `testpass123`
- Users are diverse across programs, years, and interests
- Groups have varying sizes (3-6 members)
- Friendships reflect logical connections (same course/year)
- Messages create realistic group chat history
- Safe to run in development environment only

## Cleanup

To remove all seeded test data:
```powershell
python manage.py seed_data --clear
```

This will:
- Delete users with test usernames
- Remove associated profiles
- Delete test courses and groups
- Clear friendships and messages
- Preserve superuser and non-test data
