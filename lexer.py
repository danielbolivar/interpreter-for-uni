
import sys

def print_error(error: str):
    print("\033[91mError: Could not process the file. There are existing errors.\033[0m")
    if not isinstance(error, dict):
        print("\033[91m" + error + "\033[0m")
    sys.exit()

def are_there_known_errors(tokens: dict) -> bool:
    return len(tokens['known_errors']) > 0

def handle_nested_parenthesis(text: str) -> list:

    # Si encuentra una keyword entonces va a poner un token hasta que encuentre un parentesis (ubicacion anterior)
    # if it finds a keyword it is going to put a token until it finds a parenthesis (one position before the parenthesis)

    result = []
    current_word = ""
    open_count = 0

    for i, char in enumerate(text):
        if char == '(':
            open_count += 1
            if open_count == 1:  # Start of a new inner expression or word
                if current_word:
                    result.append(current_word)
                    current_word = ""
            else:  # Already within a word
                current_word += char
        elif char == ')':
            open_count -= 1
            if open_count == 0:  # End of an inner expression
                result.append(handle_nested_parenthesis(current_word))  # Process inner expression
                current_word = ""
            else:
                current_word += char
        elif char == ' ' and open_count == 0:  # Word separator outside parenthesis
            if current_word:
                result.append(current_word)
                current_word = ""
        else:
            current_word += char

    if current_word:  # Add any remaining part
        result.append(current_word)

    return result




def process_text(text: str, tokens: dict):
    """It receives a text and returns a list of the expressions that composes the text.
    The expressions are separated by parenthesis.

    Keyword arguments:
    expression -- can be also part of an expression. It has to be a string.
    Return: an array of strings that are the elements of the expression.
    """

    expressions = []

    current_expression = ""
    open_parenthesis = 0
    close_parenthesis = 0

    # We iterate through the text and separate the expressions. We do this by counting the parenthesis.
    # We also remove doble spaces
    for character in text:

        character = character.lower()

        if open_parenthesis == close_parenthesis and open_parenthesis != 0 and close_parenthesis != 0:
            # Check if there are more than one expression in the same line if
            # We want to separate the expression into a bunch of expressions
            if close_parenthesis > 1: # If close_parenthesis > 1 so will open_parethesis. We have to separate the expressions

                expressions.append(handle_nested_parenthesis(current_expression))
            else:
                expressions.append(current_expression)
            current_expression = ""
            open_parenthesis = 0
            close_parenthesis = 0
        elif character != '\n' and character != '\t' and character != '\r' and character != '\v' and character != '\f' and character :
            # Removes the double spaces
            if character == ' ' and current_expression[-1] == ' ':
                continue
            else:
                current_expression += character

        # If there where nested parenthesis we have to
        # Add the first item in the array a parenthesis and the last item a parenthesis

        if character == '(':
            open_parenthesis += 1
        elif character == ')':
            close_parenthesis += 1

   # if expressions[0] in tokens['reserved_words']:

    # Check if there are any open parenthesis
    if open_parenthesis != close_parenthesis:
        # find the last open parenthesis in the expressions array and return its position
        tokens['known_errors'] = 'Error: There are open statements. You have to close them.'

    return expressions

# Check the type of the expression


def tokenizer(expression: list, tokens: dict):
    from process import process

    process(expression, tokens)

def lexer(file_path: str):

    # Read the file
    try:
        with open(file_path, 'r') as file:
            text = file.read()
    except FileNotFoundError:
        print("\033[91mError: The file does not exist. Please check the file path and try again.\033[0m")
        sys.exit()


    # We create and object that will store the tokens, their values and their types.

    tokens = {
        'known_errors': {}, # This will store the known errors
        'variables': {}, # This will store the variables and their values
        'functions': {}, # This will store the functions, their arguments and their body.
        'scoped_variables': [] , # This will store the variables and their on scope (only variables that are inside a function (works as a stack)
    }
    # We separate the text into expressions
    expressions = process_text(text, tokens)

    # if there is a blank text
    if len(expressions) == 0:
        tokens['known_errors'] = 'Error: The file is empty. Did you forget to write something?'
        print_error(tokens['known_errors'])

    # Then we separate the expressions into tokens
    # The expressions are passed in lower case to the tokenizer
    try:
        for expression in expressions:
            if are_there_known_errors(tokens):
                print_error(tokens['known_errors'])
                sys.exit()
            tokenizer(expression, tokens)
        print("\033[92mSuccess: No errors found. The file was processed successfully.\033[0m")
    except Exception as _: # If there is an error we print the error
        print("\033[91mFatal: An error occurred while processing the file. Please check the file and try again.\033[0m")





