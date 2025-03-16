#!/usr/bin/env python
"""
Script to process speaker data from provided files and load them into the database.
This script extracts speaker information from the website_material directory.
It uses OpenAI's GPT-4o to help parse files that are difficult to read directly.
"""

import os
import django
import re
import json
import base64
from pathlib import Path
import shutil
from datetime import datetime, time
import dotenv
from typing import Dict, List, Optional, Tuple, Any
import requests
import mimetypes

# Load environment variables from .env file
dotenv.load_dotenv()

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khcc_conference.settings')
django.setup()

from conference.models import Speaker, Session, ScheduleItem  # noqa: E402

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"  # Using gpt-4o-mini as specified in requirements
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def extract_name_from_filename(filename: str) -> str:
    """Extract name from filename removing common prefixes and suffixes."""
    name = os.path.splitext(os.path.basename(filename))[0]
    
    # Remove common prefixes and suffixes
    name = re.sub(r'^(Dr\.?\s+|Dr\s+|CV\s+|\d+\s+)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'(_CV|CV|photo|Picture|\d+).*$', '', name, flags=re.IGNORECASE)
    name = name.replace('_', ' ').strip()
    
    return name

def encode_file_to_base64(file_path: str) -> Optional[str]:
    """
    Encode a file to base64 for sending to OpenAI API.
    Returns None if file cannot be read.
    """
    try:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding file {file_path}: {str(e)}")
        return None

def get_file_content_type(file_path: str) -> str:
    """
    Get the content type of a file.
    """
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        # Default to octet-stream if type can't be determined
        content_type = "application/octet-stream"
    return content_type

def extract_info_from_file_with_gpt(file_path: str, name: str, file_type: str) -> Dict[str, str]:
    """
    Use OpenAI's GPT-4o model to extract information from a file.
    
    Args:
        file_path: Path to the file
        name: Name of the speaker
        file_type: Type of file (bio, cv, photo)
    
    Returns:
        Dictionary containing extracted information
    """
    if not OPENAI_API_KEY:
        print("⚠️ OPENAI_API_KEY not found in environment variables. Skipping GPT extraction.")
        return {"title": "", "institution": "", "bio": ""}
    
    # Skip processing for images
    if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.jfif')):
        return {"title": "", "institution": "", "bio": ""}
    
    file_base64 = encode_file_to_base64(file_path)
    if not file_base64:
        return {"title": "", "institution": "", "bio": ""}
    
    content_type = get_file_content_type(file_path)
    
    # Prepare system prompt based on file type
    if file_type == "bio":
        system_prompt = (
            f"You are an assistant that extracts speaker information from files. "
            f"Extract a professional biography for {name}. "
            f"Also identify their title and institution if available. "
            f"Return the information in JSON format with keys: 'title', 'institution', and 'bio'."
        )
    elif file_type == "cv":
        system_prompt = (
            f"You are an assistant that extracts speaker information from CVs. "
            f"For {name}, extract their current professional title and institution. "
            f"Also create a concise professional biography (200-300 words) from the CV. "
            f"Return the information in JSON format with keys: 'title', 'institution', and 'bio'."
        )
    else:
        system_prompt = (
            f"You are an assistant that extracts speaker information from files. "
            f"Extract any relevant information about {name}, including title, institution, "
            f"and biographical information. "
            f"Return the information in JSON format with keys: 'title', 'institution', and 'bio'."
        )
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Please extract information about {name} from this file:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{content_type};base64,{file_base64}"
                        }
                    }
                ]}
            ],
            "response_format": {"type": "json_object"}
        }
        
        print(f"Sending {file_path} to GPT-4o for analysis...")
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"Error from OpenAI API: {response.text}")
            return {"title": "", "institution": "", "bio": ""}
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parse the JSON response
        try:
            info = json.loads(content)
            # Ensure all expected keys are present
            info.setdefault("title", "")
            info.setdefault("institution", "")
            info.setdefault("bio", "")
            return info
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response from OpenAI API. Raw response: {content}")
            # Try to extract information with regex if JSON parsing fails
            title_match = re.search(r'"title"\s*:\s*"([^"]*)"', content)
            institution_match = re.search(r'"institution"\s*:\s*"([^"]*)"', content)
            bio_match = re.search(r'"bio"\s*:\s*"([^"]*)"', content)
            
            return {
                "title": title_match.group(1) if title_match else "",
                "institution": institution_match.group(1) if institution_match else "",
                "bio": bio_match.group(1) if bio_match else ""
            }
            
    except Exception as e:
        print(f"Error using OpenAI API: {str(e)}")
        return {"title": "", "institution": "", "bio": ""}

