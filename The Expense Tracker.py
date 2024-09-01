import json
import os
from datetime import datetime
import sys

class ExpenseManager:
    def __init__(self, data_file='expenses.json'):
        self.data_file = data_file
        self.expenses = []
        self.categories = ["Food", "Transportation", "Entertainment", "Utilities", "Others"]
        self.load_data()

    def load_data(self):
        """Load expenses and categories from the JSON file."""
        if not os.path.exists(self.data_file):
            self.save_data()  # Create the file if it doesn't exist
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                self.expenses = data.get('expenses', [])
                self.categories = data.get('categories', self.categories)
        except json.JSONDecodeError:
            print("Error: Corrupted data file. Starting with empty data.")
            self.expenses = []
            self.categories = ["Food", "Transportation", "Entertainment", "Utilities", "Others"]
        except Exception as e:
            print(f"An error occurred while loading data: {e}")
            sys.exit(1)

    def save_data(self):
        """Save expenses and categories to the JSON file."""
        data = {
            'expenses': self.expenses,
            'categories': self.categories
        }
        try:
            with open(self.data_file, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"An error occurred while saving data: {e}")
            sys.exit(1)

    def add_expense(self, amount, description, category, date=None):
        """Add a new expense to the list."""
        if category not in self.categories:
            print(f"Category '{category}' not found. Adding it to categories.")
            self.categories.append(category)
        if date is None:
            date = datetime.today().strftime('%Y-%m-%d')
        expense = {
            'amount': amount,
            'description': description,
            'category': category,
            'date': date
        }
        self.expenses.append(expense)
        self.save_data()
        print("Expense added successfully!")

    def view_expenses(self, filter_month=None, filter_year=None):
        """Display all expenses, optionally filtered by month and year."""
        filtered_expenses = self.expenses
        if filter_month and filter_year:
            filtered_expenses = [
                exp for exp in self.expenses
                if self._extract_month(exp['date']) == filter_month and self._extract_year(exp['date']) == filter_year
            ]
        elif filter_year:
            filtered_expenses = [
                exp for exp in self.expenses
                if self._extract_year(exp['date']) == filter_year
            ]
        elif filter_month:
            filtered_expenses = [
                exp for exp in self.expenses
                if self._extract_month(exp['date']) == filter_month
            ]

        if not filtered_expenses:
            print("No expenses to show.")
            return

        print(f"{'Date':<12} {'Category':<15} {'Amount':<10} {'Description'}")
        print("-" * 60)
        for exp in filtered_expenses:
            print(f"{exp['date']:<12} {exp['category']:<15} ${exp['amount']:<10.2f} {exp['description']}")
        print("-" * 60)
        print(f"Total Expenses: ${sum(exp['amount'] for exp in filtered_expenses):.2f}")

    def view_summary(self, month=None, year=None):
        """Provide summaries of expenses."""
        summary = {}
        if month and year:
            filtered_expenses = [
                exp for exp in self.expenses
                if self._extract_month(exp['date']) == month and self._extract_year(exp['date']) == year
            ]
        elif year:
            filtered_expenses = [
                exp for exp in self.expenses
                if self._extract_year(exp['date']) == year
            ]
        elif month:
            filtered_expenses = [
                exp for exp in self.expenses
                if self._extract_month(exp['date']) == month
            ]
        else:
            filtered_expenses = self.expenses

        for exp in filtered_expenses:
            category = exp['category']
            summary[category] = summary.get(category, 0) + exp['amount']

        print(f"{'Category':<20} {'Amount Spent'}")
        print("-" * 30)
        for category, amount in summary.items():
            print(f"{category:<20} ${amount:.2f}")
        print("-" * 30)
        print(f"Total Expenses: ${sum(summary.values()):.2f}")

    def add_category(self, category):
        """Add a new category."""
        if category in self.categories:
            print(f"Category '{category}' already exists.")
        else:
            self.categories.append(category)
            self.save_data()
            print(f"Category '{category}' added successfully.")

    def remove_category(self, category):
        """Remove an existing category."""
        if category not in self.categories:
            print(f"Category '{category}' does not exist.")
        else:
            self.categories.remove(category)
            # Optionally, you could reassign expenses in this category to 'Others' or another category
            for exp in self.expenses:
                if exp['category'] == category:
                    exp['category'] = 'Others'
            self.save_data()
            print(f"Category '{category}' removed successfully.")

    def _extract_month(self, date_str):
        """Extract month from date string."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').month
        except ValueError:
            return None

    def _extract_year(self, date_str):
        """Extract year from date string."""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').year
        except ValueError:
            return None

def display_menu():
    print("\n===== Expense Tracker =====")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. View Summary")
    print("4. Manage Categories")
    print("5. Exit")

def display_manage_categories_menu():
    print("\n--- Manage Categories ---")
    print("1. Add Category")
    print("2. Remove Category")
    print("3. View Categories")
    print("4. Back to Main Menu")

def get_validated_input(prompt, validation_func, error_message):
    """Utility function to get validated user input."""
    while True:
        user_input = input(prompt)
        try:
            return validation_func(user_input)
        except Exception:
            print(error_message)

def main():
    manager = ExpenseManager()

    while True:
        display_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            # Add Expense
            try:
                amount = float(input("Enter amount spent: $"))
                if amount < 0:
                    print("Amount cannot be negative.")
                    continue
            except ValueError:
                print("Invalid amount. Please enter a numerical value.")
                continue

            description = input("Enter description: ").strip()
            print("Select a category from the following list:")
            for idx, cat in enumerate(manager.categories, start=1):
                print(f"{idx}. {cat}")
            try:
                cat_choice = int(input(f"Enter category number (1-{len(manager.categories)}): "))
                if 1 <= cat_choice <= len(manager.categories):
                    category = manager.categories[cat_choice - 1]
                else:
                    print("Invalid category selection.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a number corresponding to the category.")
                continue

            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if date_input == '':
                date = None
            else:
                try:
                    datetime.strptime(date_input, '%Y-%m-%d')  # Validate date format
                    date = date_input
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    continue

            manager.add_expense(amount, description, category, date)

        elif choice == '2':
            # View Expenses
            print("\n--- View Expenses ---")
            print("Filter options:")
            print("1. No Filter")
            print("2. Filter by Month and Year")
            print("3. Filter by Year")
            print("4. Filter by Month")
            filter_choice = input("Select a filter option (1-4): ").strip()

            filter_month = None
            filter_year = None

            if filter_choice == '2':
                # Filter by Month and Year
                try:
                    month = int(input("Enter month (1-12): "))
                    year = int(input("Enter year (e.g., 2023): "))
                    if 1 <= month <= 12:
                        filter_month = month
                        filter_year = year
                    else:
                        print("Invalid month.")
                        continue
                except ValueError:
                    print("Invalid input. Please enter numerical values for month and year.")
                    continue
            elif filter_choice == '3':
                # Filter by Year
                try:
                    year = int(input("Enter year (e.g., 2023): "))
                    filter_year = year
                except ValueError:
                    print("Invalid input. Please enter a numerical value for year.")
                    continue
            elif filter_choice == '4':
                # Filter by Month
                try:
                    month = int(input("Enter month (1-12): "))
                    if 1 <= month <= 12:
                        filter_month = month
                    else:
                        print("Invalid month.")
                        continue
                except ValueError:
                    print("Invalid input. Please enter a numerical value for month.")
                    continue
            elif filter_choice == '1':
                pass
            else:
                print("Invalid selection.")
                continue

            manager.view_expenses(filter_month, filter_year)

        elif choice == '3':
            # View Summary
            print("\n--- View Summary ---")
            print("Summary options:")
            print("1. No Filter")
            print("2. Filter by Month and Year")
            print("3. Filter by Year")
            print("4. Filter by Month")
            summary_choice = input("Select a summary option (1-4): ").strip()

            summary_month = None
            summary_year = None

            if summary_choice == '2':
                # Filter by Month and Year
                try:
                    month = int(input("Enter month (1-12): "))
                    year = int(input("Enter year (e.g., 2023): "))
                    if 1 <= month <= 12:
                        summary_month = month
                        summary_year = year
                    else:
                        print("Invalid month.")
                        continue
                except ValueError:
                    print("Invalid input. Please enter numerical values for month and year.")
                    continue
            elif summary_choice == '3':
                # Filter by Year
                try:
                    year = int(input("Enter year (e.g., 2023): "))
                    summary_year = year
                except ValueError:
                    print("Invalid input. Please enter a numerical value for year.")
                    continue
            elif summary_choice == '4':
                # Filter by Month
                try:
                    month = int(input("Enter month (1-12): "))
                    if 1 <= month <= 12:
                        summary_month = month
                    else:
                        print("Invalid month.")
                        continue
                except ValueError:
                    print("Invalid input. Please enter a numerical value for month.")
                    continue
            elif summary_choice == '1':
                pass
            else:
                print("Invalid selection.")
                continue

            manager.view_summary(summary_month, summary_year)

        elif choice == '4':
            # Manage Categories
            while True:
                display_manage_categories_menu()
                cat_choice = input("Select an option (1-4): ").strip()
                if cat_choice == '1':
                    # Add Category
                    new_category = input("Enter new category name: ").strip()
                    if new_category:
                        manager.add_category(new_category)
                    else:
                        print("Category name cannot be empty.")
                elif cat_choice == '2':
                    # Remove Category
                    print("Existing Categories:")
                    for idx, cat in enumerate(manager.categories, start=1):
                        print(f"{idx}. {cat}")
                    try:
                        rem_choice = int(input(f"Enter category number to remove (1-{len(manager.categories)}): "))
                        if 1 <= rem_choice <= len(manager.categories):
                            category_to_remove = manager.categories[rem_choice - 1]
                            manager.remove_category(category_to_remove)
                        else:
                            print("Invalid category selection.")
                    except ValueError:
                        print("Invalid input. Please enter a number corresponding to the category.")
                elif cat_choice == '3':
                    # View Categories
                    print("\n--- Categories ---")
                    for idx, cat in enumerate(manager.categories, start=1):
                        print(f"{idx}. {cat}")
                elif cat_choice == '4':
                    # Back to Main Menu
                    break
                else:
                    print("Invalid selection. Please choose between 1-4.")

        elif choice == '5':
            # Exit
            print("Exiting Expense Tracker. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid selection. Please choose a valid option (1-5).")

if __name__ == "__main__":
    main()
