import re
import string
import numpy as np
from tkinter import Tk, Label, Entry, Button, StringVar, Frame, Checkbutton, IntVar
import matplotlib.pyplot as plt
import pyperclip  # To copy to clipboard

# Load a local dictionary file for dictionary attack checks
with open('/usr/share/dict/words', 'r') as file:
    dictionary_words = set(word.strip().lower() for word in file)

# Common weak passwords list
common_passwords = [
    '123456', 'password', '12345678', 'qwerty', '123456789',
    '12345', '1234', '111111', '1234567', 'dragon', '123123', 
    'baseball', 'football', 'letmein', 'monkey', 'abc123'
]

def is_common_password(password):
    """Check if the password is among common weak passwords."""
    return password.lower() in common_passwords

def contains_dictionary_words(password):
    """Check if the password contains any dictionary words."""
    words = re.findall(r'\b\w+\b', password.lower())
    return any(word in dictionary_words for word in words)

def calculate_entropy(password):
    """Calculate the entropy of a password."""
    charset_size = 0
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in string.punctuation for c in password):
        charset_size += len(string.punctuation)
    entropy = len(password) * np.log2(charset_size)
    return entropy

def levenshtein_distance(s1, s2):
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def has_repeated_patterns(password):
    """Check if the password has repeated patterns or sequences."""
    for i in range(1, len(password)//2 + 1):
        if password[:i] * (len(password)//i) == password:
            return True
    return False

def analyze_password(password):
    """Analyzes the strength of a password and provides a score and feedback."""
    length_score = len(password) * 5  # 5 points per character

    # Complexity scoring
    lower = len(re.findall(r'[a-z]', password))
    upper = len(re.findall(r'[A-Z]', password))
    digits = len(re.findall(r'\d', password))
    symbols = len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', password))

    complexity_score = (min(lower, 2) + min(upper, 2) +
                        min(digits, 2) + min(symbols, 2)) * 5

    # Uniqueness scoring
    unique_chars = len(set(password))
    uniqueness_score = (unique_chars / len(password)) * 10

    # Bonus for very diverse passwords
    diversity_bonus = 0
    if lower > 0 and upper > 0 and digits > 0 and symbols > 0:
        diversity_bonus = 10

    # Calculate entropy
    entropy = calculate_entropy(password)
    entropy_score = min(entropy / 2, 20)  # Cap entropy score at 20

    # Dictionary word penalty
    dictionary_penalty = 20 if contains_dictionary_words(password) else 0

    # Common password penalty
    common_penalty = 20 if is_common_password(password) else 0

    # Pattern penalty
    pattern_penalty = 15 if has_repeated_patterns(password) else 0

    # Levenshtein distance check with common passwords
    levenshtein_penalty = 0
    for common in common_passwords:
        if levenshtein_distance(password, common) <= 2:
            levenshtein_penalty = 10
            break

    # Calculate the total score
    total_score = (length_score + complexity_score + uniqueness_score +
                   diversity_bonus + entropy_score - dictionary_penalty -
                   common_penalty - pattern_penalty - levenshtein_penalty)
    total_score = max(0, min(total_score, 100))  # Cap the score between 0 and 100

    return int(total_score), generate_feedback(total_score, lower, upper, digits, symbols, unique_chars, entropy, dictionary_penalty, common_penalty, pattern_penalty, levenshtein_penalty)

def generate_feedback(score, lower, upper, digits, symbols, unique_chars, entropy, dictionary_penalty, common_penalty, pattern_penalty, levenshtein_penalty):
    """Generates feedback based on the password's score and components."""
    feedback = []

    if score < 50:
        feedback.append("Weak password.")
    elif score < 70:
        feedback.append("Moderate password.")
    else:
        feedback.append("Strong password!")

    if lower == 0:
        feedback.append("Add lowercase letters.")
    if upper == 0:
        feedback.append("Add uppercase letters.")
    if digits == 0:
        feedback.append("Add numbers.")
    if symbols == 0:
        feedback.append("Add special characters.")
    if unique_chars < 5:
        feedback.append("Increase variety of characters.")
    if entropy < 40:
        feedback.append("Increase password length or complexity.")
    if dictionary_penalty > 0:
        feedback.append("Avoid using dictionary words.")
    if common_penalty > 0:
        feedback.append("Avoid common passwords.")
    if pattern_penalty > 0:
        feedback.append("Avoid repeated patterns.")
    if levenshtein_penalty > 0:
        feedback.append("Password is too similar to common passwords.")

    if len(feedback) == 1:
        feedback.append("Great job!")

    return " ".join(feedback)

def plot_password_strength(score):
    """Plots the password strength using a pie chart."""
    labels = ['Strength', 'Weakness']
    sizes = [score, 100 - score]
    colors = ['#4CAF50', '#F44336']
    explode = (0.1, 0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')
    plt.title("Password Strength")
    plt.show()

def generate_strong_password(length=12):
    """Generate a strong random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(np.random.choice(list(characters), length))
    return password

def evaluate_password():
    """Evaluates the password entered by the user."""
    password = password_var.get()
    score, feedback = analyze_password(password)
    result_var.set(f"Score: {score}\nFeedback: {feedback}")
    plot_password_strength(score)

def toggle_password_display():
    """Toggle the display of password input between visible and hidden."""
    if show_password_var.get():
        password_entry.config(show='')
    else:
        password_entry.config(show='*')

def toggle_generated_password_display():
    """Toggle the display of the generated password between visible and hidden."""
    if show_generated_password_var.get():
        generated_password_label.config(text=generated_password_var.get())
    else:
        generated_password_label.config(text='*' * len(generated_password_var.get()))

def copy_to_clipboard():
    """Copy the generated password to the clipboard."""
    pyperclip.copy(generated_password_var.get())
    copy_button.config(text='Copied!', state='disabled')
    root.after(2000, lambda: copy_button.config(text='Copy', state='normal'))

# Setting up the GUI with Tkinter
root = Tk()
root.title("Advanced Password Strength Checker")

password_var = StringVar()
generated_password_var = StringVar()
result_var = StringVar()

show_password_var = IntVar()
show_generated_password_var = IntVar()

# UI Components
frame = Frame(root)
frame.pack(pady=20)

Label(frame, text="Enter your password:").grid(row=0, column=0, padx=5, pady=5)
password_entry = Entry(frame, textvariable=password_var, show='*')
password_entry.grid(row=0, column=1, padx=5, pady=5)
Button(frame, text="Check Strength", command=evaluate_password).grid(row=1, columnspan=2, pady=10)

Checkbutton(frame, text="Show Password", variable=show_password_var, command=toggle_password_display).grid(row=0, column=2)

Label(root, textvariable=result_var, wraplength=300, justify='left').pack(pady=10)

def on_generate_password():
    new_password = generate_strong_password()
    generated_password_var.set(new_password)
    generated_password_label.config(text=new_password if show_generated_password_var.get() else '*' * len(new_password))
    copy_button.config(text='Copy', state='normal')

Button(root, text="Generate Strong Password", command=on_generate_password).pack(pady=10)
generated_password_label = Label(root, text="", font=("Arial", 12))
generated_password_label.pack()

Checkbutton(root, text="Show Generated Password", variable=show_generated_password_var, command=toggle_generated_password_display).pack()

copy_button = Button(root, text="Copy", command=copy_to_clipboard)
copy_button.pack(pady=5)

root.geometry('400x500')
root.mainloop()
