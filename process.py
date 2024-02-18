
import re
from lexer import print_error, are_there_known_errors

def inner_scope(tokens: dict):
    return tokens['scoped_variables'][-1]

def break_scope(tokens: dict):
    # First we remove the variables from the scope that are asigned to the global variables
    scope = tokens['scoped_variables'].pop()

    # We iterate over the variables in the scope and remove them from the global variables. tokens['variables'] is a dictionary
    # that stores the variables and their values.
    for variable in scope:
        tokens['variables'].pop(variable)

def create_scope(tokens: dict):
    tokens['scoped_variables'].append({})

# Functions to process the grammars

def try_cast_to_int(value):

    try:
        return int(value)
    except ValueError:
        return value
# Check functions

def is_active_scope(tokens: dict):
    if len(tokens['scoped_variables']) > 0:
        return True
    return False

def is_declaration(expression: str):
    """It receives an expression and returns True if the expression is a declaration and False otherwise.

    Keyword arguments:
    expression -- can be also part of an expression. It has to be a string.
    Return: a boolean that is True if the expression is a declaration and False otherwise.
    """

    return expression == 'defvar'

def is_reserved_word(word: str, grammar : dict) -> bool:
    return word in grammar['reserved_words']

def is_variable_declared(variable: str, tokens: dict) -> bool:

    if tokens['variables'].get(variable) is not None:
        return True
    else:
        local_approach = variable + "__local__"
        if tokens['variables'].get(local_approach) is not None:
            return True
    return False

def is_identifier(string: str) -> bool:
    return any(character.isalpha() for character in string)

def is_constant_c(expression: str, grammar: dict) -> bool:
    return expression in grammar['constant_c']

def is_constant_dir(expression: str, grammar: dict) -> bool:
    return expression in grammar['constant_dir']

def is_constant_rotate(expression: str, grammar: dict) -> bool:
    return expression in grammar['constant_rotate']

def is_constant(expression: str, grammar: dict) -> bool:
    return expression in grammar['constant']

def is_keyword(expression: str, grammar: dict) -> bool:
    # This mean is eaither a reserved word or any kind of constant
    if is_reserved_word(expression, grammar) or is_constant(expression, grammar) or is_constant_c(expression, grammar) or is_constant_dir(expression, grammar) or is_constant_rotate(expression, grammar) or is_ballons_chips(expression, grammar):
        return True

def is_ballons_chips(expression: str, grammar: dict) -> bool:
    return expression in grammar['ballons_chips']

# Process functions

def process_block(expression: list, tokens: dict, grammar: dict):
    if len(expression) > 1 and isinstance(expression[0], list):
        # We create a new scope
        create_scope(tokens)
        for exp in expression:
            process_line(exp, tokens, grammar)
        # We break the scope
        break_scope(tokens)

def process_loop(expression: list, tokens: dict, grammar: dict):
    if len(expression) != 3:
        tokens['known_errors'] = f'Error: loop has to have two arguments. You gave {len(expression) - 1} arguments.'
    else:
        process_condition(expression[1], tokens, grammar)
        process_block(expression[2], tokens, grammar)

def process_if(expression: list, tokens: dict, grammar: dict):

    # Checks if the expression has the correct number of arguments
    if len(expression) != 4:
        tokens['known_errors'] = f'Error: "if" has to have three arguments. You gave {len(expression) - 1} arguments.'
    else:
        process_condition(expression[1], tokens, grammar)
        process_block(expression[2], tokens, grammar)

def reassign_variable(expression: list, tokens: dict):
    if len(expression) != 3:
        tokens['known_errors'] = f'Error: "=" has to have two arguments. You gave {len(expression) - 1} arguments.'
    elif is_variable_declared(expression[1], tokens):
        expression[2] = try_cast_to_int(expression[2])
        tokens['variables'][expression[1]] = (expression[2], type(expression[2]))
    else:
        tokens['known_errors'] = f'Error: "{expression[1]}" is not declared. You cannot reassign a variable that is not declared.'

