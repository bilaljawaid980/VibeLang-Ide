const sourceCodeEl = document.getElementById("source-code");
const runBtn = document.getElementById("run-btn");
const compileIndicatorEl = document.getElementById("compile-indicator");
const terminalOutputEl = document.getElementById("terminal-output");
const terminalTabs = document.querySelectorAll(".term-tab");
const docsTabs = document.querySelectorAll(".docs-tab");
const docPanes = document.querySelectorAll(".doc-pane");
const insertDocSnippetButtons = document.querySelectorAll(".insert-doc-snippet");

const fileListEl = document.getElementById("file-list");
const newFileNameEl = document.getElementById("new-file-name");
const createFileBtn = document.getElementById("create-file-btn");
const activeFileNameEl = document.getElementById("active-file-name");

const aiTabs = document.querySelectorAll(".ai-tab");
const aiPanes = document.querySelectorAll(".ai-pane");
const aiOutputEl = document.getElementById("ai-output");
const aiStatusEl = document.getElementById("ai-status");
const promptEl = document.getElementById("prompt-text");
const promptChips = document.querySelectorAll(".prompt-chip");

const explainCodeBtn = document.getElementById("explain-code-btn");
const explainErrorBtn = document.getElementById("explain-error-btn");
const suggestFixBtn = document.getElementById("suggest-fix-btn");
const generateBtn = document.getElementById("generate-btn");

const STORAGE_KEY = "vibelang.ide.files.v1";
const aiEnabled = document.body.dataset.aiEnabled === "true";

let files = loadFiles();
let activeFile = Object.keys(files)[0] || "main.vibe";
let currentView = "all";
let lastCompile = null;

renderFileList();
loadFileIntoEditor(activeFile);
renderTerminal("all");

runBtn.addEventListener("click", compileSource);
createFileBtn.addEventListener("click", createFile);
sourceCodeEl.addEventListener("input", persistCurrentFile);

terminalTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        currentView = tab.dataset.view;
        terminalTabs.forEach((item) => item.classList.remove("active"));
        tab.classList.add("active");
        renderTerminal(currentView);
    });
});

aiTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        const selected = tab.dataset.aiTab;
        aiTabs.forEach((item) => item.classList.remove("active"));
        aiPanes.forEach((pane) => pane.classList.remove("active"));
        tab.classList.add("active");
        document.querySelector(`[data-ai-pane="${selected}"]`)?.classList.add("active");
    });
});

docsTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        const selected = tab.dataset.doc;
        docsTabs.forEach((item) => item.classList.remove("active"));
        docPanes.forEach((pane) => pane.classList.remove("active"));
        tab.classList.add("active");
        document.querySelector(`[data-doc-pane="${selected}"]`)?.classList.add("active");
    });
});

insertDocSnippetButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const snippet = button.dataset.snippet || "";
        sourceCodeEl.value = snippet;
        persistCurrentFile();
        sourceCodeEl.focus();
        terminalOutputEl.textContent = "[DOCS]\nSnippet inserted into active file.";
    });
});

promptChips.forEach((chip) => {
    chip.addEventListener("click", () => {
        const promptText = chip.dataset.prompt || "";
        promptEl.value = promptText;
        promptEl.focus();
        setAiStatus("Prompt loaded. Click Generate VibeLang Code.", "");
    });
});

explainCodeBtn.addEventListener("click", explainCode);
explainErrorBtn.addEventListener("click", explainError);
suggestFixBtn.addEventListener("click", suggestFix);
generateBtn.addEventListener("click", generateCode);

async function compileSource() {
    persistCurrentFile();
    setCompileIndicator("Running...", "");
    const result = await postJson("/compile", { source_code: sourceCodeEl.value });
    if (!result) {
        setCompileIndicator("Error", "err");
        return;
    }

    lastCompile = result;
    if (result.success) {
        setCompileIndicator("Success", "ok");
    } else {
        setCompileIndicator("Failed", "err");
    }
    renderTerminal(currentView);
}

