import json
import re
from typing import Literal

import numpy as np
import sympy as sp
import plotly.graph_objects as go
from pydantic import BaseModel, Field, ConfigDict, ValidationError


# ============================================================
# SÍMBOLOS
# ============================================================

t = sp.symbols("t")
x = sp.symbols("x")
y = sp.symbols("y")


# ============================================================
# MODELOS PYDANTIC
# ============================================================

class FunctionElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["function"]

    expr_x: str
    expr_y: str

    t_min: str = "-5"
    t_max: str = "5"

    label: str | None = None


class PointElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["point"]

    x: str
    y: str | None = None
    y_from: str | None = None

    label: str | None = None
    highlight: bool = False


class AreaElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["area"]

    upper_ref: str | None = None
    lower_ref: str | None = None

    upper: str | None = None
    lower: str | None = None

    x_start: str
    x_end: str

    label: str | None = None


class LineElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["line"]

    equation: str | None = None

    point: list[str] | None = None
    slope: str | None = None

    label: str | None = None


class SegmentElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["segment"]

    x1: str
    y1: str
    x2: str
    y2: str

    label: str | None = None


class CircleElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["circle"]

    center: list[str]
    radius: str

    # Podem ser fornecidos pela IA, mas o renderer também
    # consegue gerar automaticamente.
    expr_x: str | None = None
    expr_y: str | None = None

    t_min: str = "0"
    t_max: str = "2*pi"

    label: str | None = None


class TangentElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["tangent"]

    function_ref: str | None = None
    function: str | None = None

    at: str

    label: str | None = None
    highlight: bool = False


class CircleTangentElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["circle_tangent"]

    circle_ref: str
    point: list[str]

    label: str | None = None
    highlight: bool = False


class SecantElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["secant"]

    function_ref: str | None = None
    function: str | None = None

    x1: str
    x2: str

    label: str | None = None


class VerticalLineElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["vertical_line"]

    x: str
    label: str | None = None


class HorizontalLineElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["horizontal_line"]

    y: str
    label: str | None = None


class AnnotationElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["annotation"]

    x: str
    y: str
    text: str


class IntersectionElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    type: Literal["intersection"]

    objects: list[str]

    label: str | None = None
    highlight: bool = True


GraphElement = (
    FunctionElement
    | PointElement
    | AreaElement
    | LineElement
    | SegmentElement
    | CircleElement
    | TangentElement
    | CircleTangentElement
    | SecantElement
    | VerticalLineElement
    | HorizontalLineElement
    | AnnotationElement
    | IntersectionElement
)


class Graph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tipo: Literal[
        "funcao",
        "derivada",
        "limite",
        "geometria",
        "parametrica",
        "multiplas_funcoes"
    ]

    x_range: list[str] = Field(default_factory=lambda: ["-5", "5"])
    y_range: list[str] = Field(default_factory=lambda: ["-5", "5"])

    elements: list[GraphElement]


# ============================================================
# UTILITÁRIOS
# ============================================================

def parse_expr(expr: str):
    """
    Converte uma expressão textual em SymPy.

    A variável utilizada pelo renderer é t.
    Também aceita x para facilitar a comunicação com a IA.
    """

    expr = str(expr).strip()

    expr = expr.replace("^", "**")

    return sp.sympify(
        expr,
        locals={
            "x": x,
            "y": y,
            "t": t,
            "pi": sp.pi,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "asin": sp.asin,
            "acos": sp.acos,
            "atan": sp.atan,
            "sqrt": sp.sqrt,
            "exp": sp.exp,
            "log": sp.log,
            "ln": sp.log,
        }
    )


def eval_float(expr):
    """
    Avalia uma expressão numérica.
    """

    return float(sp.N(parse_expr(expr)))


def extrair_grafico(texto: str) -> dict:
    """
    Extrai o JSON entre <grafico> e </grafico>.
    """

    if not isinstance(texto, str):
        raise TypeError("O gráfico deve ser recebido como string.")

    padrao = r"<grafico>\s*(.*?)\s*</grafico>"

    match = re.search(padrao, texto, re.DOTALL | re.IGNORECASE)

    if not match:
        raise ValueError(
            "A resposta da IA não contém <grafico>...</grafico>."
        )

    json_texto = match.group(1).strip()

    try:
        return json.loads(json_texto)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"JSON inválido dentro de <grafico>: {e}"
        ) from e


def avaliar_curva(element, valores_t):
    """
    Avalia expr_x e expr_y para um vetor de parâmetros.
    """

    expr_x = parse_expr(element.expr_x)
    expr_y = parse_expr(element.expr_y)

    fx = sp.lambdify(t, expr_x, "numpy")
    fy = sp.lambdify(t, expr_y, "numpy")

    xs = np.asarray(fx(valores_t), dtype=float)
    ys = np.asarray(fy(valores_t), dtype=float)

    if xs.ndim == 0:
        xs = np.full_like(valores_t, xs)

    if ys.ndim == 0:
        ys = np.full_like(valores_t, ys)

    return xs, ys


