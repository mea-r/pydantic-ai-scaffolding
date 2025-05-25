import os
from datetime import datetime
from typing import Dict, Any

import requests
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

load_dotenv()

def tool_get_human_date() -> str:
    dt = datetime.now()

    # Get ordinal suffix
    day = dt.day
    suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    # Determine time of day
    hour = dt.hour
    if 5 <= hour < 12:
        time_of_day = "morning"
    elif 12 <= hour < 17:
        time_of_day = "afternoon"
    elif 17 <= hour < 21:
        time_of_day = "evening"
    else:
        time_of_day = "night"

    # Check if today
    today = datetime.now().date()
    if dt.date() == today:
        day_prefix = "Today"
    else:
        day_prefix = dt.strftime("%A")

    return f"{day_prefix} on {day}{suffix} of {dt.strftime('%B')}, {dt.strftime('%A')} {time_of_day}"
