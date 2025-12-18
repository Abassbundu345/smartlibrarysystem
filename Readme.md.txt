# SmartLibrary – Library Management System

*A Professional PyQt5 Desktop Application with Role-Based Access Control*

![Python](https://img.shields.io/badge/python-3.9%2B-blue)  
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.7-orange)  
![License](https://img.shields.io/badge/license-MIT-green)  
![Status](https://img.shields.io/badge/status-Complete%20%26%20Fully%20Functional-success)

---

## Project Overview

*SmartLibrary* is a modern, fully functional desktop-based *Library Management System* built using *Python* and *PyQt5*. It provides distinct interfaces for two user roles:

- *Members* – Browse catalog, borrow books (max 3), view current loans with overdue alerts, and participate in book clubs.
- *Librarians* – Full administrative control: manage loans & returns, add/remove books, create and manage book clubs, view real-time statistics.

The application follows *clean Object-Oriented Programming (OOP)* principles, implements the *Data Access Object (DAO)* pattern, and includes a *robust demo mode* for offline testing.

---

## Key Features

| Feature                         | Member | Librarian | Description |
|-------------------------------|--------|-----------|-----------|
| Secure Role-Based Login       | Yes    | Yes       | Email + password authentication |
| Book Catalog with Search      | Yes    | Yes       | Real-time filtering |
| Borrow Books (max 3, 7-day loan) | Yes    | –         | Enforced business rules |
| View Current Loans            | Yes    | Yes       | Due date & overdue warnings (red) |
| Return Books                  | –      | Yes       | With confirmation dialog |
| Add / Manage Books            | –      | Yes       | Full CRUD operations |
| Book Clubs Management         | View & Join | Full CRUD | Create, view, delete clubs |
| Real-Time Dashboard Stats     | –      | Yes       | Total books, active loans, clubs |
| Demo Mode (No DB Required)    | Yes    | Yes       | Works offline with fallback data |

---

## Screenshots

*(Add your screenshots to a screenshots/ folder and update links)*

```markdown
![Login Screen](screenshots/login.png)
![Member Dashboard](screenshots/member_dashboard.png)
![Librarian Loans](screenshots/librarian_loans.png)
![Book Clubs](screenshots/book_clubs.png)