def intervalo(element):
    """
    Obtém o intervalo paramétrico.
    """

    inicio = eval_float(element.t_min)
    fim = eval_float(element.t_max)

    return inicio, fim


def obter_funcao_y(element):
    """
    Obtém a função y=f(x) de um elemento.

    Para uma função cartesiana normal:
        expr_x = t
        expr_y = x**2

    retornamos:
        f(x) = x**2
    """

    expr_x = parse_expr(element.expr_x)
    expr_y = parse_expr(element.expr_y)

    # Caso cartesiano normal:
    # x(t)=t
    if sp.simplify(expr_x - t) == 0:
        return expr_y.subs(t, x)

    raise ValueError(
        f"O elemento '{element.id}' não representa "
        "uma função cartesiana y=f(x)."
    )


def encontrar_elemento(graph, ref):
    """
    Localiza um elemento pelo ID.
    """

    for element in graph.elements:
        if element.id == ref:
            return element

    raise ValueError(
        f"Elemento referenciado '{ref}' não encontrado."
    )


# ============================================================
# RENDER
# ============================================================

def render_function(fig, element):
    inicio, fim = intervalo(element)

    ts = np.linspace(inicio, fim, 800)

    xs, ys = avaliar_curva(element, ts)

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            name=element.label or element.id or "Função",
            connectgaps=False,
        )
    )


def render_point(fig, element):
    x0 = eval_float(element.x)

    if element.y is not None:
        y0 = eval_float(element.y)

    elif element.y_from is not None:
        expr = parse_expr(element.y_from)
        y0 = float(expr.subs(x, x0))

    else:
        raise ValueError(
            "Um ponto precisa possuir 'y' ou 'y_from'."
        )

    tamanho = 14 if element.highlight else 9

    fig.add_trace(
        go.Scatter(
            x=[x0],
            y=[y0],
            mode="markers+text" if element.label else "markers",
            text=[element.label] if element.label else None,
            textposition="top center",
            marker=dict(
                size=tamanho
            ),
            name=element.label or "Ponto",
        )
    )


def render_area(fig, element, graph):
    # --------------------------------------------------------
    # Determina função superior
    # --------------------------------------------------------

    if element.upper_ref:
        upper_element = encontrar_elemento(
            graph,
            element.upper_ref
        )

        upper_expr = obter_funcao_y(upper_element)

    elif element.upper is not None:
        upper_expr = parse_expr(element.upper)

    else:
        raise ValueError(
            "Área precisa de 'upper' ou 'upper_ref'."
        )

    # --------------------------------------------------------
    # Determina função inferior
    # --------------------------------------------------------

    if element.lower_ref:
        lower_element = encontrar_elemento(
            graph,
            element.lower_ref
        )

        lower_expr = obter_funcao_y(lower_element)

    elif element.lower is not None:
        lower_expr = parse_expr(element.lower)

    else:
        raise ValueError(
            "Área precisa de 'lower' ou 'lower_ref'."
        )

    x1 = eval_float(element.x_start)
    x2 = eval_float(element.x_end)

    valores_x = np.linspace(x1, x2, 500)

    f_upper = sp.lambdify(x, upper_expr, "numpy")
    f_lower = sp.lambdify(x, lower_expr, "numpy")

    valores_upper = np.asarray(
        f_upper(valores_x),
        dtype=float
    )

    valores_lower = np.asarray(
        f_lower(valores_x),
        dtype=float
    )

    fig.add_trace(
        go.Scatter(
            x=np.concatenate([
                valores_x,
                valores_x[::-1]
            ]),
            y=np.concatenate([
                valores_upper,
                valores_lower[::-1]
            ]),
            fill="toself",
            mode="lines",
            line=dict(width=0),
            name=element.label or "Área",
            hoverinfo="skip",
        )
    )


def render_line(fig, element, graph):
    if element.equation is not None:

        expr = parse_expr(element.equation)

        valores_x = np.linspace(
            eval_float(graph.x_range[0]),
            eval_float(graph.x_range[1]),
            500
        )

        f = sp.lambdify(x, expr, "numpy")

        valores_y = np.asarray(
            f(valores_x),
            dtype=float
        )

    elif element.point is not None and element.slope is not None:

        x0 = eval_float(element.point[0])
        y0 = eval_float(element.point[1])
        m = eval_float(element.slope)

        valores_x = np.linspace(
            eval_float(graph.x_range[0]),
            eval_float(graph.x_range[1]),
            500
        )

        valores_y = y0 + m * (valores_x - x0)

    else:
        raise ValueError(
            "Linha precisa de 'equation' ou "
            "'point' + 'slope'."
        )

    fig.add_trace(
        go.Scatter(
            x=valores_x,
            y=valores_y,
            mode="lines",
            name=element.label or "Reta",
        )
    )


