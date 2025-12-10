BREAK_WORDS = [
    "the code is",
    "now the code",
    "code part",
    "here is the code",
    "the function is",
    "function called",
    "the logic is as follows",
    "steps are",
    "implementation is",
    "example",
    "for example",
    "sample code",
    "test case",
    "run this",
    "execute this",
    "output will be",
    "result will be",
    "program is",
    "script is",
    "inside the function",
    "now write a function",
    "i want a function",
    "the function name is",
]

CODE_INTENT_WORDS = {
    # Functions / methods
    "function", "method", "procedure", "routine", "sub routine", "sub program",
    "create a function", "make a function", "start a function",
    "define a function", "write a function", "function called", "function named",
    "method called", "method named",

    # Variables / data
    "variable", "value", "set value", "set variable", "store value",
    "assign value", "initialize variable", "declare variable",
    "list", "array", "dictionary", "map", "key value pair",

    # Control flow
    "if condition", "if statement", "check if", "otherwise", "else condition",
    "for loop", "loop from", "loop through", "repeat for each", "repeat",
    "iterate", "go through each", "while loop", "loop until", "do until",
    
    # Logical
    "equals", "equal to", "not equal", "greater than", "less than",
    "compare", "check whether", "condition true", "condition false",

    # I/O
    "return", "output", "print", "display", "show message", "take input",
    "ask user", "user enters", "prompt user",

    # Structure
    "start program", "end program", "inside the function", "inside the loop",
    "outside the loop", "before that", "after that", "next step", "step one",
    "step two", "then do", "do this then that", "finally",

    # DS Operations
    "add to list", "remove from list", "append", "push value", "pop value",
    "sort list", "search list", "find item", "count items",

    # OOP
    "class", "object", "instance", "create object", "constructor",
    "attribute", "property", "field", "inherit", "extend", "override",

    # Errors
    "try block", "catch block", "handle error", "on error", "throw error",

    # Algorithmic
    "algorithm", "workflow", "Calculate", "compute", "determine",
    "evaluate", "process data", "convert value"
}

IGNORE_CALLED_NAMES = {
    "if", "for", "while", "switch", "catch", "else", "elif", "return",
    "print", "console", "function"
}
