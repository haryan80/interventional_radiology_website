#!/usr/bin/env python
"""
Script to update the conference schedule with the detailed program information
and update speaker information, including Dr. Cagatay Arslan's bio.
"""

import os
import django
import re
from datetime import datetime, time, date
from django.db.models import Q

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khcc_conference.settings')
django.setup()

from conference.models import Speaker, Session, ScheduleItem  # noqa: E402

def update_speaker_bio(name, bio, title=None, institution=None):
    """Update a speaker's bio and other information."""
    # Try different variations of the name to find a match
    name_variations = [
        name,
        name.replace("Dr. ", ""),
        name.replace("Dr ", ""),
        name.replace("Prof. ", ""),
        name.replace("Prof ", "")
    ]
    
    # Also add a variation with just the last name if it contains spaces
    if " " in name:
        last_name = name.split()[-1]
        name_variations.append(last_name)
    
    # Try to find the speaker by any of the name variations
    speaker = None
    for name_var in name_variations:
        try:
            # Try exact match first
            speaker = Speaker.objects.filter(
                Q(name__iexact=name_var) | 
                Q(name__icontains=name_var)
            ).first()
            if speaker:
                break
        except Exception as e:
            print(f"Error finding speaker {name_var}: {e}")
    
    if speaker:
        print(f"Updating bio for speaker: {speaker.name}")
        speaker.bio = bio
        if title and not speaker.title:
            speaker.title = title
        if institution and not speaker.institution:
            speaker.institution = institution
        speaker.save()
    else:
        print(f"Speaker not found: {name}. Creating new speaker.")
        speaker = Speaker.objects.create(
            name=name,
            bio=bio,
            title=title if title else "",
            institution=institution if institution else ""
        )
    
    return speaker

def parse_time(time_str):
    """Parse time string in format 'HH:MM' or 'H:MM' to time object."""
    try:
        # Try 24-hour format first
        return datetime.strptime(time_str.strip(), "%H:%M").time()
    except ValueError:
        try:
            # Try 12-hour format with AM/PM
            return datetime.strptime(time_str.strip(), "%I:%M %p").time()
        except ValueError:
            # Handle cases where only hours are given (e.g., "9")
            if ":" not in time_str:
                return time(int(time_str.strip()), 0)
            else:
                # Handle other potential formats
                parts = time_str.strip().split(":")
                return time(int(parts[0]), int(parts[1]))

