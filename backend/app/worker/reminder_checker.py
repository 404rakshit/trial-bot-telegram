"""Background Reminder Checker

Runs in a separate thread to periodically check reminders and send alerts.
"""
import time
from threading import Thread
from datetime import datetime
from typing import List

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.reminder import Reminder
from app.models.user import User
from app.services.weather import fetch_weather_forecast, check_condition_in_forecast, get_weather_description
from app.services.telegram_sender import send_weather_alert


def check_reminders():
    """Main loop: Check all active reminders and send notifications

    Runs continuously in a background thread, checking every 15 minutes.
    """
    print("🔄 Background reminder checker started")

    while True:
        try:
            check_start = datetime.utcnow()
            print(f"\n⏰ Checking reminders at {check_start.isoformat()}")

            db = SessionLocal()

            try:
                # Get all active reminders with their users
                reminders = (
                    db.query(Reminder)
                    .join(User)
                    .filter(Reminder.is_active == True)
                    .all()
                )

                print(f"📋 Found {len(reminders)} active reminders to check")

                for reminder in reminders:
                    try:
                        process_reminder(db, reminder)
                    except Exception as e:
                        print(f"❌ Error processing reminder {reminder.id}: {e}")
                        continue

            finally:
                db.close()

            check_duration = (datetime.utcnow() - check_start).total_seconds()
            print(f"✅ Reminder check completed in {check_duration:.2f}s")

        except Exception as e:
            print(f"❌ Error in reminder checker loop: {e}")

        # Sleep for the configured interval
        print(f"💤 Sleeping for {settings.WEATHER_CHECK_INTERVAL} seconds...")
        time.sleep(settings.WEATHER_CHECK_INTERVAL)


def process_reminder(db, reminder: Reminder):
    """Process a single reminder and send alert if conditions match

    Args:
        db: Database session
        reminder: Reminder object to process
    """
    user = reminder.user

    print(f"🔍 Checking reminder #{reminder.id} for user {user.chat_id}")
    print(f"   Condition: {reminder.condition}, Hours ahead: {reminder.hours_ahead}")

    # Fetch weather forecast for user's location
    forecast_data = fetch_weather_forecast(user.latitude, user.longitude)

    if not forecast_data:
        print(f"⚠️  Could not fetch weather for reminder #{reminder.id}")
        return

    # Check if the condition will occur
    condition_matches = check_condition_in_forecast(
        forecast_data,
        reminder.condition,
        reminder.hours_ahead
    )

    if condition_matches:
        # Check if we recently sent an alert (avoid spam)
        if should_send_alert(reminder):
            weather_desc = get_weather_description(forecast_data, reminder.hours_ahead)

            print(f"🚨 ALERT: Sending notification for reminder #{reminder.id}")

            success = send_weather_alert(
                chat_id=user.chat_id,
                condition=reminder.condition,
                hours_ahead=reminder.hours_ahead,
                weather_description=weather_desc,
                custom_message=reminder.custom_message
            )

            if success:
                # Update last alerted timestamp
                reminder.last_alerted_at = datetime.utcnow()
                db.commit()
                print(f"✅ Alert sent and recorded for reminder #{reminder.id}")
        else:
            print(f"⏭️  Alert already sent recently for reminder #{reminder.id}")
    else:
        print(f"ℹ️  Condition not met for reminder #{reminder.id}")

    # Update last checked timestamp
    reminder.last_checked_at = datetime.utcnow()
    db.commit()


def should_send_alert(reminder: Reminder) -> bool:
    """Check if we should send an alert for this reminder

    Prevents spam by not sending alerts more than once per 6 hours.

    Args:
        reminder: Reminder object

    Returns:
        True if we should send alert, False if we sent one recently
    """
    if not reminder.last_alerted_at:
        return True

    # Don't send alert if we sent one less than 6 hours ago
    time_since_last_alert = (datetime.utcnow() - reminder.last_alerted_at).total_seconds()
    min_interval = 6 * 3600  # 6 hours in seconds

    return time_since_last_alert >= min_interval


def start_background_checker():
    """Start the background reminder checker thread"""
    thread = Thread(target=check_reminders, daemon=True, name="ReminderChecker")
    thread.start()
    print("✅ Background reminder checker thread started")