def process_speaker_files():
    """Process speaker files from the website_material directory."""
    material_dir = 'website_material'
    
    # Ensure media directory exists
    media_speakers_dir = os.path.join('media', 'speakers')
    os.makedirs(media_speakers_dir, exist_ok=True)
    
    # Keep track of known speaker names
    speaker_names = {}
    
    # First pass - identify unique speakers
    for filename in os.listdir(material_dir):
        filepath = os.path.join(material_dir, filename)
        
        if not os.path.isfile(filepath):
            continue
        
        # Extract name from filename
        name = extract_name_from_filename(filename)
        
        # Skip files that don't seem to be related to speakers
        if name.lower() in ('logo', 'interventional oncology conference agenda'):
            continue
        
        if name not in speaker_names:
            speaker_names[name] = {
                'bio_file': None,
                'photo_file': None,
                'cv_file': None,
                'bio_text': '',
                'title': '',
                'institution': ''
            }
        
        # Identify file type
        lower_filename = filename.lower()
        if 'photo' in lower_filename or lower_filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.jfif')):
            speaker_names[name]['photo_file'] = filepath
        elif 'cv' in lower_filename or 'curriculum' in lower_filename:
            speaker_names[name]['cv_file'] = filepath
        elif 'bio' in lower_filename or 'biography' in lower_filename:
            speaker_names[name]['bio_file'] = filepath
    
    # Second pass - process files with GPT-4o and extract information
    for name, data in speaker_names.items():
        print(f"\nProcessing speaker: {name}")
        
        # Initialize combined information
        combined_info = {
            "title": "",
            "institution": "",
            "bio": ""
        }
        
        # Process bio file if available
        if data['bio_file']:
            print(f"Processing bio file: {data['bio_file']}")
            bio_info = extract_info_from_file_with_gpt(data['bio_file'], name, "bio")
            combined_info["title"] = bio_info["title"] or combined_info["title"]
            combined_info["institution"] = bio_info["institution"] or combined_info["institution"]
            combined_info["bio"] = bio_info["bio"] or combined_info["bio"]
        
        # Process CV file if available and info is still missing
        if data['cv_file'] and (not combined_info["title"] or not combined_info["institution"] or not combined_info["bio"]):
            print(f"Processing CV file: {data['cv_file']}")
            cv_info = extract_info_from_file_with_gpt(data['cv_file'], name, "cv")
            combined_info["title"] = combined_info["title"] or cv_info["title"]
            combined_info["institution"] = combined_info["institution"] or cv_info["institution"]
            combined_info["bio"] = combined_info["bio"] or cv_info["bio"]
        
        # Update the speaker data
        speaker_names[name]['title'] = combined_info["title"]
        speaker_names[name]['institution'] = combined_info["institution"]
        speaker_names[name]['bio_text'] = combined_info["bio"]
        
        # If no bio was extracted, create a generic one
        if not speaker_names[name]['bio_text']:
            speaker_names[name]['bio_text'] = (
                f"Distinguished speaker {name} will be presenting at the First KHCC "
                f"Interventional Oncology Conference 2025."
            )
    
    # Third pass - create or update speakers in the database
    for order, (name, data) in enumerate(speaker_names.items()):
        print(f"Creating/updating database entry for: {name}")
        
        # Create or get speaker
        speaker, created = Speaker.objects.get_or_create(name=name)
        
        # Set ordering
        speaker.order = order
        
        # Set title and institution if available
        if data['title']:
            speaker.title = data['title']
        
        if data['institution']:
            speaker.institution = data['institution']
        
        # Set bio
        speaker.bio = data['bio_text']
        
        # If we have a photo, copy it to media directory
        if data['photo_file']:
            photo_ext = os.path.splitext(data['photo_file'])[1]
            photo_filename = f"{name.replace(' ', '_')}{photo_ext}"
            photo_path = os.path.join(media_speakers_dir, photo_filename)
            
            try:
                shutil.copy2(data['photo_file'], photo_path)
                # Set relative path from MEDIA_ROOT
                speaker.photo = os.path.join('speakers', photo_filename)
                print(f"Copied photo for {name}")
            except Exception as e:
                print(f"Error copying photo for {name}: {e}")
        
        # Save speaker
        speaker.save()
        print(f"{'Created' if created else 'Updated'} speaker: {name}")
    
    print(f"\nProcessed {len(speaker_names)} speakers")
    return speaker_names

