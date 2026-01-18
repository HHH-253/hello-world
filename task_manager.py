import json
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Optional

class TaskManager:
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: List[Dict] = self.load_tasks()
    
def load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        # NEW FEATURE: Added backward compatibility for tasks missing category/due_date fields
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

        # Be conservative: only accept a top-level list of task dicts
        if not isinstance(data, list):
            return []

        cleaned: List[Dict] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            # Ensure required keys exist with sensible defaults
            item.setdefault("id", None)
            item.setdefault("description", "")
            item.setdefault("priority", "medium")
            item.setdefault("status", "pending")
            item.setdefault("created_at", item.get("created_at", datetime.now().isoformat()))
            item.setdefault("completed_at", None)
            # Optional fields: keep as empty string when absent for backward compat
            item.setdefault("category", "")
            item.setdefault("due_date", "")
            cleaned.append(item)
        return cleaned

    def save_tasks(self):
        # Write atomically to avoid corrupting the data file
        dirpath = os.path.dirname(self.data_file) or "."
        tmpname = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, dir=dirpath) as tmp:
                tmpname = tmp.name
                json.dump(self.tasks, tmp, indent=2)
            # Atomic replace
            os.replace(tmpname, self.data_file)
        finally:
            # In case of exceptions, ensure leftover temp file is removed
            if tmpname and os.path.exists(tmpname):
                try:
                    os.remove(tmpname)
                except Exception:
                    pass

    def _normalize_due_date(self, due_date: str) -> str:
        """Validate and normalize due_date in YYYY-MM-DD or return empty string for blank."""
        if not due_date:
            return ""
        try:
            dt = datetime.strptime(due_date, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format, expected YYYY-MM-DD")

    def add_task(self, description: str, priority: str = "medium",
                 category: str = "", due_date: str = "") -> int:
        """Add a new task. Returns new task id."""
        # Normalize and validate due_date (raises ValueError on bad format)
        normalized_due = self._normalize_due_date(due_date)
        # Generate id robustly to avoid duplicates after deletions
        new_id = max((t.get("id") or 0 for t in self.tasks), default=0) + 1
        task = {
            "id": new_id,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "category": category,
            "due_date": normalized_due
        }
        self.tasks.append(task)
        self.save_tasks()
        return new_id
    
def list_tasks(self, status: Optional[str] = None):
        filtered_tasks = [t for t in self.tasks if status is None or t.get("status") == status]
        if not filtered_tasks:
            print("No tasks found.")
            return
            
        # ENHANCED: Added category and due date display in task listing
        print("\n" + "="*80)
        print(f"{'ID':<5} {'Status':<10} {'Priority':<10} {'Category':<12} {'Description':<30} {'Due Date'}")
        print("="*80)
        for task in filtered_tasks:
            status_icon = "✓" if task.get("status") == "completed" else "○"
            priority_icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task.get("priority"), "⚪")
            category = task.get("category", "") or "-"
            due_date = task.get("due_date", "") or "-"
            desc = task.get('description', "")
            desc_display = (desc[:28] + "..") if len(desc) > 28 else desc
            print(f"{task.get('id', ''):<5} {status_icon} {task.get('status',''):<8} {priority_icon} {task.get('priority',''):<8} {category:<12} {desc_display:<30} {due_date}")
        print("="*80 + "\n")
    
def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        for task in self.tasks:
            if task.get("id") == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False
    
def delete_task(self, task_id: int) -> bool:
        for i, task in enumerate(self.tasks):
            if task.get("id") == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False
    
def update_task(self, task_id: int, description: Optional[str] = None, 
                   priority: Optional[str] = None, category: Optional[str] = None,
                   due_date: Optional[str] = None) -> bool:
        """Update task description, priority, category, or due date.
        For category/due_date: pass None to leave unchanged, pass '' to clear the value.
        ```
        """
        for task in self.tasks:
            if task.get("id") == task_id:
                if description:
                    task["description"] = description
                if priority:
                    task["priority"] = priority
                if category is not None:  # allow empty string to clear
                    task["category"] = category
                if due_date is not None:  # allow empty string to clear
                    task["due_date"] = due_date
                self.save_tasks()
                return True
        return False
    
def search_tasks(self, keyword: str) -> List[Dict]:
        """NEW FEATURE: Search tasks by keyword in description or category"""
        keyword_lower = keyword.lower()
        return [task for task in self.tasks 
                if keyword_lower in task.get("description", "").lower() or 
                   keyword_lower in task.get("category", "").lower()]
    