def create_detailed_schedule():
    """Create the detailed conference schedule from the provided information."""
    # Clear existing schedule items but keep the speakers
    print("Clearing existing schedule...")
    Session.objects.all().delete()
    ScheduleItem.objects.all().delete()
    
    # Create session for each day
    day1_date = date(2025, 4, 18)
    day2_date = date(2025, 4, 19)
    
    # Create the registration and opening sessions
    registration_session, _ = Session.objects.get_or_create(
        name="Registration",
        date=day1_date,
        start_time=parse_time("8:30"),
        end_time=parse_time("9:30"),
        description="Registration for the conference"
    )
    
    ScheduleItem.objects.get_or_create(
        session=registration_session,
        title="Registration",
        start_time=parse_time("8:30"),
        end_time=parse_time("9:30"),
        description="Registration and welcome kit collection",
        is_break=True
    )
    
    opening_session, _ = Session.objects.get_or_create(
        name="Opening Ceremony",
        date=day1_date,
        start_time=parse_time("9:30"),
        end_time=parse_time("10:00"),
        description="Official opening of the First KHCC Interventional Oncology Conference"
    )
    
    ScheduleItem.objects.get_or_create(
        session=opening_session,
        title="Opening Ceremony",
        start_time=parse_time("9:30"),
        end_time=parse_time("10:00"),
        description="Welcome speeches and introduction to the conference",
    )
    
    # Day 1 - First Session
    day1_session1, _ = Session.objects.get_or_create(
        name="First Session - Liver Interventions Part 1",
        date=day1_date,
        start_time=parse_time("10:00"),
        end_time=parse_time("12:20"),
        description="Moderators: Dr Hazem Habbub, Khaleel AlQararha, Izz Edden Gotash"
    )
    
    # Session 1 items
    schedule_items = [
        {
            "session": day1_session1,
            "title": "Role of loco-regional ablation therapy in HCC",
            "start_time": "10:00",
            "end_time": "10:20",
            "speaker_name": "Prof. Govindarajan Narayanan",
            "speaker_institution": "USA"
        },
        {
            "session": day1_session1,
            "title": "Radio-embolization application in liver HCC",
            "start_time": "10:20",
            "end_time": "10:40",
            "speaker_name": "Dr. Moh Arabi",
            "speaker_institution": "KSA"
        },
        {
            "session": day1_session1,
            "title": "Deep dive in CRLM tumor ablation / IRE",
            "start_time": "10:40",
            "end_time": "11:00",
            "speaker_name": "Dr. Praveen Peddu",
            "speaker_institution": "UK"
        },
        {
            "session": day1_session1,
            "title": "New update on TARE / TACE in liver CRLM",
            "start_time": "11:00",
            "end_time": "11:20",
            "speaker_name": "Dr Azam Khan Kan",
            "speaker_institution": "KSA"
        },
        {
            "session": day1_session1,
            "title": "Coffee Break",
            "start_time": "11:20",
            "end_time": "11:30",
            "is_break": True
        }
    ]
    
    # Add all items for the session
    add_schedule_items(schedule_items)
    
    # Day 1 - Second Session
    day1_session2, _ = Session.objects.get_or_create(
        name="Second Session - Liver Interventions Part 2",
        date=day1_date,
        start_time=parse_time("11:30"),
        end_time=parse_time("12:30"),
        description="Continuation of discussions on liver interventions"
    )
    
    # Session 2 items
    schedule_items = [
        {
            "session": day1_session2,
            "title": "SIRT vs SBRT in liver tumors",
            "start_time": "11:30",
            "end_time": "11:50",
            "speaker_name": "Dr Moh Arabi",
            "speaker_institution": "KSA"
        },
        {
            "session": day1_session2,
            "title": "SIRT vs TACE",
            "start_time": "11:50",
            "end_time": "12:10",
            "speaker_name": "Dr Amr Elfouly",
            "speaker_institution": "Egypt"
        },
        {
            "session": day1_session2,
            "title": "Application of surgery in liver HCC",
            "start_time": "12:10",
            "end_time": "12:30",
            "speaker_name": "Dr Sameer Smadi",
            "speaker_institution": "Jordan"
        },
        {
            "session": day1_session2,
            "title": "Lunch Break",
            "start_time": "12:30",
            "end_time": "13:30",
            "is_break": True
        }
    ]
    
    # Add all items for the session
    add_schedule_items(schedule_items)
    
    # Day 1 - Third Session
    day1_session3, _ = Session.objects.get_or_create(
        name="Third Session - Advanced Therapies",
        date=day1_date,
        start_time=parse_time("13:30"),
        end_time=parse_time("14:50"),
        description="Moderators: Dr Hassan AlBalas, Mamoon AlOmari, Rim Turfa"
    )
    
    # Session 3 items
    schedule_items = [
        {
            "session": day1_session3,
            "title": "Immunotherapy in the treatment of advance liver HCC (BCLC criteria)",
            "start_time": "13:30",
            "end_time": "13:50",
            "speaker_name": "Dr Yaqob Saleh",
            "speaker_institution": "Jordan"
        },
        {
            "session": day1_session3,
            "title": "Interventional oncology in primary breast cancer treatment and treatment of metastases",
            "start_time": "13:50",
            "end_time": "14:10",
            "speaker_name": "Prof. Vogl",
            "speaker_institution": "Germany"
        },
        {
            "session": day1_session3,
            "title": "ELVD vs ALPPS",
            "start_time": "14:10",
            "end_time": "14:30",
            "speaker_name": "Dr. Praveen Peddu",
            "speaker_institution": "UK"
        },
        {
            "session": day1_session3,
            "title": "IRE with immunotherapy",
            "start_time": "14:30",
            "end_time": "14:50",
            "speaker_name": "Prof. Govindarajan Narayanan",
            "speaker_institution": "USA"
        },
        {
            "session": day1_session3,
            "title": "Coffee Break",
            "start_time": "14:50",
            "end_time": "15:05",
            "is_break": True
        }
    ]
    
    # Add all items for the session
    add_schedule_items(schedule_items)
    
    # Day 1 - Fourth Session
    day1_session4, _ = Session.objects.get_or_create(
        name="Fourth Session - Renal and Prostate Interventions",
        date=day1_date,
        start_time=parse_time("15:05"),
        end_time=parse_time("16:25"),
        description="Moderators: Farid AlAdham, Mohammed Badran, Jezzef Hadad"
    )
    
    # Session 4 items
    schedule_items = [
        {
            "session": day1_session4,
            "title": "Renal Tumor Ablation (Cryo ablation/ RFA/ MWA)",
            "start_time": "15:05",
            "end_time": "15:25",
            "speaker_name": "Dr. Nicos Fotiadis",
            "speaker_institution": "UK"
        },
        {
            "session": day1_session4,
            "title": "RCC Cryoablation vs partial nephrectomy",
            "start_time": "15:25",
            "end_time": "15:45",
            "speaker_name": "Dr. Salem Bauones",
            "speaker_institution": "KSA"
        },
        {
            "session": day1_session4,
            "title": "IRE in prostate cancer",
            "start_time": "15:45",
            "end_time": "16:05",
            "speaker_name": "Prof. Jose",
            "speaker_institution": "Spain",
            "description": "Online presentation"
        },
        {
            "session": day1_session4,
            "title": "Trans-perineal Bx vs TRUS time to change",
            "start_time": "16:05",
            "end_time": "16:25",
            "speaker_name": "Dr. Jafar Bani Essa",
            "speaker_institution": "Jordan"
        }
    ]
    
    # Add all items for the session
    add_schedule_items(schedule_items)
    
    # Day 2 - First Session
    day2_session1, _ = Session.objects.get_or_create(
        name="First Session - Lung Interventions",
        date=day2_date,
        start_time=parse_time("9:00"),
        end_time=parse_time("10:20"),
        description="Moderators: Maher AlKawaldah, Jafar Bani, Jehad Fatafta"
    )
    
    # Day 2 Session 1 items
    schedule_items = [
        {
            "session": day2_session1,
            "title": "Interventional oncology in primary lung cancer treatment and treatment of metastases",
            "start_time": "9:00",
            "end_time": "9:20",
            "speaker_name": "Prof. Vogl",
            "speaker_institution": "Germany"
        },
        {
            "session": day2_session1,
            "title": "Percutaneous lung tumor ablation in metastatic lung tumors",
            "start_time": "9:20",
            "end_time": "9:40",
            "speaker_name": "Dr Farid AlAdham",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session1,
            "title": "Robotic assisted lung tumor ablation tips and tricks",
            "start_time": "9:40",
            "end_time": "10:00",
            "speaker_name": "Dr Nicos Fotiadis",
            "speaker_institution": "UK"
        },
        {
            "session": day2_session1,
            "title": "Central venous DVT thrombolysis in cancer patient",
            "start_time": "10:00",
            "end_time": "10:20",
            "speaker_name": "Dr Hazem Habbub",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session1,
            "title": "Coffee Break",
            "start_time": "10:20",
            "end_time": "10:40",
            "is_break": True
        }
    ]
    
    # Add all items for the session
    add_schedule_items(schedule_items)
    
    # Day 2 - Second Session
    day2_session2, _ = Session.objects.get_or_create(
        name="Second Session - Chemosaturation and Ablation Therapies",
        date=day2_date,
        start_time=parse_time("10:40"),
        end_time=parse_time("13:00"),
        description="Moderators: Khaled Alawnah, Osama Samarah, Samer Jfoot"
    )
    
    # Day 2 Session 2 items
    schedule_items = [
        {
            "session": day2_session2,
            "title": "Chemosaturation and isolated liver therapy",
            "start_time": "10:40",
            "end_time": "11:00",
            "speaker_name": "Dr Arslan",
            "speaker_institution": "Turkey"
        },
        {
            "session": day2_session2,
            "title": "Chemosaturation and isolated liver therapy tips and tricks",
            "start_time": "11:00",
            "end_time": "11:20",
            "speaker_name": "Dr Mahir",
            "speaker_institution": "Turkey"
        },
        {
            "session": day2_session2,
            "title": "HCC combined therapy",
            "start_time": "11:20",
            "end_time": "11:40",
            "speaker_name": "Dr Khaleel",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session2,
            "title": "Role of Cryoablation in the treatment of Desmoids Tumor",
            "start_time": "11:40",
            "end_time": "12:00",
            "speaker_name": "Dr Nicos Fotiadis",
            "speaker_institution": "UK"
        },
        {
            "session": day2_session2,
            "title": "Percutaneous ablation in ABC",
            "start_time": "12:00",
            "end_time": "12:20",
            "speaker_name": "Dr Salem Bauones",
            "speaker_institution": "KSA"
        },
        {
            "session": day2_session2,
            "title": "Spinal tumor ablation",
            "start_time": "12:20",
            "end_time": "12:40",
            "speaker_name": "Dr Roberto Cazzato",
            "speaker_institution": "Online"
        },
        {
            "session": day2_session2,
            "title": "Application of Cryo-ablation in orthopedic surgery",
            "start_time": "12:40",
            "end_time": "13:00",
            "speaker_name": "Dr Ahmed Shehadah",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session2,
            "title": "Lunch Break",
            "start_time": "13:00",
            "end_time": "13:40",
            "is_break": True
        }
    ]
    
    # Add all items for the session
    add_schedule_items(schedule_items)
    
    # Day 2 - Third Session
    day2_session3, _ = Session.objects.get_or_create(
        name="Third Session - Specialized Applications and AI",
        date=day2_date,
        start_time=parse_time("13:40"),
        end_time=parse_time("15:00"),
        description="Moderators: Hazem Habbub, Mamoon AlOmari, Muwafaq Alhees"
    )
    
    # Day 2 Session 3 items
    schedule_items = [
        {
            "session": day2_session3,
            "title": "AI in interventional oncology",
            "start_time": "13:40",
            "end_time": "14:00",
            "speaker_name": "Dr Iyad Sultan",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session3,
            "title": "CNS tumor embolisation",
            "start_time": "14:00",
            "end_time": "14:20",
            "speaker_name": "Dr Maher Khawaldah",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session3,
            "title": "Melphalan in retinoblastoma",
            "start_time": "14:20",
            "end_time": "14:40",
            "speaker_name": "Dr Ghazwan AlTaie",
            "speaker_institution": "Iraq"
        },
        {
            "session": day2_session3,
            "title": "Thyroid ablation in recurrent thyroid cancer",
            "start_time": "14:40",
            "end_time": "15:00",
            "speaker_name": "Dr. Mohammed Badran",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session3,
            "title": "Coffee Break",
            "start_time": "15:00",
            "end_time": "15:15",
            "is_break": True
        }
    ]
    
    # Add all items for the session
    add_schedule_items(schedule_items)
    
    # Day 2 - Fourth Session
    day2_session4, _ = Session.objects.get_or_create(
        name="Fourth Session - Education and Quality in IO",
        date=day2_date,
        start_time=parse_time("15:15"),
        end_time=parse_time("16:15"),
        description="Moderators: Dr. Khaleel, Jafar Bani Essa"
    )
    
    # Day 2 Session 4 items
    schedule_items = [
        {
            "session": day2_session4,
            "title": "Challenging cases in IO (TIPPS/DIPS in HCC)",
            "start_time": "15:15",
            "end_time": "15:35",
            "speaker_name": "Prof. Mamoon Alomari",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session4,
            "title": "Education and training in IO",
            "start_time": "15:35",
            "end_time": "15:55",
            "speaker_name": "Dr Azam Khan Kan",
            "speaker_institution": "Jordan"
        },
        {
            "session": day2_session4,
            "title": "Quality management in IO",
            "start_time": "15:55",
            "end_time": "16:15",
            "speaker_name": "Saad Abu Alkanam",
            "speaker_institution": "KSA"
        }
    ]
    
    # Add all items for the session
    add_schedule_items(schedule_items)
    
    # Closing ceremony
    closing_session, _ = Session.objects.get_or_create(
        name="Closing Ceremony",
        date=day2_date,
        start_time=parse_time("16:15"),
        end_time=parse_time("16:45"),
        description="Closing remarks and certificate distribution"
    )
    
    ScheduleItem.objects.get_or_create(
        session=closing_session,
        title="Closing Ceremony",
        start_time=parse_time("16:15"),
        end_time=parse_time("16:45"),
        description="Concluding remarks and certificate distribution"
    )
    
    print("Schedule updated successfully!")

