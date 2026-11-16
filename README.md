# Employee Attendance & Payroll Processing System

A Python-based console application to manage employee records, track daily attendance, calculate monthly payroll, and generate individual salary slips using SQLite database and file handling.

## Features
* **Employee Management:** Add, update, delete, and view employee details.
* **Auto ID Generation:** Automatically generates unique Employee IDs (e.g., `EMP101`, `EMP102`).
* **Daily Attendance Tracking:** Record employee attendance as `Present`, `Absent`, or `Leave` with date validation and duplicate prevention.
* **Monthly Attendance Report:** View monthly summaries of Present, Absent, and Leave days for any employee.
* **Payroll Calculation & Salary Slip:** Calculates net payable salary based on attendance and exports individual salary reports as `.txt` files.

## Technical Concepts Used
* **Object-Oriented Programming (OOP):** Classes, Inheritance (`Person` -> `Employee`), and Encapsulation (`PayrollSystem`).
* **Database Integration:** `sqlite3` for persistent storage with relational tables (`employees` and `attendance`).
* **Exception Handling:** Custom exceptions (`PayrollSystemError`) and `try-except` blocks for input and database validation.
* **File Handling:** Automated generation of formatted `.txt` salary slips.

## How to Run
1. Clone or download this repository.
2. Ensure Python 3.x is installed on your system.
3. Run the application from the terminal:
   ```bash
   python main.py
   ```
4. Follow the on-screen menu options (1–8).

## Project Structure
* `main.py` - Complete source code for the application.
* `payroll_system.db` - SQLite database storing employee and attendance records.
* `Salary_Slip_EMP101_2026-11.txt` - Sample generated salary slip report.
