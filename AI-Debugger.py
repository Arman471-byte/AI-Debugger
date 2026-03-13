# AI Debugger using ollama and tkinter

import ollama
from tkinter import * #type: ignore 
from tkinter import filedialog

from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

# -------------------------------
# Custom Rounded Button Widget
# -------------------------------

class RoundedButton(Canvas):

    def __init__(self, parent, text, command=None, width=120, height=40, radius=20):

        super().__init__(
            parent,
            width=width,
            height=height,
            bg="black",              # canvas background
            highlightthickness=0     # removes border around canvas
        )

        self.command = command
        self.radius = radius
        self.width = width
        self.height = height

        # Draw the rounded rectangle
        self.draw_rounded_rect(2, 2, width-2, height-2, radius)

        # Draw the text in the center of the button
        self.create_text(
            width/2,
            height/2,
            text=text,
            fill="white",
            font=("Consolas", 12, "bold")
        )

        # Mouse events
        self.bind("<Button-1>", self.on_click)  # left mouse click
        self.bind("<Enter>", self.on_hover)     # mouse enters button
        self.bind("<Leave>", self.on_leave)     # mouse leaves button


    # --------------------------------
    # Function that draws rounded box
    # --------------------------------
    def draw_rounded_rect(self, x1, y1, x2, y2, r):

        # x1,y1 = top-left corner of button
        # x2,y2 = bottom-right corner of button
        # r     = radius of the rounded corners

        points = [

            # ----- Top Edge -----
            x1+r, y1,     # start after top-left corner curve
            x2-r, y1,     # stop before top-right corner curve

            # ----- Top Right Corner -----
            x2, y1,       # corner control point
            x2, y1+r,     # move downward to begin right edge

            # ----- Right Edge -----
            x2, y2-r,     # stop before bottom-right curve

            # ----- Bottom Right Corner -----
            x2, y2,       # bottom-right control point
            x2-r, y2,     # move left along bottom edge

            # ----- Bottom Edge -----
            x1+r, y2,     # stop before bottom-left curve

            # ----- Bottom Left Corner -----
            x1, y2,       # bottom-left control point
            x1, y2-r,     # move upward along left edge

            # ----- Left Edge -----
            x1, y1+r,     # stop before top-left curve

            # ----- Top Left Corner -----
            x1, y1        # closing point of polygon
        ]

        # Draw shape
        self.rect = self.create_polygon(
            points,
            smooth=True,      # this creates rounded corners
            fill="black",     # button body color
            outline="white",  # white border
            width=2
        )

    # When button is clicked
    def on_click(self, event):
        if self.command:
            self.command()

    # Hover effect
    def on_hover(self, event):
        self.itemconfig(self.rect, outline="cyan")

    # Mouse leaves button
    def on_leave(self, event):
        self.itemconfig(self.rect, outline="white")