def add_schedule_items(items):
    """Add schedule items and link to speakers."""
    for item in items:
        # Extract data
        session = item["session"]
        title = item["title"]
        start_time = parse_time(item["start_time"])
        end_time = parse_time(item["end_time"])
        is_break = item.get("is_break", False)
        description = item.get("description", "")
        
        # Create schedule item
        schedule_item, created = ScheduleItem.objects.get_or_create(
            session=session,
            title=title,
            start_time=start_time,
            end_time=end_time,
            is_break=is_break,
            description=description
        )
        
        # Link to speaker if not a break
        if not is_break and "speaker_name" in item:
            speaker_name = item["speaker_name"]
            speaker_institution = item.get("speaker_institution", "")
            
            # Find or create speaker
            speaker = None
            try:
                # Look for exact or partial matches
                speaker = Speaker.objects.filter(
                    Q(name__iexact=speaker_name) | 
                    Q(name__icontains=speaker_name)
                ).first()
                
                if not speaker and " " in speaker_name:
                    # Try with just the last name
                    last_name = speaker_name.split()[-1]
                    speaker = Speaker.objects.filter(
                        Q(name__icontains=last_name)
                    ).first()
                
                if not speaker:
                    # Create a new speaker if not found
                    speaker = Speaker.objects.create(
                        name=speaker_name,
                        institution=speaker_institution,
                        bio=f"Speaker at the First KHCC Interventional Oncology Conference 2025."
                    )
                    print(f"Created new speaker: {speaker_name}")
                else:
                    # Update institution if it's not set
                    if speaker_institution and not speaker.institution:
                        speaker.institution = speaker_institution
                        speaker.save()
                    print(f"Using existing speaker: {speaker.name}")
                
                # Link the speaker to the schedule item
                schedule_item.speakers.add(speaker)
                
            except Exception as e:
                print(f"Error processing speaker {speaker_name}: {e}")

