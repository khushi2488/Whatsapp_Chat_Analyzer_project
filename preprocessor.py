import re
import pandas as pd

def preprocess(data):
    # Updated regex pattern to capture the datetime with AM/PM and the delimiter " - "
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s*(?:AM|PM)\s-\s'
    
    # Split the data using the updated pattern and ignore the first empty split
    messages = re.split(pattern, data)[1:]
    
    # Find all occurrences of the date-time pattern
    dates = re.findall(pattern, data)
    
    # Create a DataFrame with the extracted messages and dates
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    # Remove the trailing " - " and any extra whitespace from the extracted date strings.
    df['message_date'] = df['message_date'].apply(lambda x: x.replace(" - ", "").strip())
    
    # Convert 'message_date' column to datetime using the format: month/day/two-digit-year, 12-hour time with AM/PM.
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p')
    df.rename(columns={'message_date': 'date'}, inplace=True)
    
    users = []
    messages_list = []
    
    # Process each message to separate the user and the actual message
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if len(entry) > 1:
            users.append(entry[1])
            messages_list.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages_list.append(entry[0])
    
    df['user'] = users
    df['message'] = messages_list
    df.drop(columns=['user_message'], inplace=True)
    
    # ------------------------------
    # New: Extract additional time features for analysis
    # ------------------------------
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['only_date'] = df['date'].dt.date
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    
    # Create a 'period' column for hourly analysis (e.g., "23-0", "0-1", etc.)
    def get_period(hour):
        if hour == 23:
            return "23-0"
        else:
            return f"{hour}-{hour+1}"
    
    df['period'] = df['hour'].apply(get_period)
    
    return df
