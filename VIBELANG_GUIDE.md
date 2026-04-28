# VibeLang v2 Language Guide

VibeLang v2 is the expanded version of the language used in this project. It now supports strings, function definitions, function calls, and return values, while keeping the English-like syntax easy to read.

## 1) Program Basics

- Every statement ends with `;`.
- Declare variables before using them.
- Functions are defined at the top level.
- Use `print` to show values.

## 2) Variables

Declare a variable with or without an initial value:

```vibelang
declare variable marks = 75;
declare variable message;
```

Assign later:

```vibelang
message = "Ready";
```

## 3) Strings

Strings are written in double quotes and can be stored in variables, printed, returned, and joined with `+`.

```vibelang
declare variable title = "Vibe";
title = title + "Lang";
print title;
```

## 4) Arithmetic

Supported arithmetic operators:

- `+`
- `-`
- `*`
- `/`

Example:

```vibelang
declare variable a = 10;
declare variable b = 5;
declare variable c;
c = a + b * 2;
print c;
```

## 5) Conditions

VibeLang conditions are written in English-like form.

Common comparisons:

- `is greater than`
- `is less than`
- `is greater than or equal to`
- `is less than or equal to`
- `is equal to`
- `is not equal to`

Example:

```vibelang
if marks is greater than 50 then
    print "pass";
else
    print "fail";
end if;
```

## 6) While Loop

Use loops with `while ... do ... end while;`:

```vibelang
declare variable counter = 1;
while counter is less than or equal to 5 do
    print counter;
    counter = counter + 1;
end while;
```

## 7) Functions

Define reusable code blocks using `function ... then ... end function;`.

Syntax:

```vibelang
function greet(name) then
    return "Hello, " + name;
end function;
```

Call the function like any expression:

```vibelang
declare variable message = greet("Ali");
print message;
```

Rules:

- Function names must be valid identifiers.
- Parameters are comma-separated.
- Every function must return a value.
- `return` can return a number or a string.

## 8) Full Example Program

```vibelang
function add(a, b) then
    return a + b;
end function;

declare variable counter = 1;
declare variable limit = 5;
declare variable total = add(counter, limit);

while counter is less than or equal to limit do
    print counter;
    counter = counter + 1;
end while;

if total is greater than 0 then
    print "done";
end if;
```

## 9) Common Mistakes

- Missing semicolon at the end of a statement.
- Using a variable before declaration or initialization.
- Forgetting `end if;`, `end while;`, or `end function;`.
- Using a function without the right number of arguments.
- Returning no value from a function.

## 10) Learning Workflow

1. Start with declarations, prints, and strings.
2. Add one condition or loop.
3. Define a small function and call it.
4. Compile and inspect Tokens, Status, TAC, Result, and Errors.
5. Use AI tools to explain code and errors when enabled.