def create_variable(expression: list, tokens: dict, grammar: dict):

        variable = expression[1]

        if is_reserved_word(variable, grammar):
            tokens['known_errors'] = f'Error: "{variable}" is a reserved word. You cannot declare a variable with a reserved word.'
        elif is_variable_declared(variable, tokens):
            tokens['known_errors'] = f'Error: "{variable}" is already declared. You cannot redeclare a variable.'
        else:
            if is_identifier(variable):
                # We store the variable, and its value.
                # The values is a tuple of the value and its type.
                # Check if the value is a variable

                if is_variable_declared(expression[2], tokens):
                    expression[2] = tokens['variables'][expression[2]][0]

                expression[2] = try_cast_to_int(expression[2])
                tokens['variables'][variable] = (expression[2], type(expression[2]))
                if is_active_scope(tokens):
                    scope = inner_scope(tokens)
                    scope[variable] = expression[2]

def process_defvar(expression: list, tokens: dict, grammar: dict):
    if len(expression) != 3:
        tokens['known_errors'] = f'Error: "defvar" has to have two arguments. You gave {len(expression) - 1} arguments.'
    else:
        create_variable(expression, tokens,grammar)

def process_value_id(expression: list, tokens: dict, grammar: dict):

    # Check if the expression has a variable name
    if is_variable_declared(expression, tokens):

        if (expression + "__local__") in tokens['variables']:
            return

        var, vtype = tokens['variables'][expression]
        if vtype == int or var in grammar['constant']:
            return
        else:
            tokens['known_errors'] = f'Error: "{expression}" is not a number or an existing variable.'
    elif is_constant(expression, grammar):
        return
    else:
        var = try_cast_to_int(expression)
        if expression.isdigit():
            return
        else:
            tokens['known_errors'] = f'Error: "{var}" is not a number or an existing variable.'

def process_repeat(expression: list, tokens: dict, grammar: dict):
    if len(expression) != 3:
        tokens['known_errors'] = f'Error: "repeat" has to have two arguments. You gave {len(expression) - 1} arguments.'
    else:
        process_value_id(expression[1], tokens, grammar)
        process_block(expression[2], tokens, grammar)

def process_condition(expression: list, tokens: dict, grammar: dict):



    accepted_lengths = {
        "facing?": 2,
        "blocked?": 1,
        "can-put?": 3,
        "can-pick?": 3,
        "can-move?": 2,
        "isZero?": 2,
        "not": 2
    }

    def not_acceptable_argument(expression: str):
        tokens['known_errors'] = f'Error: "{expression}" is not an acceptable argument.'

    if expression[0] == "not":
        process_condition(expression[1], tokens, grammar)
    elif len(expression) != accepted_lengths[expression[0]]:
        print(expression)
        tokens['known_errors'] = f'Error: "{expression[0]}" has to have {accepted_lengths[expression[0]] - 1} arguments. You gave {len(expression) - 1} arguments.'
    else:
        if expression[0] == "facing?":
            if not is_constant_c(expression[1], grammar):
                not_acceptable_argument(expression[1])
        elif expression[0] == "can-put?":
            if is_ballons_chips(expression[1], grammar):
                process_value_id(expression[2], tokens, grammar)
            else:
                not_acceptable_argument(expression[1])
        elif expression[0] == "can-pick?":
            if is_ballons_chips(expression[1], grammar):
                process_value_id(expression[2], tokens, grammar)
        elif expression[0] == "can-move?":
            if not is_constant_c(expression[1], grammar):
                not_acceptable_argument(expression[1])
        elif expression[0] == "isZero?":
            process_value_id(expression[1], tokens, grammar)

def process_function_call(expression: list, tokens: dict, grammar: dict):

    function_name = expression[0]


    if len(expression) != len(tokens['functions'][function_name]) + 1:
        tokens['known_errors'] = f'Error: "{function_name}" has to have {len(tokens["functions"][function_name])} arguments. You gave {len(expression) - 1} arguments.'

    else:
        for arg in expression[1:]:
            process_value_id(arg, tokens, grammar)