async function explainCode() {
    setAiStatus("Analyzing code...", "");
    const compileResult = await postJson("/compile", { source_code: sourceCodeEl.value }, { reportToTerminal: false });
    if (!compileResult) {
        aiOutputEl.textContent = explainCodeFallback(sourceCodeEl.value, []);
        setAiStatus("AI request failed, fallback explanation shown.", "err");
        return;
    }

    if (!compileResult.success) {
        aiOutputEl.textContent = "Run successful code first, then ask for explanation.";
        setAiStatus("Compilation must succeed before explanation.", "err");
        return;
    }

    if (!aiEnabled) {
        aiOutputEl.textContent = explainCodeFallback(sourceCodeEl.value, compileResult.tac || []);
        setAiStatus("AI key not configured. Fallback explanation shown.", "err");
        return;
    }

    const result = await postJson("/ai/explain-code", {
        source_code: sourceCodeEl.value,
        tac: compileResult.tac,
    }, { reportToTerminal: false });
    if (result?.success) {
        aiOutputEl.textContent = result.text;
        setAiStatus("Explanation generated successfully.", "ok");
    } else {
        aiOutputEl.textContent = explainCodeFallback(sourceCodeEl.value, compileResult.tac || []);
        setAiStatus("AI response unavailable. Fallback explanation shown.", "err");
    }
}

async function explainError() {
    setAiStatus("Checking for errors...", "");
    const compileResult = await postJson("/compile", { source_code: sourceCodeEl.value }, { reportToTerminal: false });
    if (!compileResult) {
        setAiStatus("Could not compile source for error explanation.", "err");
        return;
    }

    if (compileResult.success) {
        aiOutputEl.textContent = "No errors found. Run code with an issue to explain an error.";
        setAiStatus("No error present to explain.", "");
        return;
    }

    const [firstError] = compileResult.errors || [];
    if (!firstError) {
        aiOutputEl.textContent = "Compilation failed, but no structured error details were returned.";
        setAiStatus("No error details available.", "err");
        return;
    }

    if (!aiEnabled) {
        aiOutputEl.textContent = explainErrorFallback(firstError);
        setAiStatus("AI key not configured. Fallback error help shown.", "err");
        return;
    }

    const result = await postJson("/ai/explain-error", {
        source_code: sourceCodeEl.value,
        error: firstError,
    }, { reportToTerminal: false });
    if (result?.success) {
        aiOutputEl.textContent = result.text;
        setAiStatus("Error explanation generated.", "ok");
    } else {
        aiOutputEl.textContent = explainErrorFallback(firstError);
        setAiStatus("AI response unavailable. Fallback error help shown.", "err");
    }
}

async function suggestFix() {
    setAiStatus("Preparing fix suggestions...", "");
    const compileResult = await postJson("/compile", { source_code: sourceCodeEl.value }, { reportToTerminal: false });
    if (!compileResult) {
        setAiStatus("Could not compile source for fix suggestions.", "err");
        return;
    }

    if (compileResult.success) {
        aiOutputEl.textContent = "No errors found. Nothing to fix right now.";
        setAiStatus("No fixes needed.", "ok");
        return;
    }

    if (!aiEnabled) {
        aiOutputEl.textContent = suggestFixFallback(sourceCodeEl.value, compileResult.errors || []);
        setAiStatus("AI key not configured. Fallback fix suggestions shown.", "err");
        return;
    }

    const result = await postJson("/ai/suggest-fix", {
        source_code: sourceCodeEl.value,
        errors: compileResult.errors || [],
    }, { reportToTerminal: false });
    if (result?.success) {
        aiOutputEl.textContent = result.text;
        setAiStatus("Fix suggestions generated.", "ok");
    } else {
        aiOutputEl.textContent = suggestFixFallback(sourceCodeEl.value, compileResult.errors || []);
        setAiStatus("AI response unavailable. Fallback fix suggestions shown.", "err");
    }
}