def get_statistics(self) -> Dict:
        """NEW FEATURE: Get statistics about tasks"""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.get("status") == "completed"])
        pending = len([t for t in self.tasks if t.get("status") == "pending"])
        high_priority = len([t for t in self.tasks if t.get("priority") == "high" and t.get("status") == "pending"])
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "high_priority_pending": high_priority
        }
    
def sort_tasks(self, sort_by: str = "id") -> List[Dict]:
        """NEW FEATURE: Sort tasks by different criteria"""
        tasks_copy = self.tasks.copy()
        if sort_by == "priority":
            priority_order = {"high": 1, "medium": 2, "low": 3}
            tasks_copy.sort(key=lambda x: (priority_order.get(x.get("priority", "medium"), 3), x.get("id", 0)))
        elif sort_by == "date":
            tasks_copy.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_by == "due_date":
            tasks_copy.sort(key=lambda x: (x.get("due_date") or "9999-12-31", x.get("id", 0)))
        return tasks_copy
    
def list_tasks_by_category(self, category: str):
        """NEW FEATURE: List all tasks in a specific category"""
        filtered_tasks = [t for t in self.tasks if t.get("category", "").lower() == category.lower()]
        if not filtered_tasks:
            print(f"No tasks found in category '{category}'.")
            return
        
        print(f"\n" + "="*80)
        print(f"Tasks in category: {category}")
        print("="*80)
        print(f"{'ID':<5} {'Status':<10} {'Priority':<10} {'Category':<12} {'Description':<30} {'Due Date'}")
        print("="*80)
        for task in filtered_tasks:
            status_icon = "✓" if task.get("status") == "completed" else "○"
            priority_icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task.get("priority"), "⚪")
            due_date_str = f" (Due: {task.get('due_date')})" if task.get("due_date") else ""
            category_display = task.get("category", "") or "-"
            desc = task.get("description", "")
            desc_display = (desc[:28] + "..") if len(desc) > 28 else desc
            print(f"{task.get('id', ''):<5} {status_icon} {task.get('status',''):<8} {priority_icon} {task.get('priority',''):<8} {category_display:<12} {desc_display:<30} {task.get('due_date','')}")
        print("="*80 + "\n")


