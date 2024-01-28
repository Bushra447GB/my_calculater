import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
from datetime import datetime  # Add this line to import the datetime module

class FinancialCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Financial Calculator")

        # Create or connect to the database
        self.conn = sqlite3.connect("financial_data.db")
        self.create_table()

        # Frequency options
        self.frequency_options = ["Monthly", "Yearly"]

        # Income
        self.income_frame = ttk.LabelFrame(root, text="Income")
        self.income_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.labels_income = ["Total Salary", "Earned Income & Pension"]
        self.income_entries = self.create_entries(self.income_frame, self.labels_income, self.frequency_options, default_frequency="Monthly")

        # Expenses
        self.expenses_frame = ttk.LabelFrame(root, text="Expenses")
        self.expenses_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.labels_expenses = [
            "Rent", "Bills", "Mortgage", "Tax", "Home Maintenance", "Loan", "Living Expenses (Grocery)", "Household Supplies",
            "Shopping", "Self-Investment", "Healthcare (Medical Spending/Insurance)",
            "Children & Education", "Emergency Fund & Other", "Gifts & Donations", "Hobbies & Sports", "Travel & Vacation", "Other Spending"
        ]
        self.expenses_entries = self.create_entries(self.expenses_frame, self.labels_expenses, self.frequency_options, default_frequency="Monthly")

        # Total Expenses
        ttk.Label(self.expenses_frame, text="Total Expenses").grid(row=len(self.labels_expenses), column=0, sticky="w", pady=5)
        self.total_expenses_entry = ttk.Entry(self.expenses_frame, state="readonly")
        self.total_expenses_entry.grid(row=len(self.labels_expenses), column=1, pady=5)
        ttk.Label(self.expenses_frame, text="/").grid(row=len(self.labels_expenses), column=2, sticky="w", pady=5)

        # Frequency selector for total expenses
        self.expenses_frequency_var = tk.StringVar()
        self.expenses_frequency_var.set(self.frequency_options[0])
        ttk.Label(self.expenses_frame, text="").grid(row=len(self.labels_expenses), column=3, pady=5)
        self.expenses_frequency_menu = ttk.Combobox(self.expenses_frame, values=self.frequency_options, textvariable=self.expenses_frequency_var)
        self.expenses_frequency_menu.grid(row=len(self.labels_expenses), column=3, pady=5)

        # Calculate Expenses Button
        self.calculate_expenses_button = ttk.Button(self.expenses_frame, text="Calculate Expenses", command=self.calculate_expenses)
        self.calculate_expenses_button.grid(row=len(self.labels_expenses) + 1, column=1, columnspan=3, pady=10)

        # Savings
        self.savings_frame = ttk.LabelFrame(root, text="Savings")
        self.savings_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.labels_savings = ["Total Savings"]
        self.savings_entries = self.create_entries(self.savings_frame, self.labels_savings, self.frequency_options, default_frequency="Monthly")

        # Calculate Button
        self.calculate_button = ttk.Button(root, text="Calculate", command=self.calculate_budget)
        self.calculate_button.grid(row=3, column=0, pady=5)

        # Save Button
        self.save_button = ttk.Button(root, text="Save Data", command=self.save_data)
        self.save_button.grid(row=4, column=0, pady=5)

        # Report Button
        self.report_button = ttk.Button(root, text="Generate Report", command=self.generate_report)
        self.report_button.grid(row=5, column=0, pady=10)

    def create_entries(self, parent, labels, frequency_options, default_frequency="Monthly"):
        entries = {}
        frequency_vars = {}
        for i, label in enumerate(labels):
            ttk.Label(parent, text=label).grid(row=i, column=0, sticky="w", pady=5)
            entries[label] = ttk.Entry(parent)
            entries[label].grid(row=i, column=1, pady=5)
            ttk.Label(parent, text="/").grid(row=i, column=2, sticky="e", pady=5)
            ttk.Label(parent, text="").grid(row=i, column=3, pady=5)
            frequency_combobox = ttk.Combobox(parent, values=["Monthly", "Yearly"])
            frequency_combobox.set("Monthly")
            frequency_combobox.grid(row=i, column=3, pady=5)
            entries[label + "_frequency"] = frequency_combobox

        return entries

    def calculate_expenses(self):
        try:
            # Collect expenses data
            expenses_data = {}
            for label in self.labels_expenses:
                category = label
                sub_category = ""
                if "Healthcare" in label:
                    category, sub_category = label.split(" (")
                    sub_category = sub_category[:-1]
                expenses_data.setdefault(category, {})[sub_category] = {
                    "amount": float(self.expenses_entries[label].get()),
                    "frequency": self.expenses_entries[label + "_frequency"].get()
                }

            # Calculate total expenses
            total_expenses = sum(
                (expense["amount"] * 12) if expense["frequency"] == "Yearly" else expense["amount"]
                for category in expenses_data.values() for expense in category.values()
            )

            # Update total expenses entry
            self.total_expenses_entry.config(state="normal")
            self.total_expenses_entry.delete(0, tk.END)
            self.total_expenses_entry.insert(0, f"{total_expenses:,.2f}")
            self.total_expenses_entry.config(state="readonly")

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")

    def calculate_budget(self):
        try:
            # Collect income data
            income_data = {label: {
                "amount": float(self.income_entries[label].get()),
                "frequency": self.income_entries[label + "_frequency"].get()
            } for label in self.labels_income}

            # Collect total expenses
            total_expenses = float(self.total_expenses_entry.get())

            # Calculate total savings
            total_savings = sum(
                (income["amount"] * 12) if income["frequency"] == "Yearly" else income["amount"]
                for income in income_data.values()
            ) - total_expenses

            # Update savings entry
            self.savings_entries["Total Savings"].delete(0, tk.END)
            self.savings_entries["Total Savings"].insert(0, f"{total_savings:,.2f}")

            # Display result
            result_text = f"Total Savings: ${total_savings:,.2f} "
            # (Assuming you have a label called result_label)
            # self.result_label.config(text=result_text)

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")

    def save_data(self):
        try:
            # Collect income data
            income_data = {label: {
                "amount": float(self.income_entries[label].get()),
                "frequency": self.income_entries[label + "_frequency"].get()
            } for label in self.labels_income}

            # Collect expenses data
            expenses_data = {}
            for label in self.labels_expenses:
                category = label
                sub_category = ""
                if "Healthcare" in label:
                    category, sub_category = label.split(" (")
                    sub_category = sub_category[:-1]
                expenses_data.setdefault(category, {})[sub_category] = {
                    "amount": float(self.expenses_entries[label].get()),
                    "frequency": self.expenses_entries[label + "_frequency"].get()
                }

            # Calculate total expenses
            total_expenses = sum(
                (expense["amount"] * 12) if expense["frequency"] == "Yearly" else expense["amount"]
                for category in expenses_data.values() for expense in category.values()
            )

            # Calculate total savings
            total_savings = sum(
                (income["amount"] * 12) if income["frequency"] == "Yearly" else income["amount"]
                for income in income_data.values()
            ) - total_expenses

            # Get the current date and time in the correct format
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save data to the database
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO financial_data (total_salary, earned_income, pension_social_security, total_expenses, total_savings, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                income_data["Total Salary"]["amount"],
                income_data["Earned Income & Pension"]["amount"],
                0,  # Assuming "pension_social_security" is not collected in the UI
                total_expenses,
                total_savings,
                current_timestamp
            ))

            self.conn.commit()
            cursor.close()

            print("Data saved successfully!")

            messagebox.showinfo("Success", "Data saved successfully!")

        except ValueError as ve:
            print(f"ValueError: {ve}")
            messagebox.showerror("Error", "Invalid input. Please enter valid numbers.")

    def generate_report(self):
        try:
            # Get the start date from the user
            start_date_str = simpledialog.askstring("Input", "Enter the start date (e.g., 01/01/2024):")
            if not start_date_str:
                return

            # Parse the start date
            try:
                start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use the format 'dd/mm/yyyy' (e.g., 01/01/2024).")
                return

            # Get the end date from the user
            end_date_str = simpledialog.askstring("Input", "Enter the end date (e.g., 31/01/2024):")
            if not end_date_str:
                return

            # Parse the end date
            try:
                end_date = datetime.strptime(end_date_str, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use the format 'dd/mm/yyyy' (e.g., 31/01/2024).")
                return

            # Fetch data from the database for the specified period
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT total_salary, earned_income, pension_social_security, total_expenses, total_savings
                FROM financial_data
                WHERE timestamp BETWEEN ? AND ?
            """, (start_date, end_date))
            rows = cursor.fetchall()
            cursor.close()

            # Generate the report
            if rows:
                report = f"Financial Report for {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}\n\n"
                for row in rows:
                    report += f"Total Salary: {row[0]:,.2f} ({'Yearly' if row[0] > 0 else 'Monthly'})\n"
                    report += f"Earned Income: {row[1]:,.2f} ({'Yearly' if row[1] > 0 else 'Monthly'})\n"
                    report += f"Pension & Social Security: {row[2]:,.2f} ({'Yearly' if row[2] > 0 else 'Monthly'})\n"
                    report += f"Total Expenses: {row[3]:,.2f} ({'Yearly' if row[3] > 0 else 'Monthly'})\n"
                    report += f"Total Savings: {row[4]:,.2f}\n\n"

                # Ask the user to select a file to save the report
                file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

                # Save the report to the selected file
                if file_path:
                    with open(file_path, "w") as file:
                        file.write(report)

                    messagebox.showinfo("Report Saved", f"Report saved successfully to:\n{file_path}")

            else:
                messagebox.showwarning("No Data", "No data available for the specified period.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_salary REAL,
                earned_income REAL,
                pension_social_security REAL,
                total_expenses REAL,
                total_savings REAL
            )
        """)
        self.conn.commit()
        cursor.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinancialCalculator(root)
    root.mainloop()
