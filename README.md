# AI-Assisted VibeLang Compiler

An educational compiler project for **VibeLang**, a beginner-friendly English-like programming language. The project demonstrates lexical analysis, parsing, semantic analysis, and three-address code generation through a Python + Flask web app. Optional AI features use the **Vercel AI Gateway** through an OpenAI-compatible API client.

## Features

- Rule-based VibeLang compiler pipeline
- Beginner-friendly errors with line and column information
- Three-address code generation for arithmetic, `if`, `if-else`, and `while`
- Web UI for source input and compiler output
- Optional AI help for explaining code, suggesting fixes, and generating VibeLang from English
- Example `.vibe` programs and `pytest` coverage for core phases

## Language Documentation

For a clear beginner reference of syntax and examples, see **[VIBELANG_GUIDE.md](VIBELANG_GUIDE.md)**.

## VibeLang Syntax Examples

```vibelang
declare variable marks = 75;
if marks is greater than 50 then
    print "pass";
else
    print "fail";
end if;
```

```vibelang
declare variable counter = 1;
while counter is less than or equal to 5 do
    print counter;
    counter = counter + 1;
end while;
```

## Folder Structure

```text
compiler/
ai/
templates/
static/
examples/
tests/
app.py
requirements.txt
```

## Setup

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```powershell
python app.py
```

Open `http://127.0.0.1:5000`.

## AI Configuration

Create a `.env` file from `.env.example` and provide your Vercel AI Gateway values:

```env
AI_GATEWAY_API_KEY=your_api_key_here
AI_GATEWAY_BASE_URL=https://ai-gateway.vercel.sh/v1
AI_MODEL=openai/gpt-4.1-nano
FLASK_ENV=development
PORT=5000
```

If the API key is missing, all compiler features still work and AI routes are disabled gracefully.

The default AI model is `openai/gpt-4.1-nano`, which OpenAI currently documents as the cheapest and fastest GPT-4.1 API model, and Vercel AI Gateway expects models in `provider/model` format.

## Sample Compiler Output

Input:

```vibelang
declare variable a = 10;
declare variable b = 20;
declare variable sum;
sum = a + b * 2;
```

Output TAC:

```text
a = 10
b = 20
t1 = b * 2
t2 = a + t1
sum = t2
```

## Compiler Phases

1. Lexer turns source code into tokens.
2. Parser builds an AST for declarations, assignments, print statements, conditionals, and loops.
3. Semantic analysis validates declarations and numeric expression rules.
4. TAC generation emits three-address code using temporary variables and labels.

## Testing

```powershell
python -m pytest
```

## Deploy Live For Free (Render)

This repo is now deployment-ready for Render with `render.yaml` and `Procfile`.

### 1. Push project to GitHub

```powershell
git init
git add .
git commit -m "deploy-ready"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### 2. Create free web service on Render

1. Open Render dashboard and choose **New +** -> **Blueprint**.
2. Connect your GitHub repo.
3. Render will detect `render.yaml` automatically.
4. Deploy.

### 3. Add environment variables in Render

Set these in Render service settings:

- `AI_GATEWAY_API_KEY` = your key (optional if you only need compiler features)
- `AI_GATEWAY_BASE_URL` = `https://ai-gateway.vercel.sh/v1`
- `AI_MODEL` = `openai/gpt-4.1-nano`
- `FLASK_ENV` = `production`

After deploy, Render gives you a public URL like:

`https://vibelang-compiler.onrender.com`

Note: Free Render services can sleep after inactivity and may take some seconds to wake up.
