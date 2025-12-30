# utils/time_formatter.py 
from datetime import datetime, timezone, timedelta

def get_time_ago(timestamp):
    """
    Simple time ago function.
    
    Args:
        timestamp: datetime object
    
    Returns:
        String like "2 minutes ago", "3 hours ago", etc.
    """
    if timestamp is None:
        return "never"
    
    # Ensure timestamp has timezone info
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - timestamp
    
    # Handle negative time (future)
    if diff.total_seconds() < 0:
        return "just now"
    
    # Convert to appropriate unit
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 120:
        return "1 minute ago"
    elif seconds < 3600:  # Less than 1 hour
        minutes = int(seconds / 60)
        return f"{minutes} minutes ago"
    elif seconds < 7200:  # Less than 2 hours
        return "1 hour ago"
    elif seconds < 86400:  # Less than 1 day
        hours = int(seconds / 3600)
        return f"{hours} hours ago"
    elif seconds < 172800:  # Less than 2 days
        return "yesterday"
    elif seconds < 604800:  # Less than 1 week
        days = int(seconds / 86400)
        return f"{days} days ago"
    elif seconds < 1209600:  # Less than 2 weeks
        return "1 week ago"
    elif seconds < 2592000:  # Less than 30 days
        weeks = int(seconds / 604800)
        return f"{weeks} weeks ago"
    elif seconds < 5184000:  # Less than 60 days
        return "1 month ago"
    elif seconds < 31536000:  # Less than 1 year
        months = int(seconds / 2592000)
        return f"{months} months ago"
    elif seconds < 63072000:  # Less than 2 years
        return "1 year ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} years ago"


