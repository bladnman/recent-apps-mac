import subprocess
import sqlite3
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
import plistlib

# SEEMS LIKE THE LAUNCH SERVICES DATABASE IS NOT AVAILABLE IN BIG SUR
def get_installed_applications():
    # Use system_profiler to get a plist of installed applications
    result = subprocess.run(['system_profiler', 'SPApplicationsDataType', '-xml'], capture_output=True, text=True)
    plist_data = plistlib.loads(result.stdout.encode())

    # Parse the plist data
    applications = []
    for item in plist_data[0]['_items']:
        # Retrieve application name
        app_name = item.get('_name', 'Unknown')

        # Retrieve application path
        app_path = item.get('path', None)

        # Attempt to get the last used date using mdls if the path is available
        if app_path:
            try:
                # Use mdls to get the last used date
                mdls_result = subprocess.run(['mdls', '-name', 'kMDItemLastUsedDate', app_path], capture_output=True, text=True)
                last_used_str = mdls_result.stdout.strip().split('=')[-1].strip()

                if last_used_str == "(null)" or not last_used_str:
                    last_used_str = "Never Opened"
                else:
                    # Parse the date string into a readable format
                    # Remove quotes from the string
                    last_used_str = last_used_str.replace('"', '').strip()
                    last_used_date = datetime.strptime(last_used_str, '%Y-%m-%d %H:%M:%S %z')
                    last_used_str = last_used_date.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                last_used_str = f"Error: {e}"
        else:
            last_used_str = "Path Not Available"

        applications.append({
            'name': app_name,
            'last_used': last_used_str
        })

    return applications

def get_installed_applications_from_db():
    # Path to the LaunchServices database
    db_path = os.path.expanduser(
        '~/Library/Application Support/com.apple.LaunchServices/com.apple.launchservices.secure.plist')

    # Check if the database exists
    if not os.path.exists(db_path):
        print("LaunchServices database not found at:", db_path)
        return []

    # Use sqlite3 to query the database for application names and last used dates
    applications = []
    try:
        # Connect to the LaunchServices database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query for applications
        cursor.execute('SELECT name, lastused FROM LSApplicationData WHERE lastused IS NOT NULL')

        # Fetch and process results
        for row in cursor.fetchall():
            app_name = row[0]
            last_used = row[1]
            if last_used:
                last_used_date = datetime.fromtimestamp(last_used)
                last_used_str = last_used_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_used_str = 'Never Opened'

            applications.append({
                'name': app_name,
                'last_used': last_used_str
            })
    except Exception as e:
        print("Error querying LaunchServices database:", e)
    finally:
        if conn:
            conn.close()

    return applications


def display_applications(applications):
    console = Console()
    table = Table(title="Installed Applications and Last Used Dates")

    table.add_column("Application Name", style="cyan", no_wrap=True)
    table.add_column("Last Used Date", style="magenta")

    # Sort applications by last used date (most recent first)
    applications.sort(key=lambda app: (app['last_used'] is not None, app['last_used']), reverse=True)

    for app in applications:
        table.add_row(app['name'], app['last_used'])

    console.print(table)


if __name__ == "__main__":

    # seems to not work in Big Sur
    # apps = get_installed_applications_from_db()

    apps = get_installed_applications()

    display_applications(apps)