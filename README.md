# interpreter-for-uni
This is my first approach playing with a parser. I created this as an assignment for my Lenguajes y Maquinas class at university (LyM).
```json
Language:
Grammar = {
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
        "balloons_chips": {
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
            "myballoons",
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
        "put": ["balloons_chips", "value_id"],
        "pick": ["balloons_chips", "value_id"],
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
```
