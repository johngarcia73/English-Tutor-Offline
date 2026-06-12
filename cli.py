"""
CLI Menu system for the English Tutor Offline application.

This module provides:
- Interactive menu navigation
- User input handling with validation
- Clear menu display
- Error handling for invalid inputs
- Support for different menu screens
"""

import logging
import sys
from typing import Callable, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class MenuOption:
    """Represents a menu option."""
    
    def __init__(self, key: str, label: str, action: Callable, help_text: str = ""):
        """
        Initialize a menu option.
        
        Args:
            key: Key to select this option (e.g., "1", "a")
            label: Display label for the option
            action: Function to call when selected
            help_text: Optional help text for the option
        """
        self.key = key
        self.label = label
        self.action = action
        self.help_text = help_text
    
    def display(self) -> str:
        """Return formatted menu option."""
        return f"  [{self.key}] {self.label}"


class Menu:
    """
    Interactive menu system.
    
    Handles display, user input, and navigation through menu options.
    """
    
    def __init__(self, title: str, subtitle: str = ""):
        """
        Initialize a menu.
        
        Args:
            title: Menu title
            subtitle: Optional menu subtitle
        """
        self.title = title
        self.subtitle = subtitle
        self.options: Dict[str, MenuOption] = {}
        self.back_action: Optional[Callable] = None
    
    def add_option(self, key: str, label: str, action: Callable, help_text: str = "") -> None:
        """
        Add an option to the menu.
        
        Args:
            key: Key to select this option
            label: Display label
            action: Function to execute
            help_text: Optional help text
        """
        self.options[key.lower()] = MenuOption(key, label, action, help_text)
    
    def set_back_action(self, action: Callable) -> None:
        """
        Set the action to execute when going back.
        
        Args:
            action: Function to execute when user selects back
        """
        self.back_action = action
    
    def display(self) -> None:
        """Display the menu on screen."""
        self._clear_screen()
        
        # Title with decoration
        print("\n" + "=" * 60)
        print(f"  {self.title}")
        if self.subtitle:
            print(f"  {self.subtitle}")
        print("=" * 60 + "\n")
        
        # Options
        for key in sorted(self.options.keys()):
            print(self.options[key].display())
        
        # Back option (if applicable)
        if self.back_action:
            print("  [B] Go Back")
        
        print("  [Q] Quit")
        print("\n" + "-" * 60)
    
    def get_user_choice(self) -> Optional[str]:
        """
        Get user choice with validation.
        
        Returns:
            Selected key, or None if quit/error
        """
        while True:
            try:
                user_input = input("  Select option: ").strip().lower()
                
                if not user_input:
                    print("  Please enter a valid option.")
                    continue
                
                if user_input == 'q':
                    return 'q'
                
                if user_input == 'b' and self.back_action:
                    return 'b'
                
                if user_input in self.options:
                    return user_input
                
                print(f"  Invalid option: '{user_input}'. Please try again.")
                
            except KeyboardInterrupt:
                print("\n  Application interrupted by user.")
                return 'q'
            except EOFError:
                return 'q'
            except Exception as e:
                logger.error(f"Error getting user choice: {e}")
                print("  An error occurred. Please try again.")
    
    def execute_option(self, key: str) -> bool:
        """
        Execute the action for a given key.
        
        Args:
            key: Option key to execute
            
        Returns:
            True if menu should continue, False if quit
        """
        if key == 'q':
            return False
        
        if key == 'b' and self.back_action:
            try:
                self.back_action()
                return True
            except Exception as e:
                logger.error(f"Error executing back action: {e}")
                print(f"  Error: {e}")
                return True
        
        if key in self.options:
            try:
                self.options[key].action()
                return True
            except Exception as e:
                logger.error(f"Error executing menu action: {e}")
                print(f"  Error: {e}")
                return True
        
        return True
    
    def run(self) -> None:
        """
        Run the menu loop.
        
        Displays menu, gets input, and executes actions until quit.
        """
        while True:
            self.display()
            choice = self.get_user_choice()
            
            if choice is None:
                continue
            
            if not self.execute_option(choice):
                break
            
            # Show prompt to continue
            if choice != 'b':
                try:
                    input("  Press ENTER to continue...")
                except (KeyboardInterrupt, EOFError):
                    break
    
    @staticmethod
    def _clear_screen() -> None:
        """Clear the terminal screen."""
        try:
            import os
            os.system('clear' if os.name != 'nt' else 'cls')
        except Exception:
            # Fallback if clear fails
            print("\n" * 2)


class CLIHelper:
    """Helper functions for CLI operations."""
    
    @staticmethod
    def print_section(title: str) -> None:
        """Print a section header."""
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")
    
    @staticmethod
    def print_success(message: str) -> None:
        """Print a success message."""
        print(f"\n  ✓ {message}\n")
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print an error message."""
        print(f"\n  ✗ ERROR: {message}\n")
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Print a warning message."""
        print(f"\n  ⚠ WARNING: {message}\n")
    
    @staticmethod
    def print_info(message: str) -> None:
        """Print an info message."""
        print(f"\n  ℹ {message}\n")
    
    @staticmethod
    def print_list(items: List[str], title: str = "") -> None:
        """Print a formatted list."""
        if title:
            print(f"\n  {title}:")
        for i, item in enumerate(items, 1):
            print(f"    {i}. {item}")
        print()
    
    @staticmethod
    def get_yes_no(prompt: str) -> bool:
        """
        Get yes/no input from user.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            True if yes, False if no
        """
        while True:
            response = input(f"  {prompt} (y/n): ").strip().lower()
            if response in ('y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            else:
                print("  Please enter 'y' or 'n'.")
    
    @staticmethod
    def get_choice(prompt: str, choices: List[str]) -> Optional[str]:
        """
        Get choice from user.
        
        Args:
            prompt: Prompt to display
            choices: List of valid choices
            
        Returns:
            Selected choice or None
        """
        print(f"\n  {prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"    {i}. {choice}")
        
        while True:
            try:
                user_input = input("\n  Select option (number): ").strip()
                idx = int(user_input) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
                else:
                    print(f"  Please enter a number between 1 and {len(choices)}.")
            except ValueError:
                print("  Please enter a valid number.")
            except (KeyboardInterrupt, EOFError):
                return None