def process_action(expression: list, tokens: dict, grammar: dict):

    accepted_lengths = {
        "move": 2,
        "skip": 2,
        "turn": 2,
        "face": 2,
        "put": 3,
        "pick": 3,
        "move-dir": 3,
        "run-dirs": "lots",
        "move-face": 3,
    }

    def process_move(expression: list):
        process_value_id(expression[1], tokens, grammar)

    def process_skip(expression: list):
        process_value_id(expression[1], tokens, grammar)

    def process_turn(expression: list):
        if not is_constant_rotate(expression[1], grammar):
            tokens['known_errors'] = f'Error: "{expression[1]}" is not an acceptable argument for "turn".'

    def process_face(expression: list):
        if not is_constant_c(expression[1], grammar):
            tokens['known_errors'] = f'Error: "{expression[1]}" is not an acceptable argument for "face".'

    def process_put(expression: list):
        if not is_ballons_chips(expression[1], grammar):
            tokens['known_errors'] = f'Error: "{expression[1]}" is not an acceptable argument for "put".'
        else:
            process_value_id(expression[2], tokens, grammar)

    def process_pick(expression: list):
        if not is_ballons_chips(expression[1], grammar):
            tokens['known_errors'] = f'Error: "{expression[1]}" is not an acceptable argument for "pick".'
        else:
            process_value_id(expression[2], tokens, grammar)


    def process_move_dir(expression: list):
        process_value_id(expression[1], tokens, grammar)
        if not is_constant_dir(expression[2], grammar):
            tokens['known_errors'] = f'Error: "{expression[2]}" is not an acceptable argument for "move-dir".'

    def process_move_face(expression: list):
        process_value_id(expression[1], tokens, grammar)
        if not is_constant_c(expression[2], grammar):
            tokens['known_errors'] = f'Error: "{expression[2]}" is not an acceptable argument for "move-face".'

    def process_run_dirs(expression: list):
        if len(expression) == 1:
            tokens['known_errors'] = 'Error: "run-dirs" has to have at least one argument.'
        if not all(is_constant_dir(arg, grammar) for arg in expression[1:]):
            tokens['known_errors'] = 'Error: "run-dirs" only accepts directions as arguments.'

    if expression[0] == "run-dirs":
        process_run_dirs(expression)
    elif len(expression) != accepted_lengths[expression[0]]:
        tokens['known_errors'] = f'Error: "{expression[0]}" has to have {accepted_lengths[expression[0]] - 1} arguments. You gave {len(expression) - 1} arguments.'
    else:
        if expression[0] == "turn":
            process_turn(expression)
        elif expression[0] == "face":
            process_face(expression)
        elif expression[0] == "put":
            process_put(expression)
        elif expression[0] == "pick":
            process_pick(expression)
        elif expression[0] == "move-dir":
            process_move_dir(expression)
        elif expression[0] == "move-face":
            process_move_face(expression)
        elif expression[0] == "move":
            process_move(expression)
        elif expression[0] == "skip":
            process_skip(expression)

def process_line(expression, tokens: dict, grammar: dict):
    if expression[0] in grammar['action']:
        process_action(expression, tokens, grammar)
    if expression[0] in grammar['reserved_words']:
        process(expression, tokens)
    else:
        tokens['known_errors'] = f'Error: "{expression[0]}" command could not be recognized.'

def process_defun(expression: list, tokens: dict, grammar: dict):
    if len(expression) > 3:
        if is_identifier(expression[1]):
            tokens['functions'][expression[1]] = expression[2]

            if expression[2] != []:
                # We create a new scope for the function

                create_scope(tokens)
                scope = inner_scope(tokens)
                for arg in expression[2]:

                    if is_reserved_word(arg, grammar):
                        tokens['known_errors'] = f'Error: "{arg}" is a reserved word. You cannot declare a function variable with a reserved word.'

                    var_name = arg + "__local__"
                    create_variable(["None", var_name, "None__local__"], tokens, grammar)

                # Now we process the rest of the function as a block
                block = expression[3:]
                process_block(block, tokens, grammar)
                # We break the scope
                break_scope(tokens)
        else:
            tokens['known_errors'] = f'Error: "{expression[1]}" is not a valid function name.'
    else:
        tokens['known_errors'] = f'Error: "defun" has to have at least three arguments. You gave {len(expression) - 1} arguments.'