def create_sample_schedule():
    """Create a sample conference schedule."""
    # Create sessions for the two conference days
    day1_date = datetime(2025, 4, 18).date()
    day2_date = datetime(2025, 4, 19).date()
    
    # Day 1 sessions
    morning_session, created = Session.objects.get_or_create(
        name="Morning Session - Innovations in Interventional Oncology",
        date=day1_date,
        start_time=time(8, 0),
        end_time=time(12, 30),
        description="The opening session focuses on groundbreaking technologies and approaches in interventional oncology."
    )
    
    afternoon_session, created = Session.objects.get_or_create(
        name="Afternoon Session - Liver Cancer Treatments",
        date=day1_date,
        start_time=time(13, 30),
        end_time=time(17, 0),
        description="This session explores the latest advancements in minimally invasive treatments for liver cancer."
    )
    
    # Day 2 sessions
    day2_morning, created = Session.objects.get_or_create(
        name="Morning Session - Lung & Kidney Cancer Interventions",
        date=day2_date,
        start_time=time(8, 30),
        end_time=time(12, 0),
        description="Focusing on precision treatments for lung and kidney tumors using cutting-edge techniques."
    )
    
    day2_afternoon, created = Session.objects.get_or_create(
        name="Afternoon Session - Future Directions & Panel Discussion",
        date=day2_date,
        start_time=time(13, 0),
        end_time=time(16, 30),
        description="A forward-looking session examining emerging technologies and concluding with an expert panel discussion."
    )
    
    # Get speakers to assign to schedule items
    speakers = list(Speaker.objects.all())
    speaker_count = len(speakers)
    
    if speaker_count > 0:
        # Day 1 - Morning schedule items
        ScheduleItem.objects.get_or_create(
            session=morning_session,
            title="Welcome Address",
            start_time=time(8, 0),
            end_time=time(8, 30),
            description="Opening remarks and welcome to the First KHCC Interventional Oncology Conference."
        )
        
        keynote = ScheduleItem.objects.get_or_create(
            session=morning_session,
            title="Keynote: The Future of Interventional Oncology",
            start_time=time(8, 30),
            end_time=time(9, 15),
            description="An inspiring look at how interventional oncology is transforming cancer treatment globally."
        )[0]
        
        if speaker_count > 0:
            keynote.speakers.add(speakers[0])
        
        ScheduleItem.objects.get_or_create(
            session=morning_session,
            title="Coffee Break",
            start_time=time(9, 15),
            end_time=time(9, 45),
            is_break=True
        )
        
        tech_presentation = ScheduleItem.objects.get_or_create(
            session=morning_session,
            title="New Technology Presentation",
            start_time=time(9, 45),
            end_time=time(10, 30),
            description="Unveiling of a groundbreaking new technology in interventional oncology."
        )[0]
        
        if speaker_count > 1:
            tech_presentation.speakers.add(speakers[1])
        
        case_studies = ScheduleItem.objects.get_or_create(
            session=morning_session,
            title="Clinical Case Studies",
            start_time=time(10, 30),
            end_time=time(11, 30),
            description="Presentation of challenging cases and innovative treatment approaches."
        )[0]
        
        if speaker_count > 2:
            case_studies.speakers.add(speakers[2])
        
        panel_discussion = ScheduleItem.objects.get_or_create(
            session=morning_session,
            title="Panel Discussion: Implementing New Technologies",
            start_time=time(11, 30),
            end_time=time(12, 30),
            description="Expert panel discussing practical aspects of adopting new interventional techniques."
        )[0]
        
        # Add multiple speakers to panel
        for i in range(min(3, speaker_count)):
            panel_discussion.speakers.add(speakers[i])
        
        # Add more items for afternoon session
        liver_techniques = ScheduleItem.objects.get_or_create(
            session=afternoon_session,
            title="Advanced Liver Ablation Techniques",
            start_time=time(13, 30),
            end_time=time(14, 15),
            description="An overview of cutting-edge ablation techniques for liver tumors."
        )[0]
        
        if speaker_count > 3:
            liver_techniques.speakers.add(speakers[3])
        
        # Add Day 2 items
        if speaker_count > 4:
            lung_session = ScheduleItem.objects.get_or_create(
                session=day2_morning,
                title="Precision Approaches to Lung Tumors",
                start_time=time(8, 30),
                end_time=time(9, 15),
                description="New developments in minimally invasive treatments for lung cancer."
            )[0]
            lung_session.speakers.add(speakers[4])
        
        print("Created sample conference schedule")
    else:
        print("No speakers available to create schedule items")

if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("⚠️ Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=your_api_key_here")
        print("\nContinuing without GPT assistance (limited functionality)...\n")
    
    print("Processing speaker data...")
    process_speaker_files()
    
    print("\nCreating sample conference schedule...")
    create_sample_schedule()
    
    print("\nDone!") 