import sqlite3

# Connect to your database
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# Get a list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f" - {table[0]}")

# Read posts
print("\nPosts:")
cursor.execute("SELECT id, title, subtitle, author, date_posted FROM Post")
for row in cursor.fetchall():
    print(row)

# Read contact messages
print("\nContact Messages:")
cursor.execute("SELECT id, name, email, subject, date_sent FROM ContactMessage")
for row in cursor.fetchall():
    print(row)

# Close connection
conn.close()
