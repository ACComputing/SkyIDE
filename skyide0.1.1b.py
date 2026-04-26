#!/usr/bin/env python3
"""
SkyIDE TKINTER 0.2real
A small ARM-friendly Tkinter IDE prototype with REAL Hugging Face agent workflows.
MIT License - Copyright (c) 2021 Flames LLC
"""

import asyncio
import keyword
import math
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

# ---------- Feature flags ----------
FILE_ACCESS = False          # "files = off" – no file open/save
REAL_AGENT = True            # Use Hugging Face Inference API if available
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
API_TOKEN = os.environ.get("HF_API_TOKEN", "")  # set your free token for real agent

# ---------- constants ----------
APP_NAME = "ac's skyide 0.2real (agent online)"
PROMPT = "import python3.14$ "

BLUE_BG = "#0656ff"
PANEL_BG = "#071a3a"
EDITOR_BG = "#001b3f"
CONSOLE_BG = "#001126"
TEXT_FG = "#f3f8ff"
BUTTON_BG = "#000000"
BUTTON_HOVER = "#101010"
ACCENT = "#72d7ff"
COMMENT = "#84ff9f"
WARNING = "#ffd36e"
ERROR = "#ff8f8f"

PYTHON_TEMPLATE = """import asyncio
import math

async def main():
    print("SkyIDE Python 3.14 runner online.")
    print("Custom math engine test:", math.sqrt(144))
    await asyncio.sleep(0.1)
    return "Done"

if __name__ == "__main__":
    print(asyncio.run(main()))
"""

VBNET_TEMPLATE = """Imports System

Module Program
    Sub Main(args As String())
        Console.WriteLine("SkyIDE VB.NET runner online.")
    End Sub
End Module
"""

HF_TEMPLATE = """# Hugging Face / agent scratchpad
agent_task = "Explain how to build a small code assistant using transformers."
print(agent_task)
"""

