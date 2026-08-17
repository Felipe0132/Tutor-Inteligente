import sympy as sp
import numpy as np
import plotly.graph_objects as go

t = sp.symbols('t')

def processar_pedido(tipo, expr_x, expr_y, t_min, t_max, ponto=None):
    """
    tipo: 'funcao', 'limite' ou 'derivada'
    expr_x: variavel em x
    expr_y: implicita
    t_min/t_max: intervalo
    ponto: usado só em limite/derivada (o x onde acontece)
    """

    sym_x = sp.sympify(expr_x)
    sym_y = sp.sympify(expr_y)
    fx = sp.lambdify(t, sym_x, 'numpy')
    fy = sp.lambdify(t, sym_y, 'numpy')

    fig = go.Figure()
    fig.update_yaxes(scaleanchor="x", scaleratio=1)

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

fig1 = processar_pedido("funcao", expr_x="t", expr_y="t**2", t_min=-5, t_max=5)
fig1.show()

fig2 = processar_pedido("funcao", expr_x="3*cos(t)", expr_y="3*sin(t)", t_min=0, t_max=2*np.pi)
fig2.show()