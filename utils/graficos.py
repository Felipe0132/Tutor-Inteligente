import sympy as sp
import numpy as np
import plotly.graph_objects as go

t = sp.symbols('t')
x = sp.symbols('x')

def processar_pedido(grafico):
    """
    tipo: 'funcao', 'limite' ou 'derivada'
    expr_x: variavel em x
    expr_y: implicita
    t_min/t_max: intervalo
    ponto: usado só em limite/derivada (o x onde acontece)
    """

    tipo = grafico.get("tipo", "funcao")
    expr_x = str(grafico.get("expr_x") or "t")
    expr_y = str(grafico.get("expr_y") or "t")

    raw_t_min = grafico.get("t_min")
    if raw_t_min is None or str(raw_t_min).strip() == "":
        raw_t_min = -5

    raw_t_max = grafico.get("t_max")
    if raw_t_max is None or str(raw_t_max).strip() == "":
        raw_t_max = 5

    t_min = float(sp.sympify(raw_t_min))
    t_max = float(sp.sympify(raw_t_max))

    ponto_raw = grafico.get("ponto")
    ponto = sp.sympify(ponto_raw) if (ponto_raw is not None and str(ponto_raw).strip() != "") else None

    sym_x = sp.sympify(expr_x, convert_xor=True).subs(x, t) # Forca x virar t
    sym_y = sp.sympify(expr_y, convert_xor=True).subs(x, t)
    
    fx = sp.lambdify(t, sym_x, 'numpy')
    fy = sp.lambdify(t, sym_y, 'numpy')

t = sp.symbols('t')
x = sp.symbols('x')

