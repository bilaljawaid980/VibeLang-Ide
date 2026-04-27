# Project Abstract

The AI-Assisted VibeLang Compiler is a semester project that demonstrates the main phases of compiler construction using a custom English-like programming language. VibeLang uses beginner-friendly syntax such as `declare variable`, `if ... then`, and `while ... do`, making compiler concepts easier to understand for students.

The system is implemented in Python and includes lexical analysis, recursive-descent parsing, semantic analysis with a symbol table, and three-address code generation. A Flask-based frontend provides a simple interactive environment where users can enter VibeLang code and inspect tokens, compiler status, errors, and generated TAC.

To add a modern learning layer without replacing rule-based compilation, the project also includes optional AI assistance through the Vercel AI Gateway. When configured, the AI can explain compiler errors, describe what a VibeLang program does, suggest fixes, and convert simple English instructions into VibeLang syntax.
