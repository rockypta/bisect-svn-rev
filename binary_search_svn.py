
import subprocess
import argparse

def check_text_in_command_output(command, text):
    """
    Executes a command and checks if the given text is present in its output.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return text in result.stdout
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        print(f"Stderr: {e.stderr}")
        return False

def binary_search_revisions(start_rev, end_rev, text, command):
    """
    Performs a binary search on the SVN revisions to find the first revision
    where the given text appears in the command's output.
    """
    good = -1
    bad = -1

    low = start_rev
    high = end_rev

    while low <= high:
        mid = (low + high) // 2
        print(f"Checking revision {mid}...")

        # Update to the revision
        subprocess.run(["svn", "update", "-r", str(mid)], check=True)

        if check_text_in_command_output(command, text):
            print(f"Text found in revision {mid}.")
            good = mid
            high = mid - 1
        else:
            print(f"Text not found in revision {mid}.")
            bad = mid
            low = mid + 1

    if good != -1:
        # Now, we need to check if the previous revision also has the text
        if good > start_rev:
            print(f"Verifying revision {good - 1}...")
            subprocess.run(["svn", "update", "-r", str(good - 1)], check=True)
            if not check_text_in_command_output(command, text):
                print(f"First appearance of the text is in revision {good}.")
                return good

        # If we are here, it means the text was present in the first revision checked
        # or the previous revision also had the text.
        # We need to search in the lower half.
        return binary_search_revisions(start_rev, good -1, text, command)


    return -1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Binary search SVN revisions for a text string in a command's output.")
    parser.add_argument("start_rev", type=int, help="The starting revision.")
    parser.add_argument("end_rev", type=int, help="The ending revision.")
    parser.add_argument("text", help="The text to search for.")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The command to execute.")

    args = parser.parse_args()

    if not args.command:
        print("Error: You must specify a command to execute.")
        exit(1)

    first_rev = binary_search_revisions(args.start_rev, args.end_rev, args.text, args.command)

    if first_rev != -1:
        print(f"The first revision containing the text is: {first_rev}")
    else:
        print("The text was not found in any revision in the given range.")
