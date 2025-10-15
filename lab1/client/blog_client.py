import getpass
from typing import Optional, List, Dict

import requests


class BlogClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None

    def login(self, username: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                print("Login successful!")
                return True
            else:
                print(f"Login failed: {response.json().get('detail', 'Unknown error')}")
                return False
        except requests.exceptions.ConnectionError:
            print("Cannot connect to server. Make sure the server is running.")
            return False

    def get_posts(self) -> Optional[List[Dict]]:
        if not self.token:
            print("Please login first")
            return None

        try:
            response = requests.get(
                f"{self.base_url}/api/data",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get posts: {response.json().get('detail', 'Unknown error')}")
                return None
        except requests.exceptions.ConnectionError:
            print("Cannot connect to server")
            return None

    def create_post(self, title: str, content: str) -> bool:
        if not self.token:
            print("Please login first")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/api/data",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"title": title, "content": content}
            )
            if response.status_code == 200:
                print("Post created successfully!")
                return True
            else:
                print(f"Failed to create post: {response.json().get('detail', 'Unknown error')}")
                return False
        except requests.exceptions.ConnectionError:
            print("Cannot connect to server")
            return False

    def interactive_menu(self):
        while True:
            print("\n=== Blog Client ===")
            print("1. Login")
            print("2. View Posts")
            print("3. Create Post")
            print("4. Exit")

            choice = input("Choose an option (1-4): ").strip()

            if choice == "1":
                self._handle_login()
            elif choice == "2":
                self._handle_view_posts()
            elif choice == "3":
                self._handle_create_post()
            elif choice == "4":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def _handle_login(self):
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        self.login(username, password)

    def _handle_view_posts(self):
        posts = self.get_posts()
        if posts:
            print("\n=== Posts ===")
            for post in posts:
                print(f"\nTitle: {post['title']}")
                print(f"Content: {post['content']}")
                print(f"Author ID: {post['author_id']}")
                print(f"Created: {post['created_at']}")
                print("-" * 40)
        else:
            print("No posts to display")

    def _handle_create_post(self):
        title = input("Post title: ").strip()
        content = input("Post content: ").strip()
        if title and content:
            self.create_post(title, content)
        else:
            print("Title and content are required")


def main():
    client = BlogClient()
    print("Blog Client Started")
    print("Make sure the server is running on http://localhost:8000")
    client.interactive_menu()


if __name__ == "__main__":
    main()