def render_segment(fig, element):
    fig.add_trace(
        go.Scatter(
            x=[
                eval_float(element.x1),
                eval_float(element.x2)
            ],
            y=[
                eval_float(element.y1),
                eval_float(element.y2)
            ],
            mode="lines",
            name=element.label or "Segmento",
        )
    )


def render_circle(fig, element):
    x0 = eval_float(element.center[0])
    y0 = eval_float(element.center[1])
    radius = eval_float(element.radius)

    valores_t = np.linspace(
        eval_float(element.t_min),
        eval_float(element.t_max),
        600
    )

    xs = x0 + radius * np.cos(valores_t)
    ys = y0 + radius * np.sin(valores_t)

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            name=element.label or "Círculo",
        )
    )


def render_tangent(fig, element, graph):
    # --------------------------------------------------------
    # Obtém a função
    # --------------------------------------------------------

    if element.function_ref:

        function_element = encontrar_elemento(
            graph,
            element.function_ref
        )

        f = obter_funcao_y(function_element)

    elif element.function:

        f = parse_expr(element.function)

    else:
        raise ValueError(
            "Tangente precisa de 'function_ref' "
            "ou 'function'."
        )

    a = eval_float(element.at)

    derivada = sp.diff(f, x)

    y0 = float(sp.N(f.subs(x, a)))
    inclinacao = float(sp.N(derivada.subs(x, a)))

    x_min = eval_float(graph.x_range[0])
    x_max = eval_float(graph.x_range[1])

    valores_x = np.linspace(
        x_min,
        x_max,
        500
    )

    valores_y = y0 + inclinacao * (
        valores_x - a
    )

    fig.add_trace(
        go.Scatter(
            x=valores_x,
            y=valores_y,
            mode="lines",
            line=dict(dash="dash"),
            name=(
                element.label
                or f"Tangente em x = {a:g}"
            ),
        )
    )

    # Ponto de tangência

    fig.add_trace(
        go.Scatter(
            x=[a],
            y=[y0],
            mode="markers+text",
            text=[
                element.label
                or f"({a:g}, {y0:g})"
            ],
            textposition="top center",
            marker=dict(size=13),
            name="Ponto de tangência",
        )
    )


def render_circle_tangent(fig, element, graph):
    circle = encontrar_elemento(
        graph,
        element.circle_ref
    )

    cx = eval_float(circle.center[0])
    cy = eval_float(circle.center[1])

    px = eval_float(element.point[0])
    py = eval_float(element.point[1])

    # Vetor raio
    rx = px - cx
    ry = py - cy

    # A tangente é perpendicular ao raio.
    # Um vetor diretor da tangente é (-ry, rx).

    dx = -ry
    dy = rx

    if abs(dx) < 1e-12 and abs(dy) < 1e-12:
        raise ValueError(
            "O ponto da tangente não pode ser o centro do círculo."
        )

    x_min = eval_float(graph.x_range[0])
    x_max = eval_float(graph.x_range[1])

    # Parametrização da reta
    escala = 20

    s = np.linspace(
        -escala,
        escala,
        300
    )

    xs = px + dx * s
    ys = py + dy * s

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            line=dict(dash="dash"),
            name=element.label or "Tangente",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[px],
            y=[py],
            mode="markers",
            marker=dict(size=13),
            name="Ponto de tangência",
        )
    )


def render_secant(fig, element, graph):
    if element.function_ref:

        function_element = encontrar_elemento(
            graph,
            element.function_ref
        )

        f = obter_funcao_y(function_element)

    elif element.function:

        f = parse_expr(element.function)

    else:
        raise ValueError(
            "Secante precisa de 'function_ref' "
            "ou 'function'."
        )

    x1 = eval_float(element.x1)
    x2 = eval_float(element.x2)

    y1 = float(sp.N(f.subs(x, x1)))
    y2 = float(sp.N(f.subs(x, x2)))

    if abs(x2 - x1) < 1e-12:
        raise ValueError(
            "Os pontos da secante não podem possuir o mesmo x."
        )

    inclinacao = (y2 - y1) / (x2 - x1)

    valores_x = np.linspace(
        eval_float(graph.x_range[0]),
        eval_float(graph.x_range[1]),
        500
    )

    valores_y = y1 + inclinacao * (
        valores_x - x1
    )

    fig.add_trace(
        go.Scatter(
            x=valores_x,
            y=valores_y,
            mode="lines",
            line=dict(dash="dot"),
            name=element.label or "Secante",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[x1, x2],
            y=[y1, y2],
            mode="markers",
            marker=dict(size=11),
            name="Pontos da secante",
        )
    )


