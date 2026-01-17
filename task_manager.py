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
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    
    def save_tasks(self):
        """Save tasks to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, description: str, priority: str = "medium") -> int:
        """Add a new task"""
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "completed_at": None
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
        
        print("\n" + "="*60)
        print(f"{'ID':<5} {'Status':<10} {'Priority':<10} {'Description'}")
        print("="*60)
        for task in filtered_tasks:
            status_icon = "✓" if task["status"] == "completed" else "○"
            priority_icon = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task["priority"], "⚪")
            print(f"{task['id']:<5} {status_icon} {task['status']:<8} {priority_icon} {task['priority']:<8} {task['description']}")
        print("="*60 + "\n")
    
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
                   priority: Optional[str] = None) -> bool:
        """Update task description or priority"""
        for task in self.tasks:
            if task["id"] == task_id:
                if description:
                    task["description"] = description
                if priority:
                    task["priority"] = priority
                self.save_tasks()
                return True
        return False


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
        print("  8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            description = input("Enter task description: ").strip()
            if not description:
                print("Error: Description cannot be empty.")
                continue
            priority = input("Enter priority (high/medium/low) [default: medium]: ").strip().lower()
            if priority not in ["high", "medium", "low"]:
                priority = "medium"
            task_id = manager.add_task(description, priority)
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
                if manager.update_task(task_id, 
                                       description if description else None,
                                       priority if priority else None):
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
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

