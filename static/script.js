const sourceCodeEl = document.getElementById("source-code");
const runBtn = document.getElementById("run-btn");
const compileIndicatorEl = document.getElementById("compile-indicator");
const terminalOutputEl = document.getElementById("terminal-output");
const terminalTabs = document.querySelectorAll(".term-tab");

const fileListEl = document.getElementById("file-list");
const newFileNameEl = document.getElementById("new-file-name");
const createFileBtn = document.getElementById("create-file-btn");
const activeFileNameEl = document.getElementById("active-file-name");

const aiTabs = document.querySelectorAll(".ai-tab");
const aiPanes = document.querySelectorAll(".ai-pane");
const aiOutputEl = document.getElementById("ai-output");
const promptEl = document.getElementById("prompt-text");

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
    const compileResult = await postJson("/compile", { source_code: sourceCodeEl.value });
    if (!compileResult) {
        return;
    }

    if (!compileResult.success) {
        aiOutputEl.textContent = "Run successful code first, then ask for explanation.";
        return;
    }

    if (!ensureAiEnabled()) {
        return;
    }

    const result = await postJson("/ai/explain-code", {
        source_code: sourceCodeEl.value,
        tac: compileResult.tac,
    });
    if (result?.success) {
        aiOutputEl.textContent = result.text;
    }
}

async function explainError() {
    const compileResult = await postJson("/compile", { source_code: sourceCodeEl.value });
    if (!compileResult) {
        return;
    }

    if (compileResult.success) {
        aiOutputEl.textContent = "No errors found. Run code with an issue to explain an error.";
        return;
    }

    if (!ensureAiEnabled()) {
        return;
    }

    const [firstError] = compileResult.errors || [];
    const result = await postJson("/ai/explain-error", {
        source_code: sourceCodeEl.value,
        error: firstError,
    });
    if (result?.success) {
        aiOutputEl.textContent = result.text;
    }
}

async function suggestFix() {
    const compileResult = await postJson("/compile", { source_code: sourceCodeEl.value });
    if (!compileResult) {
        return;
    }

    if (compileResult.success) {
        aiOutputEl.textContent = "No errors found. Nothing to fix right now.";
        return;
    }

    if (!ensureAiEnabled()) {
        return;
    }

    const result = await postJson("/ai/suggest-fix", {
        source_code: sourceCodeEl.value,
        errors: compileResult.errors || [],
    });
    if (result?.success) {
        aiOutputEl.textContent = result.text;
    }
}

async function generateCode() {
    if (!ensureAiEnabled()) {
        return;
    }
    const prompt = promptEl.value.trim();
    if (!prompt) {
        aiOutputEl.textContent = "Describe what code you want to generate first.";
        return;
    }
    const result = await postJson("/ai/generate-code", { prompt });
    if (result?.success) {
        sourceCodeEl.value = result.text;
        persistCurrentFile();
        aiOutputEl.textContent = "Generated code inserted into current file.";
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

async function postJson(url, payload) {
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
        terminalOutputEl.textContent = `[REQUEST ERROR]\n${error.message}`;
        return null;
    }
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
