# VibeLang Language Guide

This guide explains the practical syntax of VibeLang so you can write programs correctly before compiling.

## 1) Program Basics

- VibeLang is an English-like language.
- Every statement should end with `;`.
- Variables should be declared before they are used.

## 2) Variable Declaration

Declare and optionally initialize a variable:

```vibelang
declare variable marks = 75;
declare variable total;
```

## 3) Assignment

Assign a value or expression to a variable:

```vibelang
total = marks + 10;
```

## 4) Print Statement

Print numbers, variables, or text:

```vibelang
print total;
print "hello";
```

## 5) Arithmetic

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

## 6) Conditions

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

## 7) While Loop

Use loops with `while ... do ... end while;`:

```vibelang
declare variable counter = 1;
while counter is less than or equal to 5 do
    print counter;
    counter = counter + 1;
end while;
```

## 8) Full Example Program

```vibelang
declare variable counter = 1;
declare variable limit = 5;
while counter is less than or equal to limit do
    print counter;
    counter = counter + 1;
end while;
if counter is greater than limit then
    print "done";
end if;
```

## 9) Common Mistakes

- Missing semicolon at the end of a statement
- Using a variable before declaration
- Forgetting `end if;` or `end while;`
- Using unsupported phrasing in conditions

## 10) Learning Workflow

1. Start with small declarations and prints.
2. Add one condition or loop.
3. Compile and inspect Tokens, Status, TAC, and Errors.
4. Use AI tools to explain code and errors when enabled.
