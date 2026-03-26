import customtkinter as ctk
import re
from decimal import Decimal

ctk.set_appearance_mode("dark")

APP_WIDTH = 360
APP_HEIGHT = 640

# =========================
# ESTADO
# =========================
expr_display = "0"
expr_calc = "0"
ultimo_resultado = "0"
modo_cientifico = False

# =========================
# FORMATAÇÃO
# =========================
def formatar_br(valor):
    try:
        valor = str(valor)
        termina_virgula = valor.endswith(",")

        if "," in valor:
            inteiro, decimal = valor.split(",", 1)
        else:
            inteiro, decimal = valor, ""

        inteiro = re.sub(r"\D", "", inteiro)
        if inteiro == "":
            inteiro = "0"

        inteiro = f"{int(inteiro):,}".replace(",", ".")

        if termina_virgula:
            return inteiro + ","

        if decimal:
            return inteiro + "," + decimal

        return inteiro
    except:
        return valor

# =========================
# CALCULO CORRETO (FIX TOTAL)
# =========================
def calcular():
    try:
        expr = expr_calc.replace(",", ".")

        # 🔥 CONVERTE TODOS OS NÚMEROS (inteiros + decimais)
        def converter(match):
            return f'Decimal("{match.group(0)}")'

        expr = re.sub(r'\d+(\.\d+)?', converter, expr)

        resultado = eval(expr, {"Decimal": Decimal})

        res = format(resultado, "f").rstrip("0").rstrip(".")
        res = res.replace(".", ",")

        return formatar_br(res)

    except:
        return ultimo_resultado

# =========================
# ATUALIZA
# =========================
def atualizar():
    global ultimo_resultado

    display_var.set(formatar_br(expr_display))

    # bloqueia cálculo incompleto
    if expr_display.endswith(",") or expr_display[-1] in "+-*/":
        result_var.set(ultimo_resultado)
        return

    res = calcular()
    ultimo_resultado = res
    result_var.set(res)

# =========================
# AÇÕES
# =========================
def add(v):
    global expr_display, expr_calc

    if expr_display == "0":
        expr_display = v
        expr_calc = v
    else:
        expr_display += v
        expr_calc += v

    atualizar()

def op(o):
    global expr_display, expr_calc

    if expr_display[-1] in "+-*/":
        expr_display = expr_display[:-1]
        expr_calc = expr_calc[:-1]

    expr_display += o
    expr_calc += o

    atualizar()

def virgula():
    global expr_display, expr_calc

    partes = re.split(r'[\+\-\*/\(\)]', expr_display)
    ultimo = partes[-1]

    if "," not in ultimo:
        expr_display += ","
        expr_calc += "."

    atualizar()

def limpar():
    global expr_display, expr_calc, ultimo_resultado
    expr_display = "0"
    expr_calc = "0"
    ultimo_resultado = "0"
    atualizar()

def apagar():
    global expr_display, expr_calc

    if len(expr_display) > 1:
        expr_display = expr_display[:-1]
        expr_calc = expr_calc[:-1]
    else:
        expr_display = "0"
        expr_calc = "0"

    atualizar()

# =========================
# SCI
# =========================
def toggle_cientifico():
    global modo_cientifico

    modo_cientifico = not modo_cientifico

    if modo_cientifico:
        frame_cientifico.pack(fill="x", padx=10, pady=5)
    else:
        frame_cientifico.pack_forget()

# =========================
# UI
# =========================
app = ctk.CTk()
app.geometry("900x700")

container = ctk.CTkFrame(app, width=APP_WIDTH, height=APP_HEIGHT, fg_color="#000")
container.place(relx=0.5, rely=0.5, anchor="center")

display_var = ctk.StringVar(value="0")
result_var = ctk.StringVar(value="0")

ctk.CTkLabel(container, textvariable=display_var, font=("Arial", 36), anchor="e").pack(fill="x", padx=20, pady=(40,10))
ctk.CTkLabel(container, textvariable=result_var, font=("Arial", 18), anchor="e", text_color="#aaa").pack(fill="x", padx=20)

frame = ctk.CTkFrame(container, fg_color="#000")
frame.pack(expand=True, fill="both", padx=10, pady=10)

for i in range(5):
    frame.rowconfigure(i, weight=1)
for j in range(4):
    frame.columnconfigure(j, weight=1)

def botao(txt, cor, cmd, r, c, cs=1):
    ctk.CTkButton(
        frame,
        text=txt,
        fg_color=cor,
        corner_radius=40,
        font=("Arial", 20),
        command=cmd
    ).grid(row=r, column=c, columnspan=cs, sticky="nsew", padx=5, pady=5)

NUM = "#333"
TOP = "#a5a5a5"
OP = "#ff9500"

botao("AC", TOP, limpar, 0, 0)
botao("⌫", TOP, apagar, 0, 1)
botao("SCI", TOP, toggle_cientifico, 0, 2)
botao("÷", OP, lambda: op("/"), 0, 3)

botao("7", NUM, lambda: add("7"), 1, 0)
botao("8", NUM, lambda: add("8"), 1, 1)
botao("9", NUM, lambda: add("9"), 1, 2)
botao("×", OP, lambda: op("*"), 1, 3)

botao("4", NUM, lambda: add("4"), 2, 0)
botao("5", NUM, lambda: add("5"), 2, 1)
botao("6", NUM, lambda: add("6"), 2, 2)
botao("-", OP, lambda: op("-"), 2, 3)

botao("1", NUM, lambda: add("1"), 3, 0)
botao("2", NUM, lambda: add("2"), 3, 1)
botao("3", NUM, lambda: add("3"), 3, 2)
botao("+", OP, lambda: op("+"), 3, 3)

botao("0", NUM, lambda: add("0"), 4, 0, 2)
botao(",", NUM, virgula, 4, 2)
botao("=", OP, atualizar, 4, 3)

# =========================
# CIENTÍFICO
# =========================
frame_cientifico = ctk.CTkFrame(container, fg_color="#111")

def criar_linha(itens):
    row = ctk.CTkFrame(frame_cientifico, fg_color="#111")
    row.pack(fill="x")
    for item in itens:
        def comando(x=item):
            if x == "√":
                add("math.sqrt(")
            elif x == "^":
                add("**")
            elif x == "π":
                add(str(3.1415926535))
            elif x == "e":
                add(str(2.718281828))
            else:
                add(x)

        ctk.CTkButton(row, text=item, command=comando).pack(
            side="left", expand=True, fill="both", padx=3, pady=3
        )

criar_linha(["(", ")", "%"])
criar_linha(["sin", "cos", "tan"])
criar_linha(["log", "ln", "√"])
criar_linha(["π", "e", "^"])

frame_cientifico.pack_forget()

atualizar()
app.mainloop()