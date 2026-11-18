#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt


# ----------------------------- Dados -----------------------------
T_AMB_C = 20.0  # Temperatura do ar em graus Celsius.
T_ALVO_C = 100.0  # Temperatura desejada na face superior da placa.

LARGURA = 260e-3  # Dimensao horizontal da placa em metros.
COMPRIMENTO = 147e-3  # Dimensao horizontal da placa em metros.
AREA_PLACA = LARGURA * COMPRIMENTO  # Area da face superior da placa em m^2.
AREA_AQUECEDOR = 8060 * 10e-6  # Area ocupada pelos dois aquecedores em m^2.
PERIMETRO = 2 * (LARGURA + COMPRIMENTO)  # Perimetro usado para calcular a area lateral.

# Cada item contem:
# (nome da camada, espessura em m, condutividade termica em W/(m*K)).
CAMADAS = [
    ("Pasta termica", 50e-6, 7.5),
    ("Placa 1", 8e-3, 167.0),
    ("Placa 2", 1e-3, 0.403),
]

SIGMA = 5.670374419e-8  # Constante de Stefan-Boltzmann em W/(m^2*K^4).
EMISSIVIDADE = 0.30  # Emissividade superficial usada para a troca de calor por radiacao.


# ----------------------------- Convecção ------------------------
def propriedades_ar(temperatura_k):
    """Calcula propriedades do ar a pressao atmosferica."""
    pressao = 101325.0  # Pressao atmosferica em Pa.
    constante_ar = 287.05  # Constante especifica do ar seco em J/(kg*K).
    densidade = pressao / (constante_ar * temperatura_k)  # kg/m^3.
    viscosidade = 1.458e-6 * temperatura_k**1.5 / (temperatura_k + 110.4)  # Pa*s.
    cp = 1007.0  # Calor especifico do ar em J/(kg*K).
    condutividade = 0.0263 * (temperatura_k / 300.0)**0.87  # W/(m*K).
    viscosidade_cinematica = viscosidade / densidade  # Viscosidade cinematica em m^2/s.
    difusividade = condutividade / (densidade * cp)  # Difusividade termica em m^2/s.
    prandtl = viscosidade_cinematica / difusividade  # Numero adimensional de Prandtl.
    expansao = 1.0 / temperatura_k  # Coeficiente aproximado de expansao volumetrica.
    return viscosidade_cinematica, difusividade, condutividade, prandtl, expansao


def conveccao_natural(temperatura_superficie_k, orientacao, comprimento_k):
    """Estima o coeficiente de conveccao natural em W/(m^2*K)."""
    temperatura_media = (temperatura_superficie_k + T_AMB_C + 273.15) / 2
    nu, alpha, k_ar, prandtl, beta = propriedades_ar(temperatura_media)
    delta_t = abs(temperatura_superficie_k - (T_AMB_C + 273.15))

    # Numero de Rayleigh: relaciona conveccao natural, gravidade e diferenca de temperatura.
    rayleigh = 9.81 * beta * delta_t * comprimento_k**3 / (nu * alpha)

    if orientacao == "topo":
        # Placa horizontal com a face quente voltada para cima.
        nu_adimensional = 0.54 * rayleigh**0.25 if rayleigh < 1e7 else 0.15 * rayleigh**(1/3)
    elif orientacao == "fundo":
        # Placa horizontal com a face quente voltada para baixo.
        nu_adimensional = 0.27 * rayleigh**0.25
    else:
        # Parede vertical: correlacao de Churchill-Chu.
        termo = 0.387 * rayleigh**(1/6)
        nu_adimensional = (
            0.825 + termo / (1 + (0.492 / prandtl)**(9/16))**(8/27)
        )**2

    # h = Nu*k/L; Nu representa a razao entre conveccao e conducao no ar.
    return nu_adimensional * k_ar / comprimento_k


def radiacao(temperatura_superficie_k):
    """Calcula o coeficiente linearizado de radiacao em W/(m^2*K)."""
    temperatura_inf_k = T_AMB_C + 273.15
    return EMISSIVIDADE * SIGMA * (
        temperatura_superficie_k**2 + temperatura_inf_k**2
    ) * (temperatura_superficie_k + temperatura_inf_k)