def update_arslan_bio():
    """Update Dr. Cagatay Arslan's bio with the provided text."""
    bio = """Dr Cagatay Arslan was born in 1977 in Turkey. He is married with two children. He has taken M.D. degree at Ankara University Faculty of Medicine in Ankara, Turkey. He completed internal medicine recidency in Suleyman Demirel University Faculty of Medicine in Isparta, Turkey. He finished medical oncology fellowship in Hacettepe University, Oncology Institute, Ankara, Turkey. He works as a medical oncology consultant in Izmir MedicalPoint Hospital in Turkey and he is a faculty member as a full professor in Izmir Unversity of Economics Faculty of Medicine in Izmir, Turkey. He has more than 100 scientific publications. He attended more than 150 clinical trials as principal investigator in the field of oncology. He is a full member of European Society of Medical Oncology and Turkish Society of Medical Oncology. His main interrest is on genitourinary cancers, main solid tumors and liver targeted treatments."""
    
    # Search for variations of the name
    name_variations = ["Cagatay Arslan", "Dr Arslan", "Dr. Arslan", "Arslan", "CAGATAY ARSLAN", "CAGATAY ARSALAN"]
    
    # Try to update the speaker's bio
    updated = False
    for name in name_variations:
        speaker = update_speaker_bio(name, bio, "Professor", "Izmir University of Economics, Turkey")
        if speaker:
            updated = True
            break
    
    if updated:
        print("Successfully updated Dr. Cagatay Arslan's bio")
    else:
        print("Could not find Dr. Cagatay Arslan in the database")

if __name__ == "__main__":
    print("Updating Dr. Cagatay Arslan's bio...")
    update_arslan_bio()
    
    print("\nUpdating conference schedule...")
    create_detailed_schedule()
    
    print("\nDone!") 