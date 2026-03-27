import customtkinter as ctk
import re
from decimal import Decimal
import math

ctk.set_appearance_mode("dark")

# =========================
# LÓGICA DE FORMATAÇÃO (Visual)
# =========================
def formatar_para_display(valor_string):
    """Transforma '1500.5' em '1.500,5' apenas para exibição"""
    if not valor_string or valor_string in "+-*/÷×":
        return valor_string
    
    try:
        # Se houver um ponto (decimal interno), separamos
        if "." in valor_string:
            inteiro, decimal = valor_string.split(".")
        else:
            inteiro, decimal = valor_string, None

        # Formata o milhar no inteiro (1500 -> 1.500)
        # Usamos o padrão de trocar vírgula por ponto para o padrão BR
        inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
        
        if decimal is not None:
            # Retorna com a vírgula visual
            return f"{inteiro_formatado},{decimal}"
        
        # Se a string termina em ponto (usuário acabou de clicar na vírgula)
        if valor_string.endswith("."):
            return inteiro_formatado + ","
            
        return inteiro_formatado
    except:
        return valor_string

def formatar_expressao_completa(expressao):
    """Formata todos os números dentro de uma conta (ex: 1500+500)"""
    # Regex que identifica números (inteiros ou decimais com ponto)
    return re.sub(r"\d+(\.\d+)?", lambda m: formatar_para_display(m.group(0)), expressao)

# =========================
# ESTADO E CÁLCULO
# =========================
expr_interna = "0" # Aqui guardamos 1500.5 (padrão Python)

def calcular_resultado():
    global expr_interna
    try:
        # O eval precisa de pontos para decimais e não pode ter pontos de milhar
        # Nossa expr_interna já está nesse formato
        resultado = eval(expr_interna, {"__builtins__": None}, {"math": math, "Decimal": Decimal})
        
        # Formata o número para string sem notação científica
        res_str = format(float(resultado), ".10f").rstrip('0').rstrip('.')
        return res_str
    except:
        return ""

def atualizar_interface(finalizar=False):
    global expr_interna
    
    # 1. Display de cima (Sempre formatado com pontos e vírgula visual)
    display_visual = formatar_expressao_completa(expr_interna)
    display_visual = display_visual.replace("*", "×").replace("/", "÷")
    display_var.set(display_visual)

    # 2. Display de baixo (Resultado em tempo real)
    if not finalizar and any(op in expr_interna for op in "+-*/"):
        res = calcular_resultado()
        if res:
            result_var.set(formatar_para_display(res))
        else:
            result_var.set("")
    elif finalizar:
        result_var.set("")

# =========================
# AÇÕES
# =========================
def add_num(num):
    global expr_interna
    if expr_interna == "0":
        expr_interna = str(num)
    else:
        expr_interna += str(num)
    atualizar_interface()

def add_op(op):
    global expr_interna
    if expr_interna[-1] in "+-*/.":
        expr_interna = expr_interna[:-1]
    expr_interna += op
    atualizar_interface()

def btn_virgula():
    global expr_interna
    # Pegamos apenas o último número sendo digitado
    partes = re.split(r"[\+\-\*\/]", expr_interna)
    ultimo_num = partes[-1]
    
    # Só adiciona o ponto interno se o número atual não tiver um
    if "." not in ultimo_num:
        expr_interna += "."
    atualizar_interface()

def limpar():
    global expr_interna
    expr_interna = "0"
    result_var.set("")
    atualizar_interface()

def apagar():
    global expr_interna
    if len(expr_interna) > 1:
        expr_interna = expr_interna[:-1]
    else:
        expr_interna = "0"
    atualizar_interface()

def btn_igual():
    global expr_interna
    res = calcular_resultado()
    if res:
        expr_interna = res
        atualizar_interface(finalizar=True)

# =========================
# INTERFACE (UI)
# =========================
app = ctk.CTk()
app.title("Calculadora Pro")
app.geometry("360x640")

display_var = ctk.StringVar(value="0")
result_var = ctk.StringVar(value="")

# Área dos Displays
frame_tela = ctk.CTkFrame(app, fg_color="transparent")
frame_tela.pack(fill="x", padx=20, pady=(40, 20))

ctk.CTkLabel(frame_tela, textvariable=display_var, font=("Arial", 45, "bold"), anchor="e").pack(fill="x")
ctk.CTkLabel(frame_tela, textvariable=result_var, font=("Arial", 24), text_color="#888", anchor="e").pack(fill="x")

# Grade de Botões
frame_grid = ctk.CTkFrame(app, fg_color="transparent")
frame_grid.pack(expand=True, fill="both", padx=10, pady=10)

def criar_btn(txt, r, c, cmd, cor="#333", span=1):
    btn = ctk.CTkButton(frame_grid, text=txt, font=("Arial", 22), fg_color=cor, 
                        hover_color="#555", height=70, corner_radius=15, command=cmd)
    btn.grid(row=r, column=c, columnspan=span, sticky="nsew", padx=5, pady=5)

for i in range(4): frame_grid.columnconfigure(i, weight=1)
for i in range(5): frame_grid.rowconfigure(i, weight=1)

# Layout
criar_btn("AC", 0, 0, limpar, "#A5A5A5")
criar_btn("⌫", 0, 1, apagar, "#A5A5A5")
criar_btn("%", 0, 2, lambda: add_op("/100"), "#A5A5A5")
criar_btn("÷", 0, 3, lambda: add_op("/"), "#FF9500")

criar_btn("7", 1, 0, lambda: add_num(7))
criar_btn("8", 1, 1, lambda: add_num(8))
criar_btn("9", 1, 2, lambda: add_num(9))
criar_btn("×", 1, 3, lambda: add_op("*"), "#FF9500")

criar_btn("4", 2, 0, lambda: add_num(4))
criar_btn("5", 2, 1, lambda: add_num(5))
criar_btn("6", 2, 2, lambda: add_num(6))
criar_btn("-", 2, 3, lambda: add_op("-"), "#FF9500")

criar_btn("1", 3, 0, lambda: add_num(1))
criar_btn("2", 3, 1, lambda: add_num(2))
criar_btn("3", 3, 2, lambda: add_num(3))
criar_btn("+", 3, 3, lambda: add_op("+"), "#FF9500")

criar_btn("0", 4, 0, lambda: add_num(0), span=2)
criar_btn(",", 4, 2, btn_virgula)
criar_btn("=", 4, 3, btn_igual, "#FF9500")

app.mainloop()