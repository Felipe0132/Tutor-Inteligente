import plotly.graph_objects as go
import streamlit as st

def renderizar_grafico_matematico(dados_grafico):
    x = dados_grafico.get("x", [])
    y = dados_grafico.get("y", [])
    funcao = dados_grafico.get("funcao", "f(x)")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x, 
        y=y,
        mode="lines",
        name=f"y = {funcao}",
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.update_layout(
        title=f"Gráfico: $y = {funcao}$",
        xaxis_title="Eixo X",
        yaxis_title="Eixo Y",
        xaxis=dict(
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=1,
            showgrid=True,
        ),
        yaxis=dict(
            zeroline=True,
            zerolinecolor='gray',
            zerolinewidth=1,
            showgrid=True,
            dtick=1 
        ),
        template="plotly_white"
    )

    return fig