def process(expression: str, tokens: dict):
    grammar = {
        # value_id means it accepts either a value or an id and has to be an int
        "reserved_words": {
            "defvar",
            "=",
            "move",
            "skip",
            "turn",
            "face",
            "put",
            "pick",
            "move-dir",
            "run-dirs",
            "move-face",
            "null",
            "if",
            "loop",
            "repeat",
            "defun",
            "not",
        },
        "constant_rotate": {
            ":left",
            ":right",
            ":around",
            "None__local__"
        },
        "constant_c": {
            ":north",
            ":south",
            ":east",
            ":west",
            "None__local__"
        },
        "ballons_chips": {
            ":balloons",
            ":chips",
            "None__local__"
        },
        "constant_dir": {
          ":front",
          ":right",
          ":left",
          ":back",
          "None__local__"
        },
        "constant": {
            "dim",
            "myxpos",
            "myypos",
            "mychips",
            "myballons",
            "balloonshere",
            "chipshere",
            "spaces",
        },
        "condition" : {
            "facing?",
            "blocked?",
            "can-put?",
            "can-pick?",
            "can-move?",
            "iszero?",
            "not"
        },
        "action": {
            "move",
            "skip",
            "turn",
            "face",
            "put",
            "pick",
            "move-dir",
            "run-dirs",
            "move-face",
        },

        "defvar": ["id","value_id"],
        "=": ["id", "value_id"],
        "move": ["value_id"],
        "skip": ["value_id"],
        "turn": ["constant_rotate"],
        "face": ["constant_c"],
        "put": ["ballons_chips", "value_id"],
        "pick": ["ballons_chips", "value_id"],
        "move_dir": ["value_id", "constant_dir"],
        "run-dirs": [],
        "move-face": ["value_id", "constant_c"],
        "null": [],
        "if": ["condition", "action", "action"],
        "loop": ["condition", "action"],
        "repeat": ["value_id", "action"],
        "defun": ["id_function", [], "action"],
        "id_function": [],

    }


    # Organizes the expressions for the tokenizer
    if type(expression) is str:
        expression = expression.split(" ")

    if isinstance(expression[0], list):
        expression = expression[0]
    if expression == "":
        return
    try:
        if expression[0][0] == "(":
            expression[0] = expression[0][1:]
        if expression[-1][-1] == ")":
            expression[-1] = expression[-1][:-1]
        if expression[0] == "":
            expression = expression[1:]
    except IndexError:
        print_error("Error: There is an error in the expression.")
        return

    if are_there_known_errors(tokens):
        print_error(tokens['known_errors'])
    if is_declaration(expression[0]):
        process_defvar(expression, tokens, grammar)
    elif expression[0] == "null":
        return
    elif expression[0] == "if":
        process_if(expression, tokens, grammar)
    elif expression[0] == "loop":
        process_loop(expression, tokens, grammar)
    elif expression[0] == "repeat":
        process_repeat(expression, tokens, grammar)
    elif expression[0] == "=":
        reassign_variable(expression, tokens)
    elif expression[0] == "defun":
        process_defun(expression, tokens, grammar)
    elif expression[0] in grammar["condition"]:
        process_condition(expression, tokens, grammar)
    elif expression[0] in grammar['action']:
        process_action(expression, tokens, grammar)

    elif is_keyword(expression[0], grammar):
        return
    elif expression[0] in tokens['functions']:
        process_function_call(expression, tokens, grammar)
    else:
        print_error(f'Error: "{expression[0]}" command could not be recognized.')