def main():
    """Main CLI interface"""
    manager = TaskManager()
    while True:
        print("\nTask Manager")
        print("="*40)
        print("  1. Add task")
        print("  2. List tasks")
        print("  3. List pending tasks")
        print("  4. List completed tasks")
        print("  5. Complete task")
        print("  6. Update task")
        print("  7. Delete task")
        print("  8. Search tasks")          # NEW FEATURE
        print("  9. Show statistics")        # NEW FEATURE
        print("  10. Sort tasks")            # NEW FEATURE
        print("  11. List tasks by category") # NEW FEATURE
        print("  12. Exit")
        
        choice = input("\nEnter your choice (1-12): ").strip()
        
        if choice == "1":
            description = input("Enter task description: ").strip()
            if not description:
                print("Error: Description cannot be empty.")
                continue
            priority = input("Enter priority (high/medium/low) [default: medium]: ").strip().lower()
            if priority not in ["high", "medium", "low"]:
                priority = "medium"
            # NEW FEATURE: Added category and due date input when adding tasks
            category = input("Enter category (optional, press Enter to skip): ").strip()
            due_date_in = input("Enter due date (YYYY-MM-DD format, optional, press Enter to skip): ").strip()
            # validate due date
            try:
                task_id = manager.add_task(description, priority, category, due_date_in)
            except ValueError as e:
                print(f"Error: {e}. Task not added.")
                continue
            print(f"✓ Task {task_id} added successfully!")
        
        elif choice == "2":
            manager.list_tasks()
        
        elif choice == "3":
            manager.list_tasks(status="pending")
        
        elif choice == "4":
            manager.list_tasks(status="completed")
        
        elif choice == "5":
            try:
                task_id = int(input("Enter task ID to complete: ").strip())
            except ValueError:
                print("Error: Please enter a valid task ID.")
                continue
            if manager.complete_task(task_id):
                print(f"✓ Task {task_id} marked as completed!")
            else:
                print(f"✗ Task {task_id} not found.")
        
        elif choice == "6":
            try:
                task_id = int(input("Enter task ID to update: ").strip())
            except ValueError:
                print("Error: Please enter a valid task ID.")
                continue
            description = input("Enter new description (press Enter to skip): ").strip()
            priority = input("Enter new priority (high/medium/low, press Enter to skip): ").strip().lower()
            if priority and priority not in ["high", "medium", "low"]:
                print("Error: Invalid priority. Update cancelled.")
                continue
            # NEW FEATURE: Added category and due date update options
            print("Enter new category (leave blank to keep current, '-' to clear):")
            category_in = input("Category: ").strip()
            print("Enter new due date (YYYY-MM-DD, leave blank to keep current, '-' to clear):")
            due_date_in = input("Due date: ").strip()
            # Interpret sentinel values:
            if category_in == "":
                category_arg = None
            elif category_in == "-":
                category_arg = ""
            else:
                category_arg = category_in
            if due_date_in == "":
                due_arg = None
            elif due_date_in == "-":
                due_arg = ""
            else:
                # validate date format before applying update
                try:
                    due_arg = manager._normalize_due_date(due_date_in)
                except ValueError:
                    print("Error: Invalid date format (use YYYY-MM-DD). Update cancelled.")
                    continue
            if manager.update_task(task_id, 
                                   description if description else None,
                                   priority if priority else None,
                                   category_arg,
                                   due_arg):
                print(f"✓ Task {task_id} updated successfully!")
            else:
                print(f"✗ Task {task_id} not found.")
        
        elif choice == "7":
            try:
                task_id = int(input("Enter task ID to delete: ").strip())
            except ValueError:
                print("Error: Please enter a valid task ID.")
                continue
            if manager.delete_task(task_id):
                print(f"✓ Task {task_id} deleted.")
            else:
                print(f"✗ Task {task_id} not found.")
        
        elif choice == "8":
            # NEW FEATURE: Search tasks by keyword
            keyword = input("Enter keyword to search: ").strip()
            if not keyword:
                print("Error: Keyword cannot be empty.")
                continue
            results = manager.search_tasks(keyword)
            if results:
                print(f"\nFound {len(results)} task(s) matching '{keyword}':")
                print("="*80)
                print(f"{'ID':<5} {'Status':<10} {'Priority':<10} {'Category':<12} {'Description'}")
                print("="*80)
                for task in results:
                    status_icon = "✓" if task.get("status") == "completed" else "○"
                    priority_icon = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(task.get("priority"), "⚪")
                    category = task.get("category", "") or "-"
                    print(f"{task.get('id',''):<5} {status_icon} {task.get('status',''):<8} {priority_icon} {task.get('priority',''):<8} {category:<12} {task.get('description','')}")
                print("="*80 + "\n")
            else:
                print(f"No tasks found matching '{keyword}'.")
        
        elif choice == "9":
            # NEW FEATURE: Display task statistics
            stats = manager.get_statistics()
            print("\n" + "="*40)
            print("Task Statistics")
            print("="*40)
            print(f"Total tasks:        {stats['total']}")
            print(f"Completed:          {stats['completed']}")
            print(f"Pending:            {stats['pending']}")
            print(f"High priority (pending): {stats['high_priority_pending']}")
            if stats['total'] > 0:
                completion_rate = (stats['completed'] / stats['total']) * 100
                print(f"Completion rate:    {completion_rate:.1f}%")
            print("="*40 + "\n")
        
        elif choice == "10":
            # NEW FEATURE: Sort and display tasks
            print("\nSort by:")
            print("  1. Priority (high to low)")
            print("  2. Date created (newest first)")
            print("  3. Due date (earliest first)")
            sort_choice = input("Enter sort option (1-3): ").strip()
            sort_by = {"1": "priority", "2": "date", "3": "due_date"}.get(sort_choice, "id")
            sorted_tasks = manager.sort_tasks(sort_by)
            if sorted_tasks:
                print("\n" + "="*80)
                print(f"Tasks sorted by {sort_by}:")
                print("="*80)
                print(f"{'ID':<5} {'Status':<10} {'Priority':<10} {'Category':<12} {'Description':<30} {'Due Date'}")
                print("="*80)
                for task in sorted_tasks:
                    status_icon = "✓" if task.get("status") == "completed" else "○"
                    priority_icon = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(task.get("priority"), "⚪")
                    category = task.get("category", "") or "-"
                    due_date = task.get("due_date", "") or "-"
                    desc = task.get('description', "")
                    desc_display = (desc[:28] + "..") if len(desc) > 28 else desc
                    print(f"{task.get('id',''):<5} {status_icon} {task.get('status',''):<8} {priority_icon} {task.get('priority',''):<8} {category:<12} {desc_display:<30} {due_date}")
                print("="*80 + "\n")
            else:
                print("No tasks to sort.")
        
        elif choice == "11":
            # NEW FEATURE: List tasks by category
            manager.list_tasks()
            category = input("Enter category name: ").strip()
            if not category:
                print("Error: Category cannot be empty.")
                continue
            manager.list_tasks_by_category(category)
        
        elif choice == "12":
            print("Goodbye!")
            break
        
    
if __name__ == "__main__":
    main()