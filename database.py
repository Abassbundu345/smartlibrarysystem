# database.py
# FULLY WORKING DATABASE LAYER – Supports Librarian + Member Login + Real Loans
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, timedelta

# ────────────────────── DATABASE CONNECTION ──────────────────────
try:
    conn = psycopg2.connect(
        dbname="smartlibrary",
        user="postgres",           # Change if you use another user
        password="077739689",   # ← CHANGE THIS TO YOUR POSTGRES PASSWORD
        host="localhost",
        port="5432",
        cursor_factory=RealDictCursor
    )
    cur = conn.cursor()
    DB_CONNECTED = True
    print("PostgreSQL connected successfully!")
except Exception as e:
    print("Database not available → Running in DEMO MODE")
    DB_CONNECTED = False

# ────────────────────── IN-MEMORY DEMO DATA (if no DB) ──────────────────────
if not DB_CONNECTED:
    books = [
        {"book_id":1,"title":"1984","author_name":"George Orwell","isbn":"123","genre":"Dystopia","published_year":1949,"copies_available":5},
        {"book_id":2,"title":"Harry Potter","author_name":"J.K. Rowling","isbn":"456","genre":"Fantasy","published_year":1997,"copies_available":3},
        {"book_id":3,"title":"The Alchemist","author_name":"Paulo Coelho","isbn":"789","genre":"Fiction","published_year":1988,"copies_available":4}
    ]
    members = [
        {"member_id":1, "full_name":"John Doe", "email":"john@example.com"},
        {"member_id":2, "full_name":"Jane Smith", "email":"jane@example.com"}
    ]
    loans = []
    clubs = [{"club_id":1, "name":"Sci-Fi Lovers", "member_count":12}]

# ────────────────────── HELPER FUNCTIONS ──────────────────────
def execute(query, params=None, fetch=False, commit=False):
    if not DB_CONNECTED:
        return []
    try:
        cur.execute(query, params or ())
        if commit:
            conn.commit()
        return cur.fetchall() if fetch else None
    except Exception as e:
        conn.rollback()
        print("DB Error:", e)
        return []

# ────────────────────── LOGIN FUNCTION (Librarian + Member) ──────────────────────
def authenticate_user(username, password):
    """
    Returns user dict with role and member_id (for members)
    """
    if not DB_CONNECTED:
        # Demo login
        if username == "admin@limkokwing.edu" and password == "admin123":
            return {"username": username, "role": "Librarian"}
        if username == "john@example.com" and password == "123":
            return {"username": username, "role": "Member", "member_id": 1}
        if username == "jane@example.com" and password == "123":
            return {"username": username, "role": "Member", "member_id": 2}
        return None

    # Real DB login
    query = """
        SELECT u.username, u.role, m.member_id 
        FROM users u
        LEFT JOIN members m ON u.username = m.email
        WHERE u.username = %s AND u.password = %s
    """
    result = execute(query, (username, password), fetch=True)
    return dict(result[0]) if result else None

# ────────────────────── BOOK FUNCTIONS ──────────────────────
def get_all_books(search=""):
    if not DB_CONNECTED:
        if search:
            search = search.lower()
            return [b for b in books if search in b["title"].lower() or search in b["author_name"].lower()]
        return books[:]

    query = """
        SELECT b.book_id, b.title, a.name AS author_name, b.isbn, b.genre, 
               b.published_year, b.copies_available
        FROM books b
        LEFT JOIN authors a ON b.author_id = a.author_id
        WHERE b.title ILIKE %s OR a.name ILIKE %s
    """
    search_term = f"%{search}%"
    return execute(query, (search_term, search_term), fetch=True)

def add_book(title, author_name, isbn="", genre="", year=2025, copies=1):
    if not DB_CONNECTED:
        new_id = len(books) + 1
        books.append({
            "book_id": new_id, "title": title, "author_name": author_name,
            "isbn": isbn, "genre": genre, "published_year": year, "copies_available": copies
        })
        return

    # Real DB: Insert author if not exists
    cur.execute("INSERT INTO authors (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (author_name,))
    cur.execute("SELECT author_id FROM authors WHERE name = %s", (author_name,))
    author_id = cur.fetchone()["author_id"]

    cur.execute("""
        INSERT INTO books (title, author_id, isbn, genre, published_year, copies_available)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (title, author_id, isbn or None, genre, year, copies))
    conn.commit()

# ────────────────────── LOAN FUNCTIONS ──────────────────────
def get_member_loans(member_id):
    if not DB_CONNECTED:
        return [l for l in loans if l["member_id"] == member_id]

    query = """
        SELECT l.loan_id, b.title, l.loan_date, l.due_date
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        WHERE l.member_id = %s AND l.return_date IS NULL
    """
    return execute(query, (member_id,), fetch=True)

def issue_loan(book_id, member_id):
    if not DB_CONNECTED:
        # Check max 3 loans
        if len([l for l in loans if l["member_id"] == member_id]) >= 3:
            return False
        loans.append({
            "loan_id": len(loans)+1,
            "book_id": book_id,
            "member_id": member_id,
            "title": next(b["title"] for b in books if b["book_id"] == book_id),
            "loan_date": str(date.today()),
            "due_date": str(date.today() + timedelta(days=7))
        })
        # Reduce copies
        for b in books:
            if b["book_id"] == book_id:
                b["copies_available"] -= 1
                break
        return True

    # Real DB loan
    try:
        cur.execute("SELECT copies_available FROM books WHERE book_id = %s FOR UPDATE", (book_id,))
        book = cur.fetchone()
        if not book or book["copies_available"] <= 0:
            return False

        # Check member loan limit
        cur.execute("SELECT COUNT(*) FROM loans WHERE member_id = %s AND return_date IS NULL", (member_id,))
        count = cur.fetchone()[0]
        if count >= 3:
            return False

        cur.execute("""
            INSERT INTO loans (book_id, member_id, due_date)
            VALUES (%s, %s, %s)
        """, (book_id, member_id, date.today() + timedelta(days=7)))

        cur.execute("UPDATE books SET copies_available = copies_available - 1 WHERE book_id = %s", (book_id,))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False

def get_active_loans():
    if not DB_CONNECTED:
        return loans[:]
    return execute("""
        SELECT l.loan_id, b.title AS book_title, m.full_name AS member_name,
               l.loan_date, l.due_date
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        JOIN members m ON l.member_id = m.member_id
        WHERE l.return_date IS NULL
    """, fetch=True)

def return_loan(loan_id):
    if not DB_CONNECTED:
        global loans
        loan = next((l for l in loans if l["loan_id"] == loan_id), None)
        if loan:
            loans = [l for l in loans if l["loan_id"] != loan_id]
            for b in books:
                if b["book_id"] == loan["book_id"]:
                    b["copies_available"] += 1
        return

    cur.execute("""
        UPDATE loans SET return_date = CURRENT_DATE WHERE loan_id = %s AND return_date IS NULL
    """, (loan_id,))
    if cur.rowcount > 0:
        cur.execute("UPDATE books SET copies_available = copies_available + 1 WHERE book_id = (SELECT book_id FROM loans WHERE loan_id = %s)", (loan_id,))
        conn.commit()

# ────────────────────── CLUBS ──────────────────────
def get_all_clubs():
    if not DB_CONNECTED:
        return clubs[:]
    return execute("""
        SELECT bc.club_id, bc.name, bc.description, COUNT(cm.member_id) AS member_count
        FROM book_clubs bc
        LEFT JOIN club_members cm ON bc.club_id = cm.club_id
        GROUP BY bc.club_id
    """, fetch=True)