import subprocess
import sys

def run_marker_command():
    """
    Runs the marker CLI command with specified parameters.
    """
    command = [
        "marker",
        "utils\\data\\input",
        "--output_format", "markdown",
        "--output_dir", "utils\\data\\output",
        "--debug",
        "--paginate_output"
    ]
    
    try:
        print("Running command:")
        print(" ".join(command))
        print("-" * 50)
        
        # Run the command and capture output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print stdout
        if result.stdout:
            print(result.stdout)
        
        # Print stderr (debug info often goes here)
        if result.stderr:
            print(result.stderr)
            
        print("-" * 50)
        print("parsing completed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return 1
        
    except FileNotFoundError:
        print("Error: 'marker' command not found.")
        print("Make sure marker is installed and available in your PATH.")
        return 1

if __name__ == "__main__":
    sys.exit(run_marker_command())