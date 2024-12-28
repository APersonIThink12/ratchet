import sys
import os
import tempfile
import marshal
import time

# Custom print function
def custom_print(*args):
    print(" ".join(str(arg) for arg in args))

# Function to translate Ratchet code to custom bytecode
def translate_ratchet_to_python(ratchet_code):
    python_code = []
    
    for line in ratchet_code.splitlines():
        line = line.strip()
        
        if line.startswith("print "):  # Handle print statement
            python_code.append(f"custom_print({line[6:]})")
        
        elif line.startswith("let "):  # Handle variable assignment
            # Syntax: let <var_name> = <value>
            parts = line[4:].split("=")
            var_name = parts[0].strip()
            value = parts[1].strip()
            python_code.append(f"{var_name} = {value}")
        
        else:
            # If the line doesn't match any recognized pattern, ignore or add a pass
            pass
    
    return "\n".join(python_code)

def write_rabc_bytecode(bytecode, file_path):
    # Write custom bytecode to .rabc file
    with open(file_path, 'wb') as f:
        # Custom header to identify as Ratchet bytecode
        header = b'RABC'  # 'RABC' stands for Ratchet Bytecode
        timestamp = int(time.time())
        f.write(header)  # Write header
        f.write(timestamp.to_bytes(4, byteorder='little'))  # Write timestamp
        marshal.dump(bytecode, f)  # Write bytecode

def read_rabc_bytecode(file_path):
    # Read custom bytecode from .rabc file
    with open(file_path, 'rb') as f:
        # Verify the header
        header = f.read(4)
        if header != b'RABC':
            raise ValueError(f"Invalid bytecode file: {file_path}")
        
        # Skip timestamp (4 bytes)
        f.read(4)
        
        # Read the bytecode
        bytecode = marshal.load(f)
        
    return bytecode

def run_ratchet_from_file(file):
    try:
        # Read the Ratchet code from the file
        with open(file, "r") as f:
            ratchet_code = f.read()

        # Translate the Ratchet code to Python code
        python_code = translate_ratchet_to_python(ratchet_code)

        # Compile the translated Python code into bytecode
        bytecode = compile(python_code, '<string>', 'exec')

        # Create a temporary file path for the .rabc file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rabc') as tmp_file:
            tmp_filename = tmp_file.name

        # Write the bytecode to the .rabc file with custom header
        write_rabc_bytecode(bytecode, tmp_filename)

        # Print confirmation of bytecode file creation
        print(f"Bytecode file created: {tmp_filename}")

        # Read and execute the custom bytecode
        bytecode = read_rabc_bytecode(tmp_filename)

        # Create a custom global environment with custom_print
        custom_globals = {
            "custom_print": custom_print,  # Make sure custom_print is in the global scope
            "__name__": "__main__"
        }

        # Execute the bytecode from the custom file
        exec(bytecode, custom_globals)  # Pass custom_globals explicitly

        # Delete the temporary bytecode file after execution
        os.remove(tmp_filename)

    except Exception as e:
        print(f"Execution failed: {e}")

# Ensure the script is run with a filename as argument
if len(sys.argv) != 2:
    print("Usage: ratchet <filename.ra>")
    sys.exit(1)

# Get the filename argument
filename = sys.argv[1]

# Check if the file exists
if not os.path.exists(filename):
    print(f"Error: The file '{filename}' does not exist.")
    sys.exit(1)

# Run the Ratchet code
run_ratchet_from_file(filename)