async function generateCode() {
    const prompt = promptEl.value.trim();
    if (!prompt) {
        aiOutputEl.textContent = "Describe what code you want to generate first.";
        setAiStatus("Prompt required for code generation.", "err");
        return;
    }

    setAiStatus("Generating VibeLang code...", "");

    if (!aiEnabled) {
        sourceCodeEl.value = generateCodeFallback(prompt);
        persistCurrentFile();
        aiOutputEl.textContent = "AI key not configured. Generated code using local template fallback.";
        setAiStatus("Fallback code generated.", "err");
        return;
    }

    const result = await postJson("/ai/generate-code", { prompt }, { reportToTerminal: false });
    if (result?.success) {
        sourceCodeEl.value = result.text;
        persistCurrentFile();
        aiOutputEl.textContent = "Generated code inserted into current file.";
        setAiStatus("Code generated successfully.", "ok");
    } else {
        sourceCodeEl.value = generateCodeFallback(prompt);
        persistCurrentFile();
        aiOutputEl.textContent = "AI request failed. Generated code using local template fallback.";
        setAiStatus("AI unavailable. Fallback code generated.", "err");
    }
}

function renderTerminal(view) {
    if (!lastCompile) {
        terminalOutputEl.textContent = "Click Run to compile and execute.";
        return;
    }

    const statusText = lastCompile.success ? "Syntax: Valid\nSemantic: Valid" : "Compilation failed.";
    const tokens = (lastCompile.token_display || []).join("\n") || "No tokens.";
    const tac = (lastCompile.tac || []).join("\n") || "No TAC generated.";
    const result = lastCompile.success
        ? (lastCompile.runtime_output || []).join("\n") || "Program executed successfully with no print output."
        : "Execution skipped because compilation failed.";
    const errors = formatErrors(lastCompile.errors || []);

    const sections = {
        all: [
            "[STATUS]",
            statusText,
            "",
            "[RESULT]",
            result,
            "",
            "[ERRORS]",
            errors,
            "",
            "[TOKENS]",
            tokens,
            "",
            "[TAC]",
            tac,
        ].join("\n"),
        result,
        errors,
        tokens,
        tac,
    };

    terminalOutputEl.textContent = sections[view] || sections.all;
}

function loadFiles() {
    const fallback = {
        "main.vibe": sourceCodeEl.value,
    };
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) {
            return fallback;
        }
        const parsed = JSON.parse(raw);
        if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
            return fallback;
        }
        const names = Object.keys(parsed);
        if (!names.length) {
            return fallback;
        }
        return parsed;
    } catch (_error) {
        return fallback;
    }
}

function saveFiles() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(files));
}

function createFile() {
    let name = (newFileNameEl.value || "").trim();
    if (!name) {
        newFileNameEl.focus();
        return;
    }
    if (!name.endsWith(".vibe")) {
        name = `${name}.vibe`;
    }
    if (files[name]) {
        activeFile = name;
        loadFileIntoEditor(activeFile);
        renderFileList();
        newFileNameEl.value = "";
        return;
    }
    files[name] = "";
    activeFile = name;
    saveFiles();
    renderFileList();
    loadFileIntoEditor(activeFile);
    newFileNameEl.value = "";
}

function renderFileList() {
    fileListEl.innerHTML = "";
    Object.keys(files).forEach((fileName) => {
        const li = document.createElement("li");
        const button = document.createElement("button");
        button.type = "button";
        button.className = "file-item";
        if (fileName === activeFile) {
            button.classList.add("active");
        }
        button.textContent = fileName;
        button.addEventListener("click", () => {
            persistCurrentFile();
            activeFile = fileName;
            loadFileIntoEditor(fileName);
            renderFileList();
        });
        li.appendChild(button);
        fileListEl.appendChild(li);
    });
}

function loadFileIntoEditor(fileName) {
    sourceCodeEl.value = files[fileName] || "";
    activeFileNameEl.textContent = fileName;
}

function persistCurrentFile() {
    if (!activeFile) {
        return;
    }
    files[activeFile] = sourceCodeEl.value;
    saveFiles();
}

