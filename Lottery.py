import time
import random
import threading
import json
import os
from datetime import datetime, timedelta

REGISTRATION_DURATION = 60 * 60  # 1 hour in seconds
EXTENSION_DURATION = 30 * 60     # 30 minutes in seconds
SAVE_INTERVAL = 300              # Save every 5 minutes

participants = set()
start_time = time.time()
log_file = "lottery_log.txt"
backup_file = "lottery_backup.json"
lock = threading.Lock()

def save_progress():
    while time.time() - start_time < REGISTRATION_DURATION + EXTENSION_DURATION:
        time.sleep(SAVE_INTERVAL)
        with lock:
            with open(backup_file, "w") as f:
                json.dump(list(participants), f)

def load_backup():
    if os.path.exists(backup_file):
        with open(backup_file, "r") as f:
            return set(json.load(f))
    return set()

def log_event(message):
    with open(log_file, "a") as log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"[{timestamp}] {message}\n")

def display_remaining_time():
    while True:
        time_left = int((start_time + REGISTRATION_DURATION) - time.time())
        if time_left <= 0:
            break
        if time_left % 600 == 0:  # Every 10 minutes
            print(f">>> Time remaining: {time_left // 60} minutes")
        time.sleep(60)

def register_users():
    global participants
    participants = load_backup()
    while True:
        elapsed = time.time() - start_time
        if elapsed > REGISTRATION_DURATION:
            break
        username = input("Enter username to register: ").strip()
        if not username or not username.isalnum():
            print("Invalid username. Use alphanumeric characters only.")
            continue
        if username in participants:
            print("Username already registered.")
        else:
            participants.add(username)
            print(f"Registered: {username} | Total: {len(participants)}")
            log_event(f"Registered: {username}")

def extend_registration():
    global REGISTRATION_DURATION
    print("Extending registration by 30 minutes due to low participation...")
    REGISTRATION_DURATION += EXTENSION_DURATION
    time.sleep(EXTENSION_DURATION)

def announce_winner():
    if len(participants) == 0:
        print("No users registered. Exiting.")
        log_event("No users registered. No winner.")
        return
    winner = random.choice(list(participants))
    print("\n=== LOTTERY WINNER ANNOUNCEMENT ===")
    print(f"Total Participants: {len(participants)}")
    print(f"Congratulations! The winner is: {winner}")
    print("===================================")
    log_event(f"Total Participants: {len(participants)}")
    log_event(f"Winner: {winner}")

def main():
    print("=== Terminal Lottery System Started ===")
    print("Users can register for the next 1 hour.")
    log_event("Lottery registration started.")

    timer_thread = threading.Thread(target=display_remaining_time)
    save_thread = threading.Thread(target=save_progress)

    timer_thread.start()
    save_thread.start()

    register_users()

    if len(participants) < 5:
        extend_registration()
        register_users()

    announce_winner()

if __name__ == "__main__":
    main()
