from dotenv import load_dotenv, dotenv_values
import os
import subprocess
import sys
import re
import json
from openai import OpenAI
import difflib
from datetime import datetime


load_dotenv()

# Check if the variable is loading
config = dotenv_values(".env")  # Returns a dictionary
OPEN_AI_API_KEY = config["OPEN_AI_API_KEY"]
print(OPEN_AI_API_KEY)

class AIGitPushAssistant:
    def __init__(self):
        load_dotenv(override=True)  # Load environment variables from .env file
        # Placeholders for key variables - replace these with your actual details
        self.repo_path = "C:/Users/willi/Desktop/AI/gitbuddy"  # Full path to your git repository
        self.default_commit_message = "default_commit_message"  # Default commit message if no specific one is provided
        self.github_username = "prometheusomniscient"  # Your GitHub username
        self.branch_name = "main"  # Default branch to push to (e.g., 'main' or 'master')

        # AI Configuration
        self.openai_api_key = OPEN_AI_API_KEY
        # self.openai_api_key = os.getenv("OPEN_AI_API_KEY")
        print(self.openai_api_key)
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please set the 'OPEN_AI_API_KEY' environment variable.")
        self.client = OpenAI(api_key=self.openai_api_key)

        # AI-powered features configuration
        self.ai_commit_message_generation = True
        self.code_review_enabled = True
        self.changelog_generation_enabled = True

    def git_push(self):
        """
        Push committed changes to the remote repository .
        Dummy string to test the push functionality.
        """
        try:
            self.run_command(f"git push origin {self.branch_name}")
            print(f"Pushed changes to branch '{self.branch_name}'.")
        except Exception as e:
            print(f"Error pushing changes: {e}")

    def git_commit(self, commit_message):
        """
        Commit staged changes with a commit message .
        """
        try:
            if not commit_message:
                commit_message = self.default_commit_message
            self.run_command(f'git commit -m "{commit_message}"')
            print(f"Committed changes with message: {commit_message}")
        except Exception as e:
            print(f"Error committing changes: {e}")

    def git_add_all(self):
        """
        Stage all changes in the Git repository.
        """
        try:
            self.run_command("git add .")
            print("Staged all changes.")
        except Exception as e:
            print(f"Error staging changes: {e}")

    def check_git_status(self):
        """
        Check the status of the Git repository.
        """
        try:
            status = self.run_command("git status --short")
            return status
        except Exception as e:
            print(f"Error checking Git status: {e}")
            return None

    def change_to_repo_directory(self):
        """
        Change the current working directory to the repository path.
        """
        try:
            os.chdir(self.repo_path)
            print(f"Changed working directory to: {self.repo_path}")
        except FileNotFoundError:
            print(f"Error: Repository path '{self.repo_path}' does not exist.")
        except Exception as e:
            print(f"Error changing directory: {e}")

    def run_command(self, command):
        """
        Run a shell command and return its output
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8"  # Explicitly set encoding to utf-8
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            print(f"Error output: {e.stderr}")
            return None

    def get_git_diff(self):
        """
        Get the git diff of staged changes
        """
        return self.run_command("git diff --staged")

    def generate_ai_commit_message(self, diff):
        try:
            response = self.client.openai_api_key.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software engineer helping to generate concise, descriptive git commit messages."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a professional commit message for these code changes:\n\n{diff}\n\nProvide a concise summary that explains the purpose of the changes."
                    }
                ],
                max_tokens=100
            )
            print("AI Response:", response)  # Debugging line
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Commit Message Generation Error: {e}")
            return self.default_commit_message

    def ai_code_review(self, diff):
        """
        Perform an AI-powered basic code review on changes
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software engineer conducting a code review. Provide constructive feedback on code changes."
                    },
                    {
                        "role": "user",
                        "content": f"Perform a code review on these changes. Identify potential improvements, security risks, or best practice violations:\n\n{diff}"
                    }
                ],
                max_tokens=300
            )
            review = response.choices[0].message.content.strip()

            # If review suggests serious issues, prompt user
            if any(keyword in review.lower() for keyword in ['warning', 'risk', 'security', 'potential issue']):
                print("\n🚨 AI Code Review Highlights Potential Concerns:")
                print(review)
                response = input("Would you like to proceed with the commit? (yes/no): ").lower()
                return response == 'yes'

            return True
        except Exception as e:
            print(f"AI Code Review Error: {e}")
            return True

    def generate_changelog(self, commit_message):
        """
        Generate a changelog entry for the commit
        """
        try:
            # Read existing CHANGELOG.md or create if not exists
            changelog_path = os.path.join(self.repo_path, 'CHANGELOG.md')

            # Existing changelog content or start a new one
            existing_content = ""
            if os.path.exists(changelog_path):
                with open(changelog_path, 'r') as f:
                    existing_content = f.read()

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are helping to maintain a professional changelog. Format entries clearly and concisely."
                    },
                    {
                        "role": "user",
                        "content": f"Create a changelog entry for this commit message: '{commit_message}'\n\nExisting Changelog:\n{existing_content}"
                    }
                ],
                max_tokens=200
            )

            new_entry = response.choices[0].message.content.strip()

            # Prepend new entry to changelog
            full_changelog = f"## {self.get_current_date()}\n{new_entry}\n\n{existing_content}"

            # Write updated changelog
            with open(changelog_path, 'w') as f:
                f.write(full_changelog)

            print("📝 Changelog updated successfully!")
        except Exception as e:
            print(f"Changelog Generation Error: {e}")

    def get_current_date(self):
        """
        Get current date in a changelog-friendly format
        """
        return datetime.now().strftime("%Y-%m-%d")

    def interactive_push(self, custom_message=None):
        """
        Enhanced git push workflow with AI capabilities
        """
        # Change to repo directory
        self.change_to_repo_directory()

        # Check status
        changes = self.check_git_status()
        if not changes:
            print("No changes to commit.")
            return

        print("Changes detected:")
        print(changes)

        # Stage changes
        self.git_add_all()

        # Get git diff for AI analysis
        diff = self.get_git_diff()

        # AI Code Review
        if self.code_review_enabled:
            review_passed = self.ai_code_review(diff)
            if not review_passed:
                print("Commit aborted due to code review concerns.")
                return

        # AI Commit Message Generation
        commit_message = self.generate_ai_commit_message(diff)
        # commit_message = custom_message
        # if self.ai_commit_message_generation and not custom_message:
        #     ai_generated_message = self.generate_ai_commit_message(diff)
        #     if ai_generated_message:
        #         commit_message = ai_generated_message

        # Commit with message
        self.git_commit(commit_message)

        # Generate Changelog
        if self.changelog_generation_enabled:
            self.generate_changelog(commit_message)

        # Push to remote
        self.git_push()

        print("Push completed successfully!")

def main():
    git_buddy = AIGitPushAssistant()

    # Check for command-line arguments
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:]).lower()

        if "hey git buddy" in command:
            # Extract custom commit message if provided
            custom_message = command.split("hey git buddy")[-1].strip()

            if custom_message and custom_message != "can you push the code":
                git_buddy.interactive_push(custom_message)
            else:
                git_buddy.interactive_push()
        else:
            print("Unrecognized command. Use 'hey git buddy' followed by an optional commit message.")
    else:
        print("Please provide a command. Example: python script.py 'hey git buddy update login feature'")

if __name__ == "__main__":
    main()