function setCompileIndicator(text, stateClass) {
    compileIndicatorEl.textContent = text;
    compileIndicatorEl.classList.remove("ok", "err");
    if (stateClass) {
        compileIndicatorEl.classList.add(stateClass);
    }
}

async function postJson(url, payload, options = {}) {
    const { reportToTerminal = true } = options;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || "Request failed.");
        }
        return data;
    } catch (error) {
        if (reportToTerminal) {
            terminalOutputEl.textContent = `[REQUEST ERROR]\n${error.message}`;
        }
        return null;
    }
}

function setAiStatus(message, stateClass) {
    if (!aiStatusEl) {
        return;
    }
    aiStatusEl.textContent = message;
    aiStatusEl.classList.remove("ok", "err");
    if (stateClass) {
        aiStatusEl.classList.add(stateClass);
    }
}

function explainCodeFallback(sourceCode, tac) {
    const lower = sourceCode.toLowerCase();
    const parts = [];
    if (lower.includes("declare variable")) {
        parts.push("This program declares one or more numeric variables.");
    }
    if (lower.includes("while ")) {
        parts.push("It uses a while loop to repeat statements while the condition remains true.");
    }
    if (lower.includes("if ")) {
        parts.push("It contains conditional logic using if/else.");
    }
    if (lower.includes("print ")) {
        parts.push("It prints values as runtime output.");
    }
    if (tac.length) {
        parts.push(`Compiler generated ${tac.length} TAC instructions for execution flow.`);
    }
    if (!parts.length) {
        parts.push("This program appears to contain simple statements. Run it to inspect result and TAC.");
    }
    return parts.join("\n");
}

function explainErrorFallback(error) {
    const location = `line ${error.line}, column ${error.column}`;
    const hint = error.hint ? `\nHint: ${error.hint}` : "";
    return `Error Type: ${error.type}\nLocation: ${location}\nMessage: ${error.message}${hint}`;
}

function suggestFixFallback(sourceCode, errors) {
    if (!errors.length) {
        return "No compiler errors were provided.";
    }
    const first = errors[0];
    const tips = [
        `Primary issue: ${first.message}`,
        `Location: line ${first.line}, column ${first.column}`,
        first.hint ? `Hint: ${first.hint}` : "Hint: Ensure declarations and semicolons are correct.",
        "Review this source and fix the highlighted statement:",
        sourceCode,
    ];
    return tips.join("\n");
}

function generateCodeFallback(prompt) {
    const lower = prompt.toLowerCase();
    const range = lower.match(/from\s+(\d+)\s+to\s+(\d+)/);
    if (range) {
        const start = Number(range[1]);
        const end = Number(range[2]);
        return [
            `declare variable counter = ${start};`,
            `declare variable limit = ${end};`,
            "while counter is less than or equal to limit do",
            "    print counter;",
            "    counter = counter + 1;",
            "end while;",
        ].join("\n");
    }

    if (lower.includes("pass") && lower.includes("fail")) {
        return [
            "declare variable marks = 60;",
            "if marks is greater than 50 then",
            "    print \"pass\";",
            "else",
            "    print \"fail\";",
            "end if;",
        ].join("\n");
    }

    return [
        "declare variable a = 10;",
        "declare variable b = 20;",
        "declare variable total;",
        "total = a + b;",
        "print total;",
    ].join("\n");
}

function formatErrors(errors) {
    if (!errors.length) {
        return "No compiler errors.";
    }
    return errors
        .map((error) => {
            const location = `line ${error.line}, column ${error.column}`;
            const hint = error.hint ? `\nHint: ${error.hint}` : "";
            return `${error.type}: ${error.message} (${location})${hint}`;
        })
        .join("\n\n");
}

function ensureAiEnabled() {
    if (!aiEnabled) {
        aiOutputEl.textContent = "AI is disabled. Set AI_GATEWAY_API_KEY in .env to enable AI features.";
        return false;
    }
    return true;
}