class AI_Debugger:
    def __init__(self,root):
        self.root = root
        self.root.title("AI Debugger")
        self.root.geometry("1200x675")
        self.text = "AI-Debugger --> \n"
        self.code = ""
        self.Buttons()

        # Display label
        main_frame = Frame(self.root, bg="black")
        main_frame.pack(fill="both", expand=True)

        self.editor = Text(main_frame, bg="#1e1e1e", fg="yellow", font=("Consolas", 12), width=40)
        self.editor.pack(side="left", fill="both", expand=True)

        self.output = Text(main_frame, bg="black", fg="white", font=("Consolas", 12), width=60)
        self.output.pack(side="right", fill="both", expand=True)


    def highlight_code(self, widget):

        # Get all text from the widget
        code = widget.get("1.0", "end")

        # Remove previous highlighting
        for tag in widget.tag_names():
            widget.tag_delete(tag)

        index = "1.0"

        # Tokenize the code using Pygments
        for token, content in lex(code, PythonLexer()):

            end_index = f"{index}+{len(content)}c"

            tag = None

            if token in Token.Keyword:
                tag = "keyword"

            elif token in Token.String:
                tag = "string"

            elif token in Token.Comment:
                tag = "comment"

            elif token in Token.Name.Function:
                tag = "function"

            if tag:
                widget.tag_add(tag, index, end_index)

            index = end_index

        # Color configuration
        widget.tag_config("keyword", foreground="#569CD6")
        widget.tag_config("string", foreground="#CE9178")
        widget.tag_config("comment", foreground="#6A9955")
        widget.tag_config("function", foreground="#DCDCAA")

    def openFile(self):
        filepath = filedialog.askopenfilename(initialdir=".",
                                            title="Open File",
                                            filetypes = (("All Files","*.*"),
                                                    ("Python File","*.py"),
                                                    ("HTML File","*.html"),
                                                    ("JavaScript File","*.js"),
                                                    ("C++ File","*.cpp"),
                                                    ("Java File","*.java"),
                                                    ("HtML File","*.html"),
                                                    ("CSS File","*.css")))
        with open(filepath, "r", encoding="utf-8") as filetext:
            self.code = filetext.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", self.code)
            self.highlight_code(self.editor)

    def save_file(self):
        file = filedialog.asksaveasfile(
            defaultextension=".*",
            filetypes=[
                ("All Files","*.*"),
                ("Python File","*.py"),
                ("HTML File","*.html"),
                ("JavaScript File","*.js"),
                ("C++ File","*.cpp"),
                ("Java File","*.java"),
                ("HtML File","*.html"),
                ("CSS File","*.css")
            ]
        )
        if file:
            file.write(self.editor.get("1.0", "end"))
            file.close()

    def clear(self):
        self.text = ""
        self.output.delete("1.0", "end") # Clear the text widget 
        self.output.see("end")                   

    def Debug(self):
        try:
            selected_code = self.editor.selection_get()
        except:
            selected_code = self.editor.get("1.0", "end")

        prompt = f"""Read the following code: {selected_code} line by line.
                    Return your answer in this format:
                    1. Language detected
                    2. Bugs found
                    3. Explanation
                    4. Corrected code."""
        
        stream = ollama.chat(
            model="codegemma:7b",
            messages = [{"role": "user", "content": prompt}],
            stream = True
         )
        response_text = ""

        for chunk in stream:
            self.text = chunk["message"]["content"]
            self.output.insert("end", self.text) # Insert the response text into the text widget
            self.output.see("end")                   # Auto-scroll to the end of the text widget
            self.output.update_idletasks()           # Update the text widget to reflect changes
            
        self.highlight_code(self.output)

    def Explain(self):
        try:
            selected_code = self.editor.selection_get()
        except:
            selected_code = self.editor.get("1.0", "end")

        prompt = f"""Read the following code: {selected_code} line by line.
                    explain what the code does as well as runs in detail,
                    following this format:
                    1. Language detected
                    2. Summary of code
                    3. Explanation of code
                    4. Output of code."""
        
        stream = ollama.chat(
            model="codegemma:7b",
            messages = [{"role": "user", "content": prompt}],
            stream = True
         )
        response_text = ""

        for chunk in stream:
            self.text = chunk["message"]["content"]
            self.output.insert("end", self.text) # Insert the response text into the text widget
            self.output.see("end")                   # Auto-scroll to the end of the text widget
            self.output.update_idletasks()           # Update the text widget to reflect changes

    def Buttons(self):

        # Bottom toolbar frame
        self.button_frame = Frame(self.root, bg="black")
        self.button_frame.pack(side="bottom", fill="x", pady=7)

        # Open button
        open_btn = RoundedButton(
            self.button_frame,
            "Open",
            command=self.openFile
        )
        open_btn.pack(side="left", padx=25)

        # Debug button
        debug_btn = RoundedButton(
            self.button_frame,
            "Debug",
            command=self.Debug
        )
        debug_btn.pack(side="left", padx=25)

        # Save button
        save_btn = RoundedButton(
            self.button_frame,
            "Save",
            command=self.save_file
        )
        save_btn.pack(side="left", padx=25)

        # Clear button
        clear_btn = RoundedButton(
            self.button_frame,
            "Clear",
            command=self.clear 
        )
        clear_btn.pack(side="left", padx=25)

        # Explain button
        explain_btn = RoundedButton(
            self.button_frame,
            "Explain",
            command=self.Explain
        )
        explain_btn.pack(side="left", padx=25)


# ------------------------
# -------Run App----------
# ------------------------

root = Tk()
app = AI_Debugger(root)
root.mainloop()  