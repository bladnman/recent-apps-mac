import os
import subprocess

def is_git_repo(folder_path):
    """Check if a folder is a Git repository."""
    return os.path.isdir(os.path.join(folder_path, '.git'))

def is_repo_clean(repo_path):
    """Check if a Git repository has no uncommitted changes."""
    try:
        # Run the `git status` command
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # The `git status --porcelain` output is empty if there are no changes
        return result.stdout.strip() == ""
    except subprocess.CalledProcessError as e:
        print(f"Error checking repository at {repo_path}: {e.stderr}")
        return False

def check_projects_for_git(base_path):
    """Find and list project folders without a Git repository and check if repos are clean."""
    for subfolder in os.listdir(base_path):
        subfolder_path = os.path.join(base_path, subfolder)

        # Ensure we are checking only directories
        if os.path.isdir(subfolder_path):
            print()
            print(f"Checking in {subfolder_path}...")

            # Search only one level deep within the base_path
            for project in os.listdir(subfolder_path):
                project_path = os.path.join(subfolder_path, project)

                if os.path.isdir(project_path):
                    if is_git_repo(project_path):
                        # Check if the Git repository is clean
                        if not is_repo_clean(project_path):
                            print(f"⚠️ {project_path} has uncommitted changes.")
                    else:
                        print(f"❌ {project_path} is not a Git repository.")

if __name__ == "__main__":
    base_path = os.path.expanduser('~/code')  # Replace with your actual base path
    check_projects_for_git(base_path)