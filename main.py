from lexer import lexer
import sys

def process_file(file_path):
    with open(file_path, 'r') as file:
        contents = file.read()
        print(contents)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        lexer(file_path)
    else:
        print("\033[33mPlease provide a file path as an argument.\033[0m")
