from app import app, db, Attendance

# Check if the Attendance table exists
def check_database():
    with app.app_context():  # Ensure that we have an app context
        try:
            records = Attendance.query.all()
            if records:
                print("Attendance Records Found:")
                for record in records:
                    print(f"ID: {record.id}, Name: {record.name}, Entry Time: {record.entry_time}, Exit Time: {record.exit_time}")
            else:
                print("No records found in the database.")
        except Exception as e:
            print(f"Error checking the database: {e}")

# Run the check
if __name__ == '__main__':
    check_database()
