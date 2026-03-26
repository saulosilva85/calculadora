import customtkinter as ctk
import math
import re
from decimal import Decimal, getcontext

getcontext().prec = 20

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =========================
# ESTADOS
# =========================
display_expr = "0"
calc_expr = "0"
cientifico_visivel = False
ultimo_resultado = "0"

# =========================
# FORMATAÇÃO BR
# =========================
def formatar_numero_br(numero):
    try:
        numero = str(numero)

        termina_virgula = numero.endswith(",")

        if "," in numero:
            inteiro, decimal = numero.split(",", 1)
        else:
            inteiro, decimal = numero, ""

        inteiro = re.sub(r"\D", "", inteiro)

        if inteiro == "":
            inteiro = "0"

        inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")

        if termina_virgula:
            return inteiro_formatado + ","

        if decimal:
            return inteiro_formatado + "," + decimal

        return inteiro_formatado

    except:
        return numero

def formatar_expressao(expr):
    partes = re.split(r'(\+|\-|\*|\/|\(|\))', expr)
    resultado = []

    for parte in partes:
        if re.fullmatch(r'[0-9,]+', parte) or parte.endswith(","):
            resultado.append(formatar_numero_br(parte))
        else:
            resultado.append(parte)

    return "".join(resultado)

# =========================
# CALCULO COM DECIMAL
# =========================
def calcular_decimal(expr):
    try:
        expr = expr.replace(",", ".")
        numeros = re.findall(r'\d+\.\d+|\d+', expr)

        for num in numeros:
            expr = expr.replace(num, f'Decimal("{num}")')

        return eval(expr)
    except:
        return None

# =========================
# ATUALIZA TELA
# =========================
def atualizar_tela():
    global ultimo_resultado

    entrada.set(formatar_expressao(display_expr))

    if display_expr.endswith(","):
        resultado_label.configure(text=ultimo_resultado)
        return

    try:
        expr = calc_expr

        expr = expr.replace("^", "**")
        expr = expr.replace("√", "math.sqrt")
        expr = expr.replace("sin", "math.sin")
        expr = expr.replace("cos", "math.cos")
        expr = expr.replace("tan", "math.tan")
        expr = expr.replace("log", "math.log10")
        expr = expr.replace("ln", "math.log")

        resultado = calcular_decimal(expr)

        if resultado is None:
            return

        resultado_str = format(resultado, "f").rstrip("0").rstrip(".")
        resultado_str = resultado_str.replace(".", ",")

        resultado_formatado = formatar_numero_br(resultado_str)

        ultimo_resultado = resultado_formatado
        resultado_label.configure(text=resultado_formatado)

    except:
        resultado_label.configure(text=ultimo_resultado)

# =========================
# BOTÕES
# =========================
def adicionar(valor):
    global display_expr, calc_expr

    if display_expr == "0":
        display_expr = valor
        calc_expr = valor
    else:
        display_expr += valor
        calc_expr += valor

    atualizar_tela()

def operador(op):
    global display_expr, calc_expr
    display_expr += op
    calc_expr += op
    atualizar_tela()

def virgula():
    global display_expr, calc_expr

    partes = re.split(r'[\+\-\*/\(\)]', display_expr)
    ultimo = partes[-1]

    if "," not in ultimo:
        display_expr += ","
        calc_expr += "."

    atualizar_tela()

def limpar():
    global display_expr, calc_expr, ultimo_resultado
    display_expr = "0"
    calc_expr = "0"
    ultimo_resultado = "0"
    atualizar_tela()

def apagar():
    global display_expr, calc_expr

    if len(display_expr) > 1:
        display_expr = display_expr[:-1]
        calc_expr = calc_expr[:-1]
    else:
        display_expr = "0"
        calc_expr = "0"

    atualizar_tela()

def toggle_cientifico():
    global cientifico_visivel
    cientifico_visivel = not cientifico_visivel

    if cientifico_visivel:
        frame_cientifico.pack(expand=True, fill="both")
    else:
        frame_cientifico.pack_forget()

# =========================
# INTERFACE
# =========================
app = ctk.CTk()
app.title("Calculadora")
app.geometry("400x700")

entrada = ctk.StringVar(value="0")

display = ctk.CTkEntry(
    app,
    textvariable=entrada,
    font=("Arial", 28),
    justify="right",
    height=60
)
display.pack(fill="both", padx=10, pady=(10, 0))

resultado_label = ctk.CTkLabel(
    app,
    text="0",
    font=("Arial", 20),
    anchor="e"
)
resultado_label.pack(fill="both", padx=15, pady=(0, 10))

# =========================
# BOTÕES
# =========================
frame = ctk.CTkFrame(app)
frame.pack(expand=True, fill="both")

botoes = [
    ["C", "⌫", "SCI", "/"],
    ["7", "8", "9", "*"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ","]
]

for linha in botoes:
    row = ctk.CTkFrame(frame)
    row.pack(expand=True, fill="both")

    for item in linha:
        def comando(x=item):
            if x == "C":
                limpar()
            elif x == "⌫":
                apagar()
            elif x == "SCI":
                toggle_cientifico()
            elif x == ",":
                virgula()
            elif x in "+-*/":
                operador(x)
            else:
                adicionar(x)

        ctk.CTkButton(row, text=item, command=comando).pack(
            side="left", expand=True, fill="both", padx=5, pady=5
        )

# =========================
# CIENTÍFICO
# =========================
frame_cientifico = ctk.CTkFrame(app)

botoes_cientificos = [
    ["(", ")", "%"],
    ["sin", "cos", "tan"],
    ["log", "ln", "√"],
    ["π", "e", "^"],
    ["x²"]
]

for linha in botoes_cientificos:
    row = ctk.CTkFrame(frame_cientifico)
    row.pack(expand=True, fill="both")

    for item in linha:
        def comando(x=item):
            if x == "x²":
                adicionar("**2")
            else:
                adicionar(x)

        ctk.CTkButton(row, text=item, command=comando).pack(
            side="left", expand=True, fill="both", padx=5, pady=5
        )

frame_cientifico.pack_forget()

atualizar_tela()
app.mainloop()