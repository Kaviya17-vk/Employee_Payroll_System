import sqlite3
import datetime
import os

# Custom Exception for handling invalid inputs or missing records
class PayrollSystemError(Exception):
    pass

# Base Class demonstrating OOP (Encapsulation & Inheritance)
class Person:
    def __init__(self, name, role):
        self.name = name
        self.role = role

# Derived Class for Employee
class Employee(Person):
    def __init__(self, emp_id, name, role, base_salary):
        super().__init__(name, role)
        self.emp_id = emp_id
        self.base_salary = base_salary

# Main System Class managing Database, Attendance, Payroll, and File Reports
class PayrollSystem:
    def __init__(self, db_name="payroll_system.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    # Create required SQLite tables
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                emp_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                base_salary REAL NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                UNIQUE(emp_id, date),
                FOREIGN KEY (emp_id) REFERENCES employees (emp_id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    # Generate Unique Employee ID (e.g., EMP101, EMP102)
    def generate_emp_id(self):
        self.cursor.execute("SELECT emp_id FROM employees ORDER BY emp_id DESC LIMIT 1")
        last_emp = self.cursor.fetchone()
        if last_emp:
            last_num = int(last_emp[0].replace("EMP", ""))
            return f"EMP{last_num + 1}"
        return "EMP101"

    # 1. Add Employee
    def add_employee(self, name, role, base_salary):
        try:
            if base_salary <= 0:
                raise PayrollSystemError("Salary must be greater than zero.")
            emp_id = self.generate_emp_id()
            emp = Employee(emp_id, name, role, base_salary)
            self.cursor.execute(
                "INSERT INTO employees (emp_id, name, role, base_salary) VALUES (?, ?, ?, ?)",
                (emp.emp_id, emp.name, emp.role, emp.base_salary)
            )
            self.conn.commit()
            print(f"\n[SUCCESS] Employee added! Generated ID: {emp.emp_id}")
        except Exception as e:
            print(f"\n[ERROR] Could not add employee: {e}")

    # 2. Update Employee
    def update_employee(self, emp_id, name, role, base_salary):
        try:
            self.cursor.execute("SELECT * FROM employees WHERE emp_id = ?", (emp_id,))
            if not self.cursor.fetchone():
                raise PayrollSystemError("Employee ID not found.")
            if base_salary <= 0:
                raise PayrollSystemError("Salary must be greater than zero.")
            
            self.cursor.execute(
                "UPDATE employees SET name = ?, role = ?, base_salary = ? WHERE emp_id = ?",
                (name, role, base_salary, emp_id)
            )
            self.conn.commit()
            print(f"\n[SUCCESS] Employee {emp_id} updated successfully.")
        except Exception as e:
            print(f"\n[ERROR] Update failed: {e}")

    # 3. Delete Employee
    def delete_employee(self, emp_id):
        try:
            self.cursor.execute("SELECT * FROM employees WHERE emp_id = ?", (emp_id,))
            if not self.cursor.fetchone():
                raise PayrollSystemError("Employee ID not found.")
            
            self.cursor.execute("DELETE FROM employees WHERE emp_id = ?", (emp_id,))
            self.conn.commit()
            print(f"\n[SUCCESS] Employee {emp_id} deleted.")
        except Exception as e:
            print(f"\n[ERROR] Delete failed: {e}")

    # 4. View All Employees
    def view_employees(self):
        self.cursor.execute("SELECT * FROM employees")
        rows = self.cursor.fetchall()
        print("\n--- EMPLOYEE LIST ---")
        if not rows:
            print("No employees found.")
        else:
            print(f"{'ID':<10} {'Name':<20} {'Role':<15} {'Monthly Salary':<15}")
            print("-" * 60)
            for row in rows:
                print(f"{row[0]:<10} {row[1]:<20} {row[2]:<15} Rs.{row[3]:<15.2f}")

    # 5. Record Daily Attendance
    def record_attendance(self, emp_id, date_str, status):
        try:
            # Validate Employee
            self.cursor.execute("SELECT * FROM employees WHERE emp_id = ?", (emp_id,))
            if not self.cursor.fetchone():
                raise PayrollSystemError("Employee ID not found.")

            # Validate Date Format (YYYY-MM-DD)
            datetime.datetime.strptime(date_str, "%Y-%m-%d")

            # Validate Status
            valid_statuses = ["Present", "Absent", "Leave"]
            status = status.capitalize()
            if status not in valid_statuses:
                raise PayrollSystemError("Invalid status. Choose Present, Absent, or Leave.")

            self.cursor.execute(
                "INSERT INTO attendance (emp_id, date, status) VALUES (?, ?, ?)",
                (emp_id, date_str, status)
            )
            self.conn.commit()
            print(f"\n[SUCCESS] Attendance recorded for {emp_id} on {date_str} as {status}.")
        except sqlite3.IntegrityError:
            print(f"\n[ERROR] Attendance already marked for {emp_id} on {date_str}.")
        except ValueError:
            print("\n[ERROR] Invalid date format. Use YYYY-MM-DD.")
        except Exception as e:
            print(f"\n[ERROR] {e}")

    # 6. Calculate Monthly Attendance & Display Report
    def get_monthly_attendance(self, emp_id, year_month):
        self.cursor.execute("SELECT name FROM employees WHERE emp_id = ?", (emp_id,))
        emp = self.cursor.fetchone()
        if not emp:
            raise PayrollSystemError("Employee ID not found.")

        self.cursor.execute(
            "SELECT status, COUNT(*) FROM attendance WHERE emp_id = ? AND date LIKE ? GROUP BY status",
            (emp_id, f"{year_month}-%")
        )
        records = dict(self.cursor.fetchall())
        present = records.get("Present", 0)
        absent = records.get("Absent", 0)
        leave = records.get("Leave", 0)
        return emp[0], present, absent, leave

    def display_attendance_report(self, emp_id, year_month):
        try:
            name, present, absent, leave = self.get_monthly_attendance(emp_id, year_month)
            print(f"\n--- ATTENDANCE REPORT ({year_month}) ---")
            print(f"Employee ID : {emp_id}")
            print(f"Name        : {name}")
            print(f"Present     : {present} days")
            print(f"Absent      : {absent} days")
            print(f"Leave       : {leave} days")
        except Exception as e:
            print(f"\n[ERROR] {e}")

    # 7. Calculate Salary & Generate File Report (File Handling)
    def generate_salary_report(self, emp_id, year_month):
        try:
            self.cursor.execute("SELECT name, role, base_salary FROM employees WHERE emp_id = ?", (emp_id,))
            emp = self.cursor.fetchone()
            if not emp:
                raise PayrollSystemError("Employee ID not found.")

            name, role, base_salary = emp
            _, present, absent, leave = self.get_monthly_attendance(emp_id, year_month)

            # Standard 30-day month calculation (Paid: Present + Leave, Unpaid: Absent)
            total_working_days = 30
            per_day_salary = base_salary / total_working_days
            payable_days = present + leave
            net_salary = per_day_salary * payable_days

            report_content = (
                f"=========================================\n"
                f"         MONTHLY SALARY SLIP             \n"
                f"=========================================\n"
                f"Month          : {year_month}\n"
                f"Employee ID    : {emp_id}\n"
                f"Employee Name  : {name}\n"
                f"Role           : {role}\n"
                f"-----------------------------------------\n"
                f"Base Salary    : Rs. {base_salary:.2f}\n"
                f"Present Days   : {present}\n"
                f"Paid Leaves    : {leave}\n"
                f"Absent Days    : {absent}\n"
                f"-----------------------------------------\n"
                f"Net Payable    : Rs. {net_salary:.2f}\n"
                f"=========================================\n"
            )

            print("\n" + report_content)

            # Save report to a text file (File Handling requirement)
            filename = f"Salary_Slip_{emp_id}_{year_month}.txt"
            with open(filename, "w") as file:
                file.write(report_content)
            print(f"[SUCCESS] Salary report saved to '{filename}'")

        except Exception as e:
            print(f"\n[ERROR] Could not generate salary report: {e}")

    def close(self):
        self.conn.close()

# Menu-Driven Program Execution
def main():
    system = PayrollSystem()
    
    while True:
        print("\n=== EMPLOYEE ATTENDANCE & PAYROLL SYSTEM ===")
        print("1. Add Employee")
        print("2. Update Employee")
        print("3. Delete Employee")
        print("4. View All Employees")
        print("5. Record Daily Attendance")
        print("6. Display Monthly Attendance Report")
        print("7. Generate Salary Report (Text File)")
        print("8. Exit")
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            name = input("Enter Name: ").strip()
            role = input("Enter Role: ").strip()
            
            try:
                salary = float(input("Enter Monthly Base Salary: "))
                system.add_employee(name, role, salary)
            except ValueError:
                print("\n[ERROR] Please enter a valid numeric salary.")

        elif choice == '2':
            emp_id = input("Enter Employee ID to update (e.g., EMP101): ").strip().upper()
            name = input("Enter New Name: ").strip()
            role = input("Enter New Role: ").strip()
            try:
                salary = float(input("Enter New Base Salary: "))
                system.update_employee(emp_id, name, role, salary)
            except ValueError:
                print("\n[ERROR] Please enter a valid numeric salary.")

        elif choice == '3':
            emp_id = input("Enter Employee ID to delete: ").strip().upper()
            system.delete_employee(emp_id)

        elif choice == '4':
            system.view_employees()

        elif choice == '5':
            emp_id = input("Enter Employee ID: ").strip().upper()
            date_str = input("Enter Date (YYYY-MM-DD) [Leave blank for today]: ").strip()
            if not date_str:
                date_str = datetime.date.today().strftime("%Y-%m-%d")
            status = input("Enter Status (Present / Absent / Leave): ").strip()
            system.record_attendance(emp_id, date_str, status)

        elif choice == '6':
            emp_id = input("Enter Employee ID: ").strip().upper()
            year_month = input("Enter Year-Month (YYYY-MM) [e.g., 2026-11]: ").strip()
            system.display_attendance_report(emp_id, year_month)

        elif choice == '7':
            emp_id = input("Enter Employee ID: ").strip().upper()
            year_month = input("Enter Year-Month (YYYY-MM) [e.g., 2026-11]: ").strip()
            system.generate_salary_report(emp_id, year_month)

        elif choice == '8':
            system.close()
            print("Exiting system. Goodbye!")
            break

        else:
            print("\n[ERROR] Invalid choice. Please select between 1 and 8.")


if __name__ == "__main__":
    main()