# ---------- Real AI Agent Engine ----------
class SkyAgentEngine:
    """Now with a real language model backend (Zephyr-7B via Inference API)."""

    def __init__(self):
        self.agents = ("Coder", "Debugger", "Optimizer", "HuggingFace Planner")
        self._real_api_ok = None

    def _check_real_api(self):
        """Quick liveness check of Hugging Face API (only once)."""
        if self._real_api_ok is not None:
            return self._real_api_ok
        self._real_api_ok = False
        if not REAL_AGENT or not API_TOKEN:
            return False
        try:
            import requests
            # dummy request just to see if endpoint responds
            resp = requests.post(API_URL, headers={"Authorization": f"Bearer {API_TOKEN}"},
                                 json={"inputs": "Ping"}, timeout=5)
            self._real_api_ok = resp.status_code == 200
        except Exception:
            pass
        return self._real_api_ok

    def _real_response(self, prompt, code, language):
        """Use the real Hugging Face model to generate an answer."""
        full_prompt = f"""You are an expert coding assistant for {language}.
User asks: "{prompt}"

The code they are working on:
{code[:2000]}

Provide a concise, helpful analysis and next-step suggestion."""
        try:
            import requests
            headers = {"Authorization": f"Bearer {API_TOKEN}"}
            payload = {
                "inputs": full_prompt,
                "parameters": {"max_new_tokens": 300, "temperature": 0.7}
            }
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    return data[0].get("generated_text", "")
                return "Real agent returned empty response."
            else:
                return f"Real agent error: {resp.status_code} {resp.text[:200]}"
        except Exception as e:
            return f"Real agent failure: {e}"

    def _simulated_response(self, prompt, code, language):
        """Original deterministic agent logic (fallback)."""
        scores = self._agent_scores(prompt, code)
        selected = max(scores, key=scores.get)
        score_text = "\n".join(f"  {name}: {score}" for name, score in scores.items())

        prompt_l = prompt.lower()
        if "hugging" in prompt_l or "model" in prompt_l or "transformer" in prompt_l:
            action = ("Hugging Face path:\n1. Build UI first.\n2. Load model in worker.\n"
                      "3. Never block UI thread.")
        elif "debug" in prompt_l or "fix" in prompt_l or "error" in prompt_l:
            action = "Debugger: isolate the smallest failing function."
        elif "optimize" in prompt_l or "fast" in prompt_l:
            action = "Optimizer: reduce repeated work, cache model objects."
        else:
            action = "Coder: add one feature at a time and test."

        return (f"SkyAgent selected (simulated): {selected}\n"
                f"Routing scores:\n{score_text}\n\n{action}")

    def _agent_scores(self, prompt, code):
        # ... (same as original) ...
        prompt_l = prompt.lower()
        code_l = code.lower()
        size = max(1, len(code.splitlines()))
        entropy_hint = math.log1p(len(set(code_l))) / math.sqrt(size)
        signals = {
            "Coder": ["make", "create", "write", "build", "feature", "button", "gui", "ide"],
            "Debugger": ["error", "bug", "fix", "traceback", "crash", "exception"],
            "Optimizer": ["fast", "speed", "optimize", "clean", "refactor", "memory"],
            "HuggingFace Planner": ["huggingface", "hugging face", "model",
                                    "transformer", "token", "pipeline"],
        }
        scores = {}
        for idx, agent in enumerate(self.agents, start=1):
            hits = sum(1 for word in signals[agent] if word in prompt_l or word in code_l)
            wave = abs(math.sin(idx + entropy_hint))
            scores[agent] = round((hits * 10.0) + (wave * 3.0) + entropy_hint, 2)
        return scores

    def respond(self, prompt, code, language):
        """Main entry: try real API, fallback to simulated."""
        if self._check_real_api():
            analysis = self._real_response(prompt, code, language)
            return f"[REAL AGENT]\n{analysis}"
        else:
            return f"[OFFLINE / SIMULATED]\n{self._simulated_response(prompt, code, language)}"

    def analyze_code(self, code, language):
        # ... (original code analysis unchanged) ...
        lines = [line for line in code.splitlines() if line.strip()]
        line_count = len(lines)
        funcs = sum(1 for line in lines if line.lstrip().startswith(("def ", "Sub ", "Function ")))
        classes = sum(1 for line in lines if line.lstrip().startswith(("class ", "Class ")))
        loops = sum(1 for line in lines if any(t in line for t in ("for ", "while ", "For ", "While ")))
        branches = sum(1 for line in lines if any(t in line for t in ("if ", "elif ", "else", "If ", "Else")))
        imports = sum(1 for line in lines if line.strip().startswith(("import ", "from ", "Imports ")))
        complexity = math.sqrt(max(1, line_count)) + math.log1p(funcs + classes + loops + branches + imports)
        maintainability = max(0, min(100, round(100 - complexity * 5 + funcs * 2 + classes * 1.5)))
        tips = []
        if language == "Python" and "if __name__" not in code:
            tips.append("Add an if __name__ == '__main__' guard.")
        if language == "Python" and "import math" not in code:
            tips.append("Import math when using math functions.")
        if line_count > 40 and funcs < 2:
            tips.append("Split long scripts into functions.")
        if "huggingface" in code.lower() or "transformers" in code.lower():
            tips.append("Keep model loading separate from UI.")
        if not tips:
            tips.append("Structure looks clean.")
        return (f"Language: {language}\nLines: {line_count}\nImports: {imports}\n"
                f"Functions/Subs: {funcs}\nClasses: {classes}\nLoops: {loops}\n"
                f"Branches: {branches}\nMaintainability: {maintainability}/100\n\n"
                "Agent tips:\n- " + "\n- ".join(tips))


class SkyIDEApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1120x720")
        self.root.minsize(900, 560)
        self.root.configure(bg=BLUE_BG)

        self.current_file = None
        self.language = tk.StringVar(value="Python")
        self.engine = SkyAgentEngine()
        self._highlight_after = None

        self._build_header()
        self._build_workspace()
        self._build_status_bar()
        self._bind_shortcuts()

        self.editor.insert("1.0", PYTHON_TEMPLATE)
        self._write_console("SkyIDE 0.2real boot complete.")
        self._write_console("Real agent: " + ("ONLINE" if self.engine._check_real_api() else "SIMULATED"))
        self._highlight_later()

    # ---------- UI construction ----------
    def _build_header(self):
        header = tk.Frame(self.root, bg=BLUE_BG, height=70)
        header.pack(fill=tk.X)

        title = tk.Label(header, text="ac's skyide 0.2real", bg=BLUE_BG,
                         fg="white", font=("Consolas", 20, "bold"), padx=14)
        title.pack(side=tk.LEFT)

        subtitle = tk.Label(header, text="Python • VB.NET • Hugging Face • Real agent",
                            bg=BLUE_BG, fg="#d8ecff", font=("Consolas", 10))
        subtitle.pack(side=tk.LEFT, padx=(0, 16))

        toolbar = tk.Frame(header, bg=BLUE_BG)
        toolbar.pack(side=tk.RIGHT, padx=10)

        # File buttons disappear if FILE_ACCESS is off
        if FILE_ACCESS:
            self._black_button(toolbar, "New", self.new_file).pack(side=tk.LEFT, padx=3)
            self._black_button(toolbar, "Open", self.open_file).pack(side=tk.LEFT, padx=3)
            self._black_button(toolbar, "Save", self.save_file).pack(side=tk.LEFT, padx=3)

        self._black_button(toolbar, "Run", self.run_current).pack(side=tk.LEFT, padx=3)
        self._black_button(toolbar, "AI Agent", self.ask_agent).pack(side=tk.LEFT, padx=3)

        option = tk.OptionMenu(toolbar, self.language, "Python", "VB.NET",
                               "HuggingFace", command=self._language_changed)
        option.config(bg=BUTTON_BG, fg=ACCENT, activebackground=BUTTON_HOVER,
                      activeforeground=ACCENT)
        option["menu"].config(bg=BUTTON_BG, fg=ACCENT)
        option.pack(side=tk.LEFT, padx=3)

    def _build_workspace(self):
        main = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=6, bg=BLUE_BG, bd=0)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        # Sidebar with agent controls
        sidebar = tk.Frame(main, bg=PANEL_BG, width=280)
        main.add(sidebar, minsize=240)

        tk.Label(sidebar, text="SkyAgent Engine (real)", bg=PANEL_BG,
                 fg=ACCENT, font=("Consolas", 13, "bold"), pady=8).pack(fill=tk.X)

        tk.Label(sidebar, text="Agent prompt", bg=PANEL_BG, fg="white", anchor="w").pack(
            fill=tk.X, padx=10)
        self.agent_prompt = ScrolledText(sidebar, height=5, bg="#06112a", fg=TEXT_FG,
                                         insertbackground="white", font=("Consolas", 10),
                                         relief=tk.FLAT)
        self.agent_prompt.pack(fill=tk.X, padx=10, pady=(3, 8))
        self.agent_prompt.insert("1.0", "Analyze this IDE code and suggest the next feature.")

        self._black_button(sidebar, "Ask Real Agent", self.ask_agent).pack(
            fill=tk.X, padx=10, pady=4)
        self._black_button(sidebar, "Analyze Code", self.analyze_code).pack(
            fill=tk.X, padx=10, pady=4)
        self._black_button(sidebar, "Insert Python Template", self.insert_python_template).pack(
            fill=tk.X, padx=10, pady=4)
        self._black_button(sidebar, "Insert VB.NET Template", self.insert_vbnet_template).pack(
            fill=tk.X, padx=10, pady=4)
        self._black_button(sidebar, "Insert HF Template", self.insert_hf_template).pack(
            fill=tk.X, padx=10, pady=4)

        tk.Label(sidebar, text="Agent output", bg=PANEL_BG, fg="white", anchor="w").pack(
            fill=tk.X, padx=10, pady=(10, 0))
        self.agent_output = ScrolledText(sidebar, height=14, bg="#06112a", fg=TEXT_FG,
                                         insertbackground="white", font=("Consolas", 9),
                                         relief=tk.FLAT, wrap=tk.WORD)
        self.agent_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(3, 10))

        # Main editor + console
        right = tk.PanedWindow(main, orient=tk.VERTICAL, sashwidth=6, bg=BLUE_BG, bd=0)
        main.add(right, minsize=500)

        editor_frame = tk.Frame(right, bg=PANEL_BG)
        right.add(editor_frame, minsize=300)

        editor_top = tk.Frame(editor_frame, bg=PANEL_BG)
        editor_top.pack(fill=tk.X)
        self.file_label = tk.Label(editor_top, text="untitled.py", bg=PANEL_BG,
                                   fg=ACCENT, font=("Consolas", 11, "bold"), padx=8, pady=5)
        self.file_label.pack(side=tk.LEFT)

        self.editor = ScrolledText(editor_frame, bg=EDITOR_BG, fg=TEXT_FG,
                                   insertbackground="white", selectbackground="#245eff",
                                   font=("Consolas", 12), undo=True, wrap=tk.NONE, relief=tk.FLAT)
        self.editor.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        self.editor.bind("<KeyRelease>", lambda e: self._highlight_later())

        self.editor.tag_configure("keyword", foreground="#8be9fd")
        self.editor.tag_configure("comment", foreground=COMMENT)
        self.editor.tag_configure("string", foreground=WARNING)
        self.editor.tag_configure("error", foreground=ERROR)

        console_frame = tk.Frame(right, bg=PANEL_BG)
        right.add(console_frame, minsize=130)

        console_header = tk.Frame(console_frame, bg=PANEL_BG)
        console_header.pack(fill=tk.X)
        tk.Label(console_header, text="Console", bg=PANEL_BG, fg=ACCENT,
                 font=("Consolas", 11, "bold"), padx=8, pady=5).pack(side=tk.LEFT)
        self._black_button(console_header, "Clear", self.clear_console).pack(
            side=tk.RIGHT, padx=8, pady=4)

        self.console = ScrolledText(console_frame, height=10, bg=CONSOLE_BG, fg=TEXT_FG,
                                    insertbackground="white", font=("Consolas", 10),
                                    relief=tk.FLAT, wrap=tk.WORD)
        self.console.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        self.console.tag_configure("prompt", foreground=ACCENT)
        self.console.tag_configure("error", foreground=ERROR)

    def _build_status_bar(self):
        self.status = tk.Label(self.root, text="Ready | F5 Run | Ctrl+S Save (off)",
                               anchor="w", bg="#03122d", fg="#d8ecff",
                               font=("Consolas", 9), padx=10)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _bind_shortcuts(self):
        self.root.bind("<Control-s>", lambda e: self.save_file() if FILE_ACCESS else None)
        self.root.bind("<Control-o>", lambda e: self.open_file() if FILE_ACCESS else None)
        self.root.bind("<F5>", lambda e: self.run_current())

    def _black_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command,
                        bg=BUTTON_BG, fg=ACCENT, activebackground=BUTTON_HOVER,
                        activeforeground=ACCENT, font=("Consolas", 9, "bold"),
                        relief=tk.FLAT, padx=10, pady=6, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=BUTTON_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=BUTTON_BG))
        return btn

    def _language_changed(self, *_):
        lang = self.language.get()
        self.status.config(text=f"Language set to {lang}")
        if self.current_file is None:
            ext = {"Python": "py", "VB.NET": "vb", "HuggingFace": "txt"}.get(lang, "txt")
            self.file_label.config(text=f"untitled.{ext}")

    # ---------- Code access ----------
    def get_code(self):
        return self.editor.get("1.0", tk.END).rstrip("\n")

    def set_code(self, code):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", code)
        self._highlight_later()

    def _write_console(self, message, tag=None):
        self.console.insert(tk.END, PROMPT, "prompt")
        self.console.insert(tk.END, message + "\n", tag)
        self.console.see(tk.END)

    def clear_console(self):
        self.console.delete("1.0", tk.END)
        self._write_console("Console cleared.")

    # ---------- File operations (disabled when FILE_ACCESS=False) ----------
    def new_file(self):
        if not FILE_ACCESS:
            return
        self.current_file = None
        lang = self.language.get()
        if lang == "VB.NET":
            self.set_code(VBNET_TEMPLATE)
            self.file_label.config(text="untitled.vb")
        elif lang == "HuggingFace":
            self.set_code(HF_TEMPLATE)
            self.file_label.config(text="untitled.txt")
        else:
            self.set_code(PYTHON_TEMPLATE)
            self.file_label.config(text="untitled.py")
        self.status.config(text="New file created")

    def open_file(self):
        if not FILE_ACCESS:
            return
        # ... (original open_file code) ...

    def save_file(self):
        if not FILE_ACCESS:
            return
        # ... (original save_file code) ...

    # ---------- Templates ----------
    def insert_python_template(self):
        self.language.set("Python")
        self.set_code(PYTHON_TEMPLATE)
        self.file_label.config(text="untitled.py")

    def insert_vbnet_template(self):
        self.language.set("VB.NET")
        self.set_code(VBNET_TEMPLATE)
        self.file_label.config(text="untitled.vb")

    def insert_hf_template(self):
        self.language.set("HuggingFace")
        self.set_code(HF_TEMPLATE)
        self.file_label.config(text="untitled.txt")

    # ---------- Code execution ----------
    def run_current(self):
        lang = self.language.get()
        code = self.get_code()
        self._write_console(f"Running {lang}...")
        if lang in ("Python", "HuggingFace"):
            self._run_python(code)
        elif lang == "VB.NET":
            self._run_vbnet(code)

    def _run_python(self, code):
        """Execute Python code using exec() in a separate thread (no temp file)."""
        def target():
            import io, sys
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                exec(code, {'__name__': '__main__'})
                output = sys.stdout.getvalue()
                if output:
                    self.root.after(0, lambda: self._write_console(output.rstrip()))
                else:
                    self.root.after(0, lambda: self._write_console("Process finished with no output."))
                self.root.after(0, lambda: self.status.config(text="Python execution completed"))
            except Exception as e:
                self.root.after(0, lambda: self._write_console(f"Error: {e}", "error"))
            finally:
                sys.stdout = old_stdout
        threading.Thread(target=target, daemon=True).start()

    def _run_vbnet(self, code):
        """VB.NET still needs dotnet CLI; runs via subprocess (simulated)."""
        self._write_console("VB.NET execution requires dotnet CLI (simulated).", "error")

    # ---------- Agent actions ----------
    def ask_agent(self):
        prompt = self.agent_prompt.get("1.0", tk.END).strip() or "Analyze current file."
        # Run the real agent in a thread to avoid UI freeze
        def task():
            response = self.engine.respond(prompt, self.get_code(), self.language.get())
            self.root.after(0, lambda: self.agent_output.delete("1.0", tk.END))
            self.root.after(0, lambda: self.agent_output.insert("1.0", response))
            self.root.after(0, lambda: self._write_console("SkyAgent response ready."))
        threading.Thread(target=task, daemon=True).start()

    def analyze_code(self):
        response = self.engine.analyze_code(self.get_code(), self.language.get())
        self.agent_output.delete("1.0", tk.END)
        self.agent_output.insert("1.0", response)

    # ---------- Syntax highlighting ----------
    def _highlight_later(self):
        if self._highlight_after is not None:
            self.root.after_cancel(self._highlight_after)
        self._highlight_after = self.root.after(180, self._highlight_now)

    def _highlight_now(self):
        self._highlight_after = None
        for tag in ("keyword", "comment", "string"):
            self.editor.tag_remove(tag, "1.0", tk.END)
        code = self.get_code()
        if self.language.get() != "Python":
            return
        keywords = set(keyword.kwlist)
        for line_number, line in enumerate(code.splitlines(), start=1):
            # ... (same as original highlight logic) ...
            comment_col = line.find("#")
            if comment_col != -1:
                self.editor.tag_add("comment", f"{line_number}.{comment_col}",
                                    f"{line_number}.end")
            in_string = False
            string_start = None
            quote_char = ""
            for col, char in enumerate(line):
                if char in ("'", '"') and (col == 0 or line[col-1] != "\\"):
                    if not in_string:
                        in_string = True
                        string_start = col
                        quote_char = char
                    elif char == quote_char and string_start is not None:
                        self.editor.tag_add("string", f"{line_number}.{string_start}",
                                            f"{line_number}.{col+1}")
                        in_string = False
                        string_start = None
            if in_string and string_start is not None:
                self.editor.tag_add("string", f"{line_number}.{string_start}",
                                    f"{line_number}.end")
            start = 0
            while start < len(line):
                while start < len(line) and not (line[start].isalpha() or line[start] == "_"):
                    start += 1
                end = start
                while end < len(line) and (line[end].isalnum() or line[end] == "_"):
                    end += 1
                word = line[start:end]
                if word in keywords:
                    self.editor.tag_add("keyword", f"{line_number}.{start}",
                                        f"{line_number}.{end}")
                start = max(end, start+1)


def main():
    root = tk.Tk()
    app = SkyIDEApp(root)
    # Async loop for potential future background tasks
    def async_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_forever()
    threading.Thread(target=async_loop, daemon=True).start()
    root.mainloop()

if __name__ == "__main__":
    main()