def render_vertical_line(fig, element):
    x0 = eval_float(element.x)

    fig.add_vline(
        x=x0,
        line_dash="dash",
        annotation_text=element.label
    )


def render_horizontal_line(fig, element):
    y0 = eval_float(element.y)

    fig.add_hline(
        y=y0,
        line_dash="dash",
        annotation_text=element.label
    )


def render_annotation(fig, element):
    fig.add_annotation(
        x=eval_float(element.x),
        y=eval_float(element.y),
        text=element.text,
        showarrow=True,
    )


def render_intersection(fig, element, graph):
    """
    Atualmente suporta interseção entre duas funções
    cartesianas y=f(x).
    """

    if len(element.objects) != 2:
        raise ValueError(
            "A interseção atualmente precisa de exatamente "
            "dois objetos."
        )

    obj1 = encontrar_elemento(
        graph,
        element.objects[0]
    )

    obj2 = encontrar_elemento(
        graph,
        element.objects[1]
    )

    f1 = obter_funcao_y(obj1)
    f2 = obter_funcao_y(obj2)

    equacao = sp.Eq(f1, f2)

    solucoes = sp.solve(equacao, x)

    pontos_x = []
    pontos_y = []

    for solucao in solucoes:

        if solucao.is_real is False:
            continue

        try:
            x_val = float(sp.N(solucao))
            y_val = float(sp.N(f1.subs(x, solucao)))

            pontos_x.append(x_val)
            pontos_y.append(y_val)

        except (TypeError, ValueError):
            continue

    if not pontos_x:
        return

    fig.add_trace(
        go.Scatter(
            x=pontos_x,
            y=pontos_y,
            mode="markers+text",
            text=[
                element.label or "Interseção"
            ] * len(pontos_x),
            textposition="top center",
            marker=dict(size=13),
            name=element.label or "Interseções",
        )
    )


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def processar_grafico(texto_grafico: str):
    """
    Recebe a resposta da IA contendo:

        <grafico>
        {
            ...
        }
        </grafico>

    Valida o JSON e gera o gráfico Plotly.
    """

    # --------------------------------------------------------
    # 1. Extrair JSON
    # --------------------------------------------------------

    dados = extrair_grafico(texto_grafico)

    # --------------------------------------------------------
    # 2. Validar estrutura
    # --------------------------------------------------------

    try:
        graph = Graph.model_validate(dados)

    except ValidationError as e:
        raise ValueError(
            "Estrutura do gráfico inválida:\n"
            + str(e)
        ) from e

    # --------------------------------------------------------
    # 3. Criar figura
    # --------------------------------------------------------

    fig = go.Figure()

    # --------------------------------------------------------
    # 4. Renderizar elementos
    # --------------------------------------------------------

    for element in graph.elements:

        if element.type == "function":
            render_function(fig, element)

        elif element.type == "point":
            render_point(fig, element)

        elif element.type == "area":
            render_area(fig, element, graph)

        elif element.type == "line":
            render_line(fig, element, graph)

        elif element.type == "segment":
            render_segment(fig, element)

        elif element.type == "circle":
            render_circle(fig, element)

        elif element.type == "tangent":
            render_tangent(fig, element, graph)

        elif element.type == "circle_tangent":
            render_circle_tangent(
                fig,
                element,
                graph
            )

        elif element.type == "secant":
            render_secant(
                fig,
                element,
                graph
            )

        elif element.type == "vertical_line":
            render_vertical_line(
                fig,
                element
            )

        elif element.type == "horizontal_line":
            render_horizontal_line(
                fig,
                element
            )

        elif element.type == "annotation":
            render_annotation(
                fig,
                element
            )

        elif element.type == "intersection":
            render_intersection(
                fig,
                element,
                graph
            )

    # --------------------------------------------------------
    # 5. Configuração dos eixos
    # --------------------------------------------------------

    x_min = eval_float(graph.x_range[0])
    x_max = eval_float(graph.x_range[1])

    y_min = eval_float(graph.y_range[0])
    y_max = eval_float(graph.y_range[1])

    fig.update_xaxes(
        range=[x_min, x_max],
        zeroline=True,
        zerolinewidth=2,
        showgrid=True,
        gridcolor="rgba(128,128,128,0.2)",
    )

    fig.update_yaxes(
        range=[y_min, y_max],
        scaleanchor="x",
        scaleratio=1,
        zeroline=True,
        zerolinewidth=2,
        showgrid=True,
        gridcolor="rgba(128,128,128,0.2)",
    )

    fig.update_layout(
        template="plotly_dark",
        hovermode="closest",
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),
        legend=dict(
            orientation="h"
        ),
    )

    return fig