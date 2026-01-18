#!/usr/bin/env python3
"""
Task Manager - A simple command-line task management application
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional



class TaskManager:
    """Manages tasks with persistence to JSON file"""
    
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks = self.load_tasks()
    
    def load_tasks(self) -> List[Dict]:
        """Load tasks from JSON file"""
        # NEW FEATURE: Added backward compatibility for tasks missing category/due_date fields
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    tasks = json.load(f)
                    # Ensure all tasks have category and due_date fields for backward compatibility
                    for task in tasks:
                        if "category" not in task:
                            task["category"] = ""
                        if "due_date" not in task:
                            task["due_date"] = ""
                    return tasks
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, description: str, priority: str = "medium", category: str = "", due_date: str = "") -> int:
        """Add a new task"""
        # NEW FEATURE: Added category and due_date parameters to tasks
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "category": category,  # NEW: Category field for organizing tasks
            "due_date": due_date   # NEW: Due date field for task deadlines
        }
        self.tasks.append(task)
        self.save_tasks()
        return task["id"]
    
    def list_tasks(self, status: Optional[str] = None):
        """List all tasks, optionally filtered by status"""
        filtered_tasks = self.tasks
        if status:
            filtered_tasks = [t for t in self.tasks if t["status"] == status]
        
        if not filtered_tasks:
            print("No tasks found.")
            return
        
        # ENHANCED: Added category and due date display in task listing
        print("\n" + "="*80)
        print(f"{'ID':<5} {'Status':<10} {'Priority':<10} {'Category':<12} {'Description':<30} {'Due Date'}")
        print("="*80)
        for task in filtered_tasks:
            status_icon = "✓" if task["status"] == "completed" else "○"
            priority_icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task["priority"], "⚪")
            category = task.get("category", "") or "-"
            due_date = task.get("due_date", "") or "-"
            desc = task['description'][:28] + ".." if len(task['description']) > 28 else task['description']
            print(f"{task['id']:<5} {status_icon} {task['status']:<8} {priority_icon} {task['priority']:<8} {category:<12} {desc:<30} {due_date}")
        print("="*80 + "\n")
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False
    
    def update_task(self, task_id: int, description: Optional[str] = None, 
                   priority: Optional[str] = None, category: Optional[str] = None,
                   due_date: Optional[str] = None) -> bool:
        """Update task description, priority, category, or due date"""
        # NEW FEATURE: Extended update_task to support category and due_date updates
        for task in self.tasks:
            if task["id"] == task_id:
                if description:
                    task["description"] = description
                if priority:
                    task["priority"] = priority
                if category is not None:  # NEW: Allow updating category (including empty string)
                    task["category"] = category
                if due_date is not None:  # NEW: Allow updating due date (including empty string)
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
        completed = len([t for t in self.tasks if t["status"] == "completed"])
        pending = len([t for t in self.tasks if t["status"] == "pending"])
        high_priority = len([t for t in self.tasks if t.get("priority") == "high" and t["status"] == "pending"])
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
            tasks_copy.sort(key=lambda x: (priority_order.get(x.get("priority", "medium"), 3), x["id"]))
        elif sort_by == "date":
            tasks_copy.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_by == "due_date":
            tasks_copy.sort(key=lambda x: (x.get("due_date") or "9999-12-31", x["id"]))
        return tasks_copy
    
    def list_tasks_by_category(self, category: str):
        """NEW FEATURE: List all tasks in a specific category"""
        filtered_tasks = [t for t in self.tasks if t.get("category", "").lower() == category.lower()]
        if not filtered_tasks:
            print(f"No tasks found in category '{category}'.")
            return
        
        print(f"\n" + "="*60)
        print(f"Tasks in category: {category}")
        print("="*60)
        print(f"{'ID':<5} {'Status':<10} {'Priority':<10} {'Description'}")
        print("="*60)
        for task in filtered_tasks:
            status_icon = "✓" if task["status"] == "completed" else "○"
            priority_icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task["priority"], "⚪")
            due_date_str = f" (Due: {task.get('due_date', 'N/A')})" if task.get("due_date") else ""
            print(f"{task['id']:<5} {status_icon} {task['status']:<8} {priority_icon} {task['priority']:<8} {task['description']}{due_date_str}")
        print("="*60 + "\n")


def main():
    """Main CLI interface"""
    manager = TaskManager()
    
    print("="*60)
    print("Welcome to Task Manager!")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  1. Add task")
        print("  2. List all tasks")
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
            due_date = input("Enter due date (YYYY-MM-DD format, optional, press Enter to skip): ").strip()
            task_id = manager.add_task(description, priority, category, due_date)
            print(f"✓ Task {task_id} added successfully!")
        
        elif choice == "2":
            manager.list_tasks()
        
        elif choice == "3":
            manager.list_tasks(status="pending")
        
        elif choice == "4":
            manager.list_tasks(status="completed")
        
        elif choice == "5":
            manager.list_tasks(status="pending")
            try:
                task_id = int(input("Enter task ID to complete: ").strip())
                if manager.complete_task(task_id):
                    print(f"✓ Task {task_id} marked as completed!")
                else:
                    print(f"✗ Task {task_id} not found.")
            except ValueError:
                print("Error: Please enter a valid task ID.")
        
        elif choice == "6":
            manager.list_tasks()
            try:
                task_id = int(input("Enter task ID to update: ").strip())
                description = input("Enter new description (press Enter to skip): ").strip()
                priority = input("Enter new priority (high/medium/low, press Enter to skip): ").strip().lower()
                if priority and priority not in ["high", "medium", "low"]:
                    print("Error: Invalid priority. Update cancelled.")
                    continue
                # NEW FEATURE: Added category and due date update options
                category = input("Enter new category (press Enter to skip): ").strip()
                due_date = input("Enter new due date (YYYY-MM-DD, press Enter to skip): ").strip()
                if manager.update_task(task_id, 
                                       description if description else None,
                                       priority if priority else None,
                                       category if category else None,
                                       due_date if due_date else None):
                    print(f"✓ Task {task_id} updated successfully!")
                else:
                    print(f"✗ Task {task_id} not found.")
            except ValueError:
                print("Error: Please enter a valid task ID.")
        
        elif choice == "7":
            manager.list_tasks()
            try:
                task_id = int(input("Enter task ID to delete: ").strip())
                if manager.delete_task(task_id):
                    print(f"✓ Task {task_id} deleted successfully!")
                else:
                    print(f"✗ Task {task_id} not found.")
            except ValueError:
                print("Error: Please enter a valid task ID.")
        
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
                    status_icon = "✓" if task["status"] == "completed" else "○"
                    priority_icon = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(task["priority"], "⚪")
                    category = task.get("category", "") or "-"
                    print(f"{task['id']:<5} {status_icon} {task['status']:<8} {priority_icon} {task['priority']:<8} {category:<12} {task['description']}")
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
                    status_icon = "✓" if task["status"] == "completed" else "○"
                    priority_icon = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢"
                    }.get(task["priority"], "⚪")
                    category = task.get("category", "") or "-"
                    due_date = task.get("due_date", "") or "-"
                    desc = task['description'][:28] + ".." if len(task['description']) > 28 else task['description']
                    print(f"{task['id']:<5} {status_icon} {task['status']:<8} {priority_icon} {task['priority']:<8} {category:<12} {desc:<30} {due_date}")
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
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

