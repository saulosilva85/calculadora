import customtkinter as ctk
import re
from decimal import Decimal
import math

ctk.set_appearance_mode("dark")

# =========================
# LÓGICA DE FORMATAÇÃO
# =========================
def formatar_para_display(valor_string):
    if not valor_string or any(op in valor_string for op in "+-*/÷×%"):
        return valor_string
    
    try:
        if "." in valor_string:
            partes = valor_string.split(".")
            inteiro = partes[0]
            decimal = partes[1] if len(partes) > 1 else ""
        else:
            inteiro, decimal = valor_string, None

        inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
        
        if decimal is not None:
            return f"{inteiro_formatado},{decimal}"
        return inteiro_formatado
    except:
        return valor_string

def formatar_expressao_completa(expressao):
    # Substitui operadores para o visual Android com espaços
    visual = expressao.replace("*", " × ").replace("/", " ÷ ").replace("+", " + ").replace("-", " - ")
    # Garante que o % apareça colado ao número
    visual = visual.replace("%", "%")
    
    return re.sub(r"\d+\.?\d*", lambda m: formatar_para_display(m.group(0)), visual)

# =========================
# LÓGICA DE PORCENTAGEM E CÁLCULO
# =========================
def processar_porcentagem(expr):
    """
    Transforma '1000-10%' em '1000-(1000*0.1)'
    ou '50%' em '50/100'
    """
    pattern = r"(\d+\.?\d*)\s*([\+\-\*\/])\s*(\d+\.?\d*)%"
    match = re.search(pattern, expr)
    
    if match:
        base = match.group(1)
        op = match.group(2)
        porcentagem = match.group(3)
        # Lógica: Valor +/- (Valor * percentual/100)
        nova_expr = f"{base}{op}({base}*({porcentagem}/100))"
        return nova_expr
    
    # Caso seja apenas um número seguido de % (ex: 50%)
    return re.sub(r"(\d+\.?\d*)%", r"(\1/100)", expr)

def calcular_resultado():
    global expr_interna
    try:
        limpa = expr_interna
        if limpa.endswith("."): limpa = limpa[:-1]
        
        # Processa a lógica de porcentagem antes de calcular
        if "%" in limpa:
            limpa = processar_porcentagem(limpa)
            
        # Remove operadores soltos no final
        while limpa and limpa[-1] in "+-*/": limpa = limpa[:-1]
        
        if not limpa or limpa == "0": return ""
        
        resultado = eval(limpa, {"__builtins__": None}, {"math": math, "Decimal": Decimal})
        
        res_str = format(float(resultado), ".10f").rstrip('0').rstrip('.')
        return res_str if res_str != "" else "0"
    except:
        return ""

# =========================
# AÇÕES
# =========================
expr_interna = "0"

def atualizar_interface(finalizar=False):
    display_visual = formatar_expressao_completa(expr_interna)
    display_var.set(display_visual)

    if not finalizar and any(op in expr_interna for op in "+-*/%"):
        res = calcular_resultado()
        result_var.set(formatar_para_display(res) if res else "")
    else:
        result_var.set("")

def add_num(num):
    global expr_interna
    if expr_interna == "0": expr_interna = str(num)
    else: expr_interna += str(num)
    atualizar_interface()

def add_op(op):
    global expr_interna
    if expr_interna == "0" and op == "-": expr_interna = "-"
    elif expr_interna[-1] in "+-*/%.":
        expr_interna = expr_interna[:-1] + op
    else:
        expr_interna += op
    atualizar_interface()

def btn_porcentagem():
    global expr_interna
    if expr_interna[-1].isdigit():
        expr_interna += "%"
    atualizar_interface()

def btn_virgula():
    global expr_interna
    partes = re.split(r"[\+\-\*\/%]", expr_interna)
    if "." not in partes[-1]:
        expr_interna += "."
    atualizar_interface()

def limpar():
    global expr_interna
    expr_interna = "0"
    atualizar_interface()

def apagar():
    global expr_interna
    expr_interna = expr_interna[:-1] if len(expr_interna) > 1 else "0"
    atualizar_interface()

def btn_igual():
    global expr_interna
    res = calcular_resultado()
    if res:
        expr_interna = res
        atualizar_interface(finalizar=True)

# =========================
# UI
# =========================
app = ctk.CTk()
app.title("Calculadora Corrigida")
app.geometry("380x680")

display_var = ctk.StringVar(value="0")
result_var = ctk.StringVar(value="")

frame_tela = ctk.CTkFrame(app, fg_color="transparent")
frame_tela.pack(fill="x", padx=25, pady=(60, 20))

ctk.CTkLabel(frame_tela, textvariable=display_var, font=("Arial", 48, "bold"), anchor="e").pack(fill="x")
ctk.CTkLabel(frame_tela, textvariable=result_var, font=("Arial", 26), text_color="#777", anchor="e").pack(fill="x", pady=(15, 0))

frame_grid = ctk.CTkFrame(app, fg_color="transparent")
frame_grid.pack(expand=True, fill="both", padx=15, pady=15)

def criar_btn(txt, r, c, cmd, cor="#333", span=1):
    btn = ctk.CTkButton(frame_grid, text=txt, font=("Arial", 24), fg_color=cor, 
                        hover_color="#444", height=75, corner_radius=20, command=cmd)
    btn.grid(row=r, column=c, columnspan=span, sticky="nsew", padx=6, pady=6)

for i in range(4): frame_grid.columnconfigure(i, weight=1)
for i in range(5): frame_grid.rowconfigure(i, weight=1)

criar_btn("AC", 0, 0, limpar, "#888")
criar_btn("⌫", 0, 1, apagar, "#888")
criar_btn("%", 0, 2, btn_porcentagem, "#888")
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