def processar_pedido(grafico):
    """
    tipo: 'funcao', 'limite' ou 'derivada'
    expr_x: variavel em x
    expr_y: implicita
    t_min/t_max: intervalo
    ponto: usado só em limite/derivada (o x onde acontece)
    """

    tipo = grafico.get("tipo", "funcao")
    expr_x = str(grafico.get("expr_x") or "t")
    expr_y = str(grafico.get("expr_y") or "t")

    raw_t_min = grafico.get("t_min")
    if raw_t_min is None or str(raw_t_min).strip() == "":
        raw_t_min = -5

    raw_t_max = grafico.get("t_max")
    if raw_t_max is None or str(raw_t_max).strip() == "":
        raw_t_max = 5

    t_min = float(sp.sympify(raw_t_min))
    t_max = float(sp.sympify(raw_t_max))

    ponto_raw = grafico.get("ponto")
    ponto = sp.sympify(ponto_raw) if (ponto_raw is not None and str(ponto_raw).strip() != "") else None

    sym_x = sp.sympify(expr_x, convert_xor=True).subs(x, t) # Forca x virar t
    sym_y = sp.sympify(expr_y, convert_xor=True).subs(x, t)
    
    fx = sp.lambdify(t, sym_x, 'numpy')
    fy = sp.lambdify(t, sym_y, 'numpy')

    fig = go.Figure()
    fig.update_xaxes(
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="rgba(255, 255, 255, 0.7)",  # Linha do eixo Y (onde x=0)
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.2)",
    )

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="rgba(255, 255, 255, 0.7)",  # Linha do eixo X (onde y=0)
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.2)",
    )

    ts = np.linspace(t_min, t_max, 400) # Quantos pontos no intervalo
    xs = np.array(fx(ts)) # Vetor com todos os resultados
    ys = np.array(fy(ts))

    if xs.ndim == 0: xs = np.full_like(ts, xs)
    if ys.ndim == 0: ys = np.full_like(ts, ys) # Exemplo: x(t)=3, retorna um escalavel 0, nao um array

    fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name=f"({expr_x}, {expr_y})"))

    if tipo == "funcao":
        fig.update_layout(title=f"Curva Paramétrica: x(t)={expr_x}, y(t)={expr_y}")

    elif tipo == "limite" and ponto is not None:
        lim_x = float(sp.limit(sym_x, t, ponto))
        lim_y = float(sp.limit(sym_y, t, ponto))
        
        fig.add_trace(go.Scatter(
            x=[lim_x], y=[lim_y],
            mode='markers', marker=dict(size=12, color='red'),
            name=f"t → {ponto} : ({lim_x:.2f}, {lim_y:.2f})"
        ))
        fig.update_layout(title=f"Limite quando t → {ponto} = ({lim_x:.2f}, {lim_y:.2f})")

    elif tipo == "derivada" and ponto is not None:
        dx_dt = sp.diff(sym_x, t)
        dy_dt = sp.diff(sym_y, t)

        # Coordenadas do ponto no plano cartesiano
        x0 = float(sym_x.subs(t, ponto))
        y0 = float(sym_y.subs(t, ponto))
        
        # Inclinação dy/dx = (dy/dt) / (dx/dt)
        dx_val = float(dx_dt.subs(t, ponto))
        dy_val = float(dy_dt.subs(t, ponto))
        inclinacao = dy_val / dx_val

        # Reta tangente: y = y0 + m * (x - x0)
        tangente = y0 + inclinacao * (xs - x0)
        
        fig.add_trace(go.Scatter(x=xs, y=tangente, mode='lines',
                                 line=dict(dash='dash'), name="Reta Tangente"))
        fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='markers',
                                 marker=dict(size=12, color='red'),
                                 name=f"Ponto ({x0:.2f}, {y0:.2f}) | m = {inclinacao:.2f}"))
        fig.update_layout(title=f"Derivada em t = {ponto} → Inclinação dy/dx = {inclinacao:.2f}")
    fig.update_xaxes(
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="rgba(255, 255, 255, 0.7)",  # Linha do eixo Y (onde x=0)
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.2)",
    )

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="rgba(255, 255, 255, 0.7)",  # Linha do eixo X (onde y=0)
        showgrid=True,
        gridcolor="rgba(128, 128, 128, 0.2)",
    )

    ts = np.linspace(t_min, t_max, 400) # Quantos pontos no intervalo
    xs = np.array(fx(ts)) # Vetor com todos os resultados
    ys = np.array(fy(ts))

    if xs.ndim == 0: xs = np.full_like(ts, xs)
    if ys.ndim == 0: ys = np.full_like(ts, ys) # Exemplo: x(t)=3, retorna um escalavel 0, nao um array

    fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name=f"({expr_x}, {expr_y})"))

    if tipo == "funcao":
        fig.update_layout(title=f"Curva Paramétrica: x(t)={expr_x}, y(t)={expr_y}")

    elif tipo == "limite" and ponto is not None:
        lim_x = float(sp.limit(sym_x, t, ponto))
        lim_y = float(sp.limit(sym_y, t, ponto))
        
        fig.add_trace(go.Scatter(
            x=[lim_x], y=[lim_y],
            mode='markers', marker=dict(size=12, color='red'),
            name=f"t → {ponto} : ({lim_x:.2f}, {lim_y:.2f})"
        ))
        fig.update_layout(title=f"Limite quando t → {ponto} = ({lim_x:.2f}, {lim_y:.2f})")

    elif tipo == "derivada" and ponto is not None:
        dx_dt = sp.diff(sym_x, t)
        dy_dt = sp.diff(sym_y, t)

        # Coordenadas do ponto no plano cartesiano
        x0 = float(sym_x.subs(t, ponto))
        y0 = float(sym_y.subs(t, ponto))
        
        # Inclinação dy/dx = (dy/dt) / (dx/dt)
        dx_val = float(dx_dt.subs(t, ponto))
        dy_val = float(dy_dt.subs(t, ponto))
        inclinacao = dy_val / dx_val

        # Reta tangente: y = y0 + m * (x - x0)
        tangente = y0 + inclinacao * (xs - x0)
        
        fig.add_trace(go.Scatter(x=xs, y=tangente, mode='lines',
                                 line=dict(dash='dash'), name="Reta Tangente"))
        fig.add_trace(go.Scatter(x=[x0], y=[y0], mode='markers',
                                 marker=dict(size=12, color='red'),
                                 name=f"Ponto ({x0:.2f}, {y0:.2f}) | m = {inclinacao:.2f}"))
        fig.update_layout(title=f"Derivada em t = {ponto} → Inclinação dy/dx = {inclinacao:.2f}")

    return fig
