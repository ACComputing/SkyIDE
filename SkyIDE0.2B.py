#!/usr/bin/env python3
"""
SkyIDE TKINTER 0.1
A small ARM-friendly Tkinter IDE prototype for Python, VB.NET, and Hugging Face-style agent workflows.

MIT License
Copyright (c) 2021 Flames LLC
"""

import keyword
import math
import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


APP_NAME = "ac's skyide 0.1a"
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

# Keep all buttons black with blue text.
BUTTON_TEXT_PALETTE = (
    {"fg": ACCENT, "bg": BUTTON_BG, "hover": BUTTON_HOVER},
)


PYTHON_TEMPLATE = """import math


def main():
    print("SkyIDE Python runner online.")
    print("Custom math engine test:", math.sqrt(144))


if __name__ == "__main__":
    main()
"""


VBNET_TEMPLATE = """Imports System

Module Program
    Sub Main(args As String())
        Console.WriteLine("SkyIDE VB.NET runner online.")
    End Sub
End Module
"""


HF_TEMPLATE = """# Hugging Face / agent scratchpad
# Paste a prompt, model idea, or Python helper code here.

agent_task = "Explain how to build a small code assistant."
print(agent_task)
"""


class SkyAgentEngine:
    """
    Tiny local AI-agent-style engine.

    This is not a neural model. It is a lightweight rules engine that uses
    math-based scoring to imitate agent routing for coding, debugging,
    optimization, and Hugging Face planning tasks.
    """

    def __init__(self):
        self.agents = (
            "Coder",
            "Debugger",
            "Optimizer",
            "HuggingFace Planner",
        )

    def _agent_scores(self, prompt, code):
        prompt_l = prompt.lower()
        code_l = code.lower()
        size = max(1, len(code.splitlines()))
        entropy_hint = math.log1p(len(set(code_l))) / math.sqrt(size)

        signals = {
            "Coder": [
                "make",
                "create",
                "write",
                "build",
                "feature",
                "button",
                "gui",
                "ide",
            ],
            "Debugger": [
                "error",
                "bug",
                "fix",
                "traceback",
                "crash",
                "exception",
            ],
            "Optimizer": [
                "fast",
                "speed",
                "optimize",
                "clean",
                "refactor",
                "memory",
            ],
            "HuggingFace Planner": [
                "huggingface",
                "hugging face",
                "model",
                "transformer",
                "token",
                "pipeline",
            ],
        }

        scores = {}

        for index, agent in enumerate(self.agents, start=1):
            hits = sum(
                1
                for word in signals[agent]
                if word in prompt_l or word in code_l
            )
            wave = abs(math.sin(index + entropy_hint))
            scores[agent] = round((hits * 10.0) + (wave * 3.0) + entropy_hint, 2)

        return scores

    def route(self, prompt, code):
        scores = self._agent_scores(prompt, code)
        return max(scores, key=scores.get)

    def analyze_code(self, code, language):
        lines = [line for line in code.splitlines() if line.strip()]
        line_count = len(lines)

        funcs = sum(
            1
            for line in lines
            if line.lstrip().startswith(("def ", "Sub ", "Function "))
        )

        classes = sum(
            1
            for line in lines
            if line.lstrip().startswith(("class ", "Class "))
        )

        loops = sum(
            1
            for line in lines
            if any(token in line for token in ("for ", "while ", "For ", "While "))
        )

        branches = sum(
            1
            for line in lines
            if any(token in line for token in ("if ", "elif ", "else", "If ", "Else"))
        )

        imports = sum(
            1
            for line in lines
            if line.strip().startswith(("import ", "from ", "Imports "))
        )

        complexity = math.sqrt(max(1, line_count)) + math.log1p(
            funcs + classes + loops + branches + imports
        )

        maintainability = max(
            0,
            min(100, round(100 - complexity * 5 + funcs * 2 + classes * 1.5)),
        )

        tips = []

        if language == "Python" and "if __name__" not in code:
            tips.append("Add an if __name__ == '__main__' guard for runnable Python files.")

        if language == "Python" and "import math" not in code:
            tips.append("Your concept mentions a custom math engine; add import math when needed.")

        if line_count > 40 and funcs < 2:
            tips.append("Split long scripts into functions so the IDE project stays easier to test.")

        if "huggingface" in code.lower() or "transformers" in code.lower():
            tips.append("For Hugging Face work, keep model loading separate from UI code.")

        if not tips:
            tips.append("Structure looks clean for a prototype.")

        return (
            f"Language: {language}\n"
            f"Lines: {line_count}\n"
            f"Imports: {imports}\n"
            f"Functions/Subs: {funcs}\n"
            f"Classes: {classes}\n"
            f"Loops: {loops}\n"
            f"Branches: {branches}\n"
            f"Maintainability score: {maintainability}/100\n\n"
            "Agent tips:\n- " + "\n- ".join(tips)
        )

    def respond(self, prompt, code, language):
        selected = self.route(prompt, code)
        analysis = self.analyze_code(code, language)
        scores = self._agent_scores(prompt, code)

        score_text = "\n".join(
            f"  {name}: {score}"
            for name, score in scores.items()
        )

        prompt_l = prompt.lower()

        if "hugging" in prompt_l or "model" in prompt_l or "transformer" in prompt_l:
            action = (
                "Suggested Hugging Face path:\n"
                "1. Build the Tkinter UI first.\n"
                "2. Keep model loading in a separate worker function.\n"
                "3. Add transformers only when the base IDE is stable.\n"
                "4. Never block the UI thread while generating text."
            )
        elif "debug" in prompt_l or "fix" in prompt_l or "error" in prompt_l:
            action = (
                "Debugger action: run the file, inspect stderr, then isolate "
                "the smallest failing function."
            )
        elif "optimize" in prompt_l or "fast" in prompt_l:
            action = (
                "Optimizer action: reduce repeated work, cache model objects, "
                "and avoid UI freezes with threads."
            )
        else:
            action = (
                "Coder action: add one feature at a time, test it, then commit "
                "the stable version."
            )

        return (
            f"SkyAgent selected: {selected}\n\n"
            f"Routing scores:\n{score_text}\n\n"
            f"{action}\n\n"
            f"Code analysis:\n{analysis}"
        )


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
        self._button_color_index = 0

        self._build_header()
        self._build_workspace()
        self._build_status_bar()
        self._bind_shortcuts()

        self.editor.insert("1.0", PYTHON_TEMPLATE)

        self._write_console("SkyIDE boot complete.")
        self._write_console(
            "Black buttons, blue shell, Python/VB.NET/Hugging Face agent prototype ready."
        )

        self._highlight_later()

    def _build_header(self):
        header = tk.Frame(self.root, bg=BLUE_BG, height=70)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="ac's skyide 0.1a",
            bg=BLUE_BG,
            fg="white",
            font=("Consolas", 20, "bold"),
            padx=14,
        )
        title.pack(side=tk.LEFT)

        subtitle = tk.Label(
            header,
            text="Python • VB.NET • Hugging Face • ARM-friendly Tkinter shell",
            bg=BLUE_BG,
            fg="#d8ecff",
            font=("Consolas", 10),
        )
        subtitle.pack(side=tk.LEFT, padx=(0, 16))

        toolbar = tk.Frame(header, bg=BLUE_BG)
        toolbar.pack(side=tk.RIGHT, padx=10)

        self._black_button(toolbar, "New", self.new_file).pack(side=tk.LEFT, padx=3)
        self._black_button(toolbar, "Open", self.open_file).pack(side=tk.LEFT, padx=3)
        self._black_button(toolbar, "Save", self.save_file).pack(side=tk.LEFT, padx=3)
        self._black_button(toolbar, "Run", self.run_current).pack(side=tk.LEFT, padx=3)
        self._black_button(toolbar, "AI Agent", self.ask_agent).pack(side=tk.LEFT, padx=3)

        option = tk.OptionMenu(
            toolbar,
            self.language,
            "Python",
            "VB.NET",
            "HuggingFace",
            command=self._language_changed,
        )

        option.config(
            bg=BUTTON_BG,
            fg=ACCENT,
            activebackground=BUTTON_HOVER,
            activeforeground=ACCENT,
        )
        option["menu"].config(bg=BUTTON_BG, fg=ACCENT)
        option.pack(side=tk.LEFT, padx=3)

    def _build_workspace(self):
        main = tk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            bg=BLUE_BG,
            bd=0,
        )
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        sidebar = tk.Frame(main, bg=PANEL_BG, width=280)
        main.add(sidebar, minsize=240)

        tk.Label(
            sidebar,
            text="SkyAgent Engine",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Consolas", 13, "bold"),
            pady=8,
        ).pack(fill=tk.X)

        tk.Label(
            sidebar,
            text="Agent prompt",
            bg=PANEL_BG,
            fg="white",
            anchor="w",
        ).pack(fill=tk.X, padx=10)

        self.agent_prompt = ScrolledText(
            sidebar,
            height=5,
            bg="#06112a",
            fg=TEXT_FG,
            insertbackground="white",
            font=("Consolas", 10),
            relief=tk.FLAT,
        )
        self.agent_prompt.pack(fill=tk.X, padx=10, pady=(3, 8))
        self.agent_prompt.insert(
            "1.0",
            "Analyze this IDE code and suggest the next feature.",
        )

        self._black_button(sidebar, "Ask Local Agent", self.ask_agent).pack(
            fill=tk.X,
            padx=10,
            pady=4,
        )

        self._black_button(sidebar, "Analyze Code", self.analyze_code).pack(
            fill=tk.X,
            padx=10,
            pady=4,
        )

        self._black_button(sidebar, "Insert Python Template", self.insert_python_template).pack(
            fill=tk.X,
            padx=10,
            pady=4,
        )

        self._black_button(sidebar, "Insert VB.NET Template", self.insert_vbnet_template).pack(
            fill=tk.X,
            padx=10,
            pady=4,
        )

        self._black_button(sidebar, "Insert HF Template", self.insert_hf_template).pack(
            fill=tk.X,
            padx=10,
            pady=4,
        )

        tk.Label(
            sidebar,
            text="Agent output",
            bg=PANEL_BG,
            fg="white",
            anchor="w",
        ).pack(fill=tk.X, padx=10, pady=(10, 0))

        self.agent_output = ScrolledText(
            sidebar,
            height=14,
            bg="#06112a",
            fg=TEXT_FG,
            insertbackground="white",
            font=("Consolas", 9),
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        self.agent_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=(3, 10))

        right = tk.PanedWindow(
            main,
            orient=tk.VERTICAL,
            sashwidth=6,
            bg=BLUE_BG,
            bd=0,
        )
        main.add(right, minsize=500)

        editor_frame = tk.Frame(right, bg=PANEL_BG)
        right.add(editor_frame, minsize=300)

        editor_top = tk.Frame(editor_frame, bg=PANEL_BG)
        editor_top.pack(fill=tk.X)

        self.file_label = tk.Label(
            editor_top,
            text="untitled.py",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Consolas", 11, "bold"),
            padx=8,
            pady=5,
        )
        self.file_label.pack(side=tk.LEFT)

        self.editor = ScrolledText(
            editor_frame,
            bg=EDITOR_BG,
            fg=TEXT_FG,
            insertbackground="white",
            selectbackground="#245eff",
            font=("Consolas", 12),
            undo=True,
            wrap=tk.NONE,
            relief=tk.FLAT,
        )
        self.editor.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        self.editor.bind("<KeyRelease>", lambda event: self._highlight_later())

        self.editor.tag_configure("keyword", foreground="#8be9fd")
        self.editor.tag_configure("comment", foreground=COMMENT)
        self.editor.tag_configure("string", foreground=WARNING)
        self.editor.tag_configure("error", foreground=ERROR)

        console_frame = tk.Frame(right, bg=PANEL_BG)
        right.add(console_frame, minsize=130)

        console_header = tk.Frame(console_frame, bg=PANEL_BG)
        console_header.pack(fill=tk.X)

        tk.Label(
            console_header,
            text="Console",
            bg=PANEL_BG,
            fg=ACCENT,
            font=("Consolas", 11, "bold"),
            padx=8,
            pady=5,
        ).pack(side=tk.LEFT)

        self._black_button(console_header, "Clear", self.clear_console).pack(
            side=tk.RIGHT,
            padx=8,
            pady=4,
        )

        self.console = ScrolledText(
            console_frame,
            height=10,
            bg=CONSOLE_BG,
            fg=TEXT_FG,
            insertbackground="white",
            font=("Consolas", 10),
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        self.console.tag_configure("prompt", foreground=ACCENT)
        self.console.tag_configure("error", foreground=ERROR)

    def _build_status_bar(self):
        self.status = tk.Label(
            self.root,
            text="Ready | F5 Run | Ctrl+S Save | Ctrl+O Open",
            anchor="w",
            bg="#03122d",
            fg="#d8ecff",
            font=("Consolas", 9),
            padx=10,
        )
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _bind_shortcuts(self):
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<F5>", lambda event: self.run_current())

    def _black_button(self, parent, text, command):
        palette = BUTTON_TEXT_PALETTE[
            self._button_color_index % len(BUTTON_TEXT_PALETTE)
        ]
        self._button_color_index += 1

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=palette["bg"],
            fg=palette["fg"],
            activebackground=palette["hover"],
            activeforeground=palette["fg"],
            font=("Consolas", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=6,
            cursor="hand2",
        )

        button.bind("<Enter>", lambda event: button.config(bg=palette["hover"]))
        button.bind("<Leave>", lambda event: button.config(bg=palette["bg"]))

        return button

    def _language_changed(self, *_):
        lang = self.language.get()
        self.status.config(text=f"Language set to {lang}")

        if self.current_file is None:
            extension = {
                "Python": "py",
                "VB.NET": "vb",
                "HuggingFace": "txt",
            }.get(lang, "txt")

            self.file_label.config(text=f"untitled.{extension}")

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

    def new_file(self):
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
        path = filedialog.askopenfilename(
            title="Open source file",
            filetypes=(
                ("Source files", "*.py *.vb *.txt *.md"),
                ("Python", "*.py"),
                ("VB.NET", "*.vb"),
                ("All files", "*.*"),
            ),
        )

        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                self.set_code(file.read())
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as file:
                self.set_code(file.read())
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not open file:\n{exc}")
            return

        self.current_file = path
        self.file_label.config(text=os.path.basename(path))

        if path.endswith(".py"):
            self.language.set("Python")
        elif path.endswith(".vb"):
            self.language.set("VB.NET")

        self.status.config(text=f"Opened {path}")

    def save_file(self):
        if self.current_file is None:
            return self.save_file_as()

        try:
            with open(self.current_file, "w", encoding="utf-8") as file:
                file.write(self.get_code() + "\n")
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not save file:\n{exc}")
            return

        self.status.config(text=f"Saved {self.current_file}")
        self._write_console(f"Saved {os.path.basename(self.current_file)}")

    def save_file_as(self):
        lang = self.language.get()

        if lang == "Python":
            default_ext = ".py"
        elif lang == "VB.NET":
            default_ext = ".vb"
        else:
            default_ext = ".txt"

        path = filedialog.asksaveasfilename(
            title="Save file",
            defaultextension=default_ext,
            filetypes=(
                ("Python", "*.py"),
                ("VB.NET", "*.vb"),
                ("Text", "*.txt"),
                ("All files", "*.*"),
            ),
        )

        if not path:
            return

        self.current_file = path
        self.file_label.config(text=os.path.basename(path))
        self.save_file()

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

    def run_current(self):
        lang = self.language.get()
        code = self.get_code()

        self._write_console(f"Running {lang}...")

        if lang == "Python" or lang == "HuggingFace":
            self._run_python(code)
        elif lang == "VB.NET":
            self._run_vbnet(code)
        else:
            self._write_console(f"Unknown language: {lang}", "error")

    def _run_python(self, code):
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                "w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            ) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            result = subprocess.run(
                [sys.executable, temp_path],
                capture_output=True,
                text=True,
                timeout=20,
            )

            if result.stdout:
                self._write_console(result.stdout.rstrip())

            if result.stderr:
                self._write_console(result.stderr.rstrip(), "error")

            if not result.stdout and not result.stderr:
                self._write_console("Process finished with no output.")

            self.status.config(text=f"Python exited with code {result.returncode}")

        except subprocess.TimeoutExpired:
            self._write_console("Python run timed out after 20 seconds.", "error")
        except Exception as exc:
            self._write_console(f"Python run failed: {exc}", "error")
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def _run_vbnet(self, code):
        dotnet = shutil.which("dotnet")

        if dotnet is None:
            self._write_console(
                "VB.NET needs the dotnet CLI. Install the .NET SDK, then run again.",
                "error",
            )
            return

        project_dir = tempfile.mkdtemp(prefix="skyide_vb_")

        try:
            new_project = subprocess.run(
                [dotnet, "new", "console", "-lang", "VB", "--force"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if new_project.returncode != 0:
                self._write_console(new_project.stderr or new_project.stdout, "error")
                return

            program_path = os.path.join(project_dir, "Program.vb")

            with open(program_path, "w", encoding="utf-8") as file:
                file.write(code)

            result = subprocess.run(
                [dotnet, "run"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                self._write_console(result.stdout.rstrip())

            if result.stderr:
                self._write_console(result.stderr.rstrip(), "error")

            if not result.stdout and not result.stderr:
                self._write_console("VB.NET process finished with no output.")

            self.status.config(text=f"VB.NET exited with code {result.returncode}")

        except subprocess.TimeoutExpired:
            self._write_console("VB.NET run timed out.", "error")
        except Exception as exc:
            self._write_console(f"VB.NET run failed: {exc}", "error")
        finally:
            shutil.rmtree(project_dir, ignore_errors=True)

    def ask_agent(self):
        prompt = self.agent_prompt.get("1.0", tk.END).strip()

        if not prompt:
            prompt = "Analyze current file."

        response = self.engine.respond(
            prompt,
            self.get_code(),
            self.language.get(),
        )

        self.agent_output.delete("1.0", tk.END)
        self.agent_output.insert("1.0", response)
        self._write_console("SkyAgent generated a local response.")

    def analyze_code(self):
        response = self.engine.analyze_code(
            self.get_code(),
            self.language.get(),
        )

        self.agent_output.delete("1.0", tk.END)
        self.agent_output.insert("1.0", response)
        self._write_console("Code analysis complete.")

    def _highlight_later(self):
        if self._highlight_after is not None:
            self.root.after_cancel(self._highlight_after)

        self._highlight_after = self.root.after(180, self._highlight_now)

    def _highlight_now(self):
        self._highlight_after = None

        for tag in ("keyword", "comment", "string"):
            self.editor.tag_remove(tag, "1.0", tk.END)

        code = self.get_code()
        lang = self.language.get()

        if lang != "Python":
            return

        keywords = set(keyword.kwlist)

        for line_number, line in enumerate(code.splitlines(), start=1):
            comment_col = line.find("#")

            if comment_col != -1:
                self.editor.tag_add(
                    "comment",
                    f"{line_number}.{comment_col}",
                    f"{line_number}.end",
                )

            in_string = False
            string_start = None
            quote_char = ""

            for col, char in enumerate(line):
                if char in ("'", '"') and (col == 0 or line[col - 1] != "\\"):
                    if not in_string:
                        in_string = True
                        string_start = col
                        quote_char = char
                    elif char == quote_char and string_start is not None:
                        self.editor.tag_add(
                            "string",
                            f"{line_number}.{string_start}",
                            f"{line_number}.{col + 1}",
                        )
                        in_string = False
                        string_start = None

            if in_string and string_start is not None:
                self.editor.tag_add(
                    "string",
                    f"{line_number}.{string_start}",
                    f"{line_number}.end",
                )

            start = 0

            while start < len(line):
                while start < len(line) and not (
                    line[start].isalpha() or line[start] == "_"
                ):
                    start += 1

                end = start

                while end < len(line) and (
                    line[end].isalnum() or line[end] == "_"
                ):
                    end += 1

                word = line[start:end]

                if word in keywords:
                    self.editor.tag_add(
                        "keyword",
                        f"{line_number}.{start}",
                        f"{line_number}.{end}",
                    )

                start = max(end, start + 1)


def main():
    root = tk.Tk()
    SkyIDEApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
