import tkinter as tk
from tkinter import ttk,messagebox
import json

# Add this function here
def load_games():
    try:
        with open("games.json", "r") as f:
            data = json.load(f)
            return data["games"]
    except FileNotFoundError:
        print("Error: games.json file not found")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in games.json")
        return []

# Replace the hardcoded list with this line
games = load_games()

# User preferences stays the same
user_preferences = {
    "selected_tags": [],
    "excluded_tags": [],
    "game_status": {}  
}

class GameTagApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project: Ember")
        self.root.iconbitmap("embericon.ico")

        # Frames
        self.tags_frame = ttk.LabelFrame(root, text="Select Tags", height=300)  # Set a fixed height
        self.tags_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tags_frame.grid_propagate(False)  # Prevent the frame from shrinking

        self.games_frame = ttk.LabelFrame(root, text="Filtered Games")
        self.games_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        self.actions_frame = ttk.LabelFrame(root, text="Actions")
        self.actions_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

        # Variables
        self.tag_vars = {}  # Holds each tag's Checkbutton variable
        self.filtered_games = []  # Holds filtered game results
        self.selected_game = tk.StringVar()  # Bind this to display which game is selected

        # Add this line to make sure status_var is initialized
        self.status_var = tk.StringVar(value="")

        # UI Components
        self.create_tags_ui()
        self.create_games_ui()
        self.create_actions_ui()
        self.load_preferences()
        self.filter_games()

    def create_tags_ui(self):
        """Creates the tag toggle section with scrollbar."""
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self.tags_frame)
        scrollbar = ttk.Scrollbar(self.tags_frame, orient="vertical", command=self.canvas.yview)
        
        # Create a frame inside the canvas to hold the checkbuttons
        self.tags_container = ttk.Frame(self.canvas)
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create a window in the canvas to hold the tags_container
        self.canvas_window = self.canvas.create_window((0, 0), window=self.tags_container, anchor="nw")
        
        # Get and sort all unique tags
        all_tags = sorted({tag for game in games for tag in game['tags']})

        # Create checkbuttons in the tags_container
        for tag in all_tags:
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(
                self.tags_container,
                text=tag,
                variable=var,
                command=self.filter_games
            )
            cb.pack(anchor="w", padx=5, pady=2)
            self.tag_vars[tag] = var

        # Bind configure events
        self.tags_container.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def create_games_ui(self):
        """Creates the listbox where filtered games are displayed."""
        self.games_listbox = tk.Listbox(self.games_frame, height=10, width=40)
        self.games_listbox.pack(padx=5, pady=5, fill="both", expand=True)
        self.games_listbox.bind("<<ListboxSelect>>", self.on_game_select)

    def create_actions_ui(self):
        """Creates buttons for game actions."""
        # Update Status Dropdown
        ttk.Label(self.actions_frame, text="Update Status:").grid(row=0, column=0, padx=5, pady=5)
        
        # Define the exact values we want to save
        status_options = ["played", "want to play", "not interested", "Fav"]
        
        self.status_dropdown = ttk.Combobox(
            self.actions_frame,
            textvariable=self.status_var,
            values=status_options,  # Use our defined values
            state="readonly"  # This prevents users from entering custom values
        )
        self.status_dropdown.grid(row=0, column=1, padx=5, pady=5)

        # Save Button
        save_button = ttk.Button(self.actions_frame, text="Save Status", command=self.save_status)
        save_button.grid(row=0, column=2, padx=5, pady=5)

        ## Refresh Button
        refresh_button = ttk.Button(self.actions_frame, text="Refresh Status", command=self.refresh_status)
        refresh_button.grid(row=0, column=3, padx=5, pady=5)


    def filter_games(self):
        """Filters games based on selected tags."""
        selected_tags = sorted([tag for tag, var in self.tag_vars.items() if var.get()])
        self.filtered_games = [
            game for game in games
            if all(tag in game['tags'] for tag in selected_tags)
        ]


        # Update games listbox
        self.games_listbox.delete(0, tk.END)  # Clear previous games
        for game in self.filtered_games:
            self.games_listbox.insert(tk.END, game['title'])

    def on_game_select(self, event):
        """Handles selecting a game in the listbox."""
        try:
            index = self.games_listbox.curselection()[0]  # Get the selected index
            self.selected_game.set(self.filtered_games[index]['title'])  # Get game title
        except IndexError:
            self.selected_game.set("")  # No selection

    def save_status(self):
        """Updates the status of a selected game."""
        print("\nSaving status...")
        print(f"Selected game: {self.selected_game.get()}")
        print(f"Selected status: {self.status_var.get()}")

        if not self.selected_game.get():
            print("Error: No game selected")
            return
        
        if not self.status_var.get():
            print("Error: No status selected")
            return

        # Find the selected game
        selected_game_data = None
        for game in games:
            if game['title'] == self.selected_game.get():
                selected_game_data = game
                break

        if not selected_game_data:
            print("Error: Game not found in data")
            return

        # Get the values we want to save
        game_id = str(selected_game_data['id'])
        game_title = selected_game_data['title']
        status = self.status_var.get()

        # First, try to load existing preferences
        try:
            with open("preferences.json", "r") as f:
                saved_preferences = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            saved_preferences = {
                "selected_tags": [],
                "excluded_tags": [],
                "game_status": {}
            }

        # Make sure game_status exists
        if 'game_status' not in saved_preferences:
            saved_preferences['game_status'] = {}

        # Add or update this game's status
        saved_preferences['game_status'][game_id] = {
            'title': game_title,
            'status': status
        }

        # Save back to file with error handling
        try:
            print("Saving updated preferences...")
            print(f"Current preferences: {saved_preferences}")
            
            with open("preferences.json", "w") as f:
                json.dump(saved_preferences, f, indent=4)
            
            # Update the global user_preferences to match the file
            global user_preferences
            user_preferences = saved_preferences
            
            print(f"Successfully saved! Game '{game_title}' status set to '{status}'")
        except Exception as e:
            print(f"Error saving to file: {e}")
            import traceback
            traceback.print_exc()

        messagebox.showinfo("", "Game " + game_title + " Status " + status + " Saved Successfully!")

    def refresh_status(self): ### error it loops
        """Filters games based on selected tags."""
        self.filter_games()
        messagebox.showinfo("Refresh Status", "Status Refreshed")

    def load_preferences(self):
        """Load saved preferences if they exist."""
        global user_preferences
        try:
            with open("preferences.json", "r") as f:
                user_preferences = json.load(f)
        except FileNotFoundError:
            user_preferences = {
                "selected_tags": [],
                "excluded_tags": [],
                "game_status": {}
            }

    def on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """When canvas is resized, resize the inner frame to match"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

# Initialize Tkinter
root = tk.Tk()
app = GameTagApp(root)
root.mainloop()