# ----------------------------- Calculo --------------------------
def estimar_q(retornar_temperaturas=False):
    """Resolve iterativamente a rede termica e retorna q em W e W/m^2."""
    temperatura_inf_k = T_AMB_C + 273.15  # Temperatura do ambiente em kelvin.
    temperatura_alvo_k = T_ALVO_C + 273.15  # Temperatura fixa na face superior.
    n_nos = len(CAMADAS) + 1  # Um no para a face inferior e um no em cada interface.
    temperaturas = np.full(n_nos, temperatura_alvo_k)  # Valores inicializados em 100 C.
    # Altura total usada como comprimento caracteristico das faces laterais.
    altura_total = sum(espessura for _, espessura, _ in CAMADAS)
    # Comprimento caracteristico para a superficie horizontal superior.
    comprimento_topo = AREA_PLACA / PERIMETRO

    for _ in range(500):
        condutancia = np.zeros((n_nos, n_nos))  # Matriz de conducao entre os nos.
        perdas = np.zeros(n_nos)  # Perdas do no para o ambiente.

        for i, (_, espessura, condutividade) in enumerate(CAMADAS):
            # R = t/(k*A), portanto G = k*A/t.
            g = condutividade * AREA_PLACA / espessura
            # O mesmo G aparece com sinais opostos entre dois nos adjacentes.
            condutancia[i, i] += g
            condutancia[i + 1, i + 1] += g
            condutancia[i, i + 1] -= g
            condutancia[i + 1, i] -= g

        # Conveccao natural somada a radiacao linearizada na face superior.
        h_topo = conveccao_natural(
            temperaturas[-1], "topo", comprimento_topo
        ) + radiacao(temperaturas[-1])
        perdas[-1] += h_topo * AREA_PLACA

        for i, (_, espessura, _) in enumerate(CAMADAS):
            # Cada camada lateral usa a media das temperaturas dos dois nos.
            temperatura_media = (temperaturas[i] + temperaturas[i + 1]) / 2
            h_lateral = conveccao_natural(
                temperatura_media, "lateral", altura_total
            ) + radiacao(temperatura_media)
            area_lateral = PERIMETRO * espessura
            # A perda lateral concentrada e dividida entre os dois extremos da camada.
            perdas[i] += 0.5 * h_lateral * area_lateral
            perdas[i + 1] += 0.5 * h_lateral * area_lateral

        matriz = condutancia + np.diag(perdas)  # Matriz termica completa.
        indices = list(range(n_nos - 1))

        sistema = np.zeros((n_nos, n_nos))
        rhs = np.zeros(n_nos)
        for i in range(n_nos):
            for j, indice in enumerate(indices):
                sistema[i, j] = matriz[i, indice]
            # Coluna adicional usada como a incognita da potencia q no aquecedor.
            sistema[i, n_nos - 1] = -1.0 if i == 0 else 0.0
            rhs[i] = perdas[i] * temperatura_inf_k - matriz[i, -1] * temperatura_alvo_k

        solucao = np.linalg.solve(sistema, rhs)
        novas_temperaturas = np.full(n_nos, temperatura_alvo_k)
        novas_temperaturas[:-1] = solucao[:-1]
        novo_q = solucao[-1]  # Potencia fornecida pelo aquecedor em watts.

        # Para de calcular quando a temperatura dos nos deixa de variar.
        if np.max(np.abs(novas_temperaturas - temperaturas)) < 1e-9:
            temperaturas = novas_temperaturas
            q = novo_q
            break
        temperaturas = novas_temperaturas

    # Retorna a potencia total e a potencia por unidade de area do aquecedor.
    fluxo = q / AREA_AQUECEDOR

    h_topo = conveccao_natural(
        temperaturas[-1], "topo", comprimento_topo
    ) + radiacao(temperaturas[-1])
    h_laterais = []
    altura_total = sum(espessura for _, espessura, _ in CAMADAS)
    for i, (_, espessura, _) in enumerate(CAMADAS):
        temperatura_media = (temperaturas[i] + temperaturas[i + 1]) / 2
        h_lateral = conveccao_natural(
            temperatura_media, "lateral", altura_total
        ) + radiacao(temperatura_media)
        h_laterais.append(h_lateral)

    if retornar_temperaturas:
        return q, fluxo, temperaturas, h_topo, h_laterais
    return q, fluxo


def nomes_nos():
    """Retorna o significado fisico de cada no da rede termica."""
    nomes = ["N0 - Face inferior da pasta termica"]
    for i, (nome_camada, _, _) in enumerate(CAMADAS[:-1], start=1):
        nomes.append(
            f"N{i} - Interface {nome_camada} / {CAMADAS[i][0]}"
        )
    nomes.append(f"N{len(CAMADAS)} - Face superior da {CAMADAS[-1][0]}")
    return nomes


def plotar_temperaturas_nos(temperaturas):
    """Plota a temperatura de cada no com seu respectivo nome."""
    temperaturas_c = temperaturas - 273.15
    nomes = nomes_nos()

    indices = np.arange(len(nomes))
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.plot(
        indices,
        temperaturas_c,
        marker="o",
        markersize=8,
        linewidth=2,
        color="#4C78A8",
        label="Temperatura do no",
    )

    ax.set_xticks(indices)
    ax.set_xticklabels(nomes, rotation=20, ha="right")
    ax.set_xlabel("No da rede termica")
    ax.set_ylabel("Temperatura (C)")
    ax.set_title("Temperaturas em cada no da rede termica")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend()

    amplitude = np.max(temperaturas_c) - np.min(temperaturas_c)
    offset = max(amplitude * 0.03, 0.5)
    for indice, temperatura in zip(indices, temperaturas_c):
        ax.text(
            indice,
            temperatura + offset,
            f"{temperatura:.2f} C",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig("temperaturas_nos.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    # Executa o calculo e mostra os resultados na tela.
    q, fluxo, temperaturas, h_topo, h_laterais = estimar_q(
        retornar_temperaturas=True
    )
    temperaturas_c = temperaturas - 273.15
    print(f"Temperatura do alvo: {T_ALVO_C:.1f} C")
    print(f"Potencia estimada (q): {q:.3f} W")
    print(f"Densidade de potencia: {fluxo:.1f} W/m^2")
    print(f"h da face superior: {h_topo:.3f} W/(m^2*K)")
    print("\nCoeficientes h das faces laterais:")
    for (nome_camada, _, _), h_lateral in zip(CAMADAS, h_laterais):
        print(f"{nome_camada}: {h_lateral:.3f} W/(m^2*K)")
    print("\nTemperaturas dos nos:")
    for nome, temperatura in zip(nomes_nos(), temperaturas_c):
        print(f"{nome}: {temperatura:.3f} C")
    plotar_temperaturas_nos(temperaturas)
