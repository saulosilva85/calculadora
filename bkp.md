import customtkinter as ctk
import re
from decimal import Decimal
import math

ctk.set_appearance_mode("dark")

# =========================
# LÓGICA DE FORMATAÇÃO (Visual)
# =========================
def formatar_para_display(valor_string):
    """Transforma '1500.' em '1.500,' imediatamente"""
    if not valor_string or any(op in valor_string for op in "+-*/÷×"):
        return valor_string
    
    try:
        # Detecta o ponto decimal interno
        if "." in valor_string:
            partes = valor_string.split(".")
            inteiro = partes[0]
            # Se houver números após o ponto, eles são o decimal. Se não, é vazio.
            decimal = partes[1] if len(partes) > 1 else ""
        else:
            inteiro, decimal = valor_string, None

        # Formata milhar (1500 -> 1.500)
        try:
            inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
        except:
            inteiro_formatado = inteiro
        
        # Se decimal não for None, significa que o usuário clicou na vírgula
        if decimal is not None:
            return f"{inteiro_formatado},{decimal}"
            
        return inteiro_formatado
    except:
        return valor_string

def formatar_expressao_completa(expressao):
    """Formata números e garante espaços entre operadores (Estilo Android)"""
    # 1. Adiciona espaços para o visual não ficar "junto"
    visual = expressao.replace("*", " × ").replace("/", " ÷ ").replace("+", " + ").replace("-", " - ")
    
    # 2. REGEX CORRIGIDA: \d+\.?\d* captura o número mesmo se terminar em ponto
    return re.sub(r"\d+\.?\d*", lambda m: formatar_para_display(m.group(0)), visual)

# =========================
# ESTADO E CÁLCULO
# =========================
expr_interna = "0" 

def calcular_resultado():
    global expr_interna
    try:
        limpa = expr_interna
        # Remove ponto ou operador solto no final para não dar erro no eval
        if limpa.endswith("."): limpa = limpa[:-1]
        while limpa and limpa[-1] in "+-*/": limpa = limpa[:-1]
        
        if not limpa or limpa == "0": return ""
        
        resultado = eval(limpa, {"__builtins__": None}, {"math": math, "Decimal": Decimal})
        
        # Formata resultado final limpo
        res_str = format(float(resultado), ".10f").rstrip('0').rstrip('.')
        return res_str if res_str != "" else "0"
    except:
        return ""

def atualizar_interface(finalizar=False):
    global expr_interna
    
    # Display principal com formatação instantânea
    display_visual = formatar_expressao_completa(expr_interna)
    display_var.set(display_visual)

    # Display de resultado (baixo) com espaçamento Android
    if not finalizar and any(op in expr_interna for op in "+-*/"):
        res = calcular_resultado()
        if res:
            result_var.set(formatar_para_display(res))
        else:
            result_var.set("")
    else:
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
    # Pega o último número da sequência
    partes = re.split(r"[\+\-\*\/]", expr_interna)
    ultimo_num = partes[-1]
    
    if "." not in ultimo_num:
        expr_interna += "."
    atualizar_interface()

def limpar():
    global expr_interna
    expr_interna = "0"
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
app.geometry("380x680")

display_var = ctk.StringVar(value="0")
result_var = ctk.StringVar(value="")

# Área dos Displays (Margens Android)
frame_tela = ctk.CTkFrame(app, fg_color="transparent")
frame_tela.pack(fill="x", padx=25, pady=(60, 20))

ctk.CTkLabel(frame_tela, textvariable=display_var, font=("Arial", 48, "bold"), anchor="e").pack(fill="x")
ctk.CTkLabel(frame_tela, textvariable=result_var, font=("Arial", 26), text_color="#777", anchor="e").pack(fill="x", pady=(15, 0))

# Grade de Botões
frame_grid = ctk.CTkFrame(app, fg_color="transparent")
frame_grid.pack(expand=True, fill="both", padx=15, pady=15)

def criar_btn(txt, r, c, cmd, cor="#333", span=1):
    btn = ctk.CTkButton(frame_grid, text=txt, font=("Arial", 24), fg_color=cor, 
                        hover_color="#444", height=75, corner_radius=20, command=cmd)
    btn.grid(row=r, column=c, columnspan=span, sticky="nsew", padx=6, pady=6)

for i in range(4): frame_grid.columnconfigure(i, weight=1)
for i in range(5): frame_grid.rowconfigure(i, weight=1)

# Layout dos Botões
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