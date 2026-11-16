# Generated from: Ejetor Ar com as coisas.ipynb
# Converted at: 2026-11-10T12:08:46.028Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import numpy as np
import matplotlib.pyplot as plt
import math
from sympy import symbols, solve
from sympy import solveset
from sympy import nsolve



# ==========================================================
# PROPRIEDADES DO AR
# ==========================================================

gamma = 1.4#1.1#Cp/Cv
R = 287 #j/Kg.K - 71.1 (R141-B)

# ==========================================================
# CONDIÇÕES OPERACIONAIS - Bom Vacuo + Nivel de Pressão de Entrada não tão alto + Alto Er
# ==========================================================
#Valor comercial
rho_g = 1.225 #kg/m^3
Vg = 0.79 #N L/s
consumo = rho_g*Vg/1000
#===========================================================
Pg = 0.35e6*1.013     # pressão motriz (Pa) - Pressão até 5 Bar
Tg = 300       # temperatura Entrada (K) Geralmente é uns 400K
Pe = 35*10**3      # pressão sucção (Pa) - 20KPa
Te = 400
eta_p = 0.95
ns = 0.85
phi_p = 0.83
phi_m = 0.8
Cp = 1005 #j/(Kg.K) 786 (R141-B)

#Árvore de Calculo
dt = 1.6*10**-3  #Parametro arbitrario --> Falta decidir ------->Utilizei a do artigo de calculo
At = math.pi*dt**2/4 #Área da garganta do primeiro bocal
m_p = Pg*At/math.sqrt(Tg)*math.sqrt(gamma/R*(2/(gamma+1))**((gamma+1)/(gamma-1)))*math.sqrt(eta_p)
#Analise 
#print("Erro =",abs((m_p-consumo)/consumo))

dp1 = 3*10**-3 #Parametro arbitrario --> Falta decidir ------->Utilizei a do artigo de calculo
Ap1 = math.pi*dp1**2/4
Mp1 = symbols('Mp1')
expr = (Ap1/At)**2 - (1/Mp1**2 *(2/(gamma+1) * (1 + (gamma-1)/2 * Mp1**2))**((gamma+1)/(gamma-1)))
Mp1_sol = nsolve(expr, Mp1, 3)


#Pressão na saida do bocal 1
Pp1 = Pg/(1+(gamma-1)/2*Mp1_sol**2)**(gamma/(gamma-1))

#Sucção
Msy = 1
Psy = Pe/(1+(gamma-1)/2*Msy**2)**(gamma/(gamma-1))
#Psy = Ppy --> Suposição
Ppy = Psy
Mpy = symbols('Mpy')
expr2 = (Ppy/Pp1)-(((1+((gamma-1)/2*Mp1_sol**2))**(gamma/(gamma-1)))/((1+((gamma-1)/2*Mpy**2))**(gamma/(gamma-1))))
Mpy_sol = nsolve(expr2, Mpy,1.8)

#Áreas
Num = (phi_p/Mpy_sol)*(2/(gamma+1)*(1+((gamma-1)/2*Mpy_sol**2)))**((gamma+1)/(2*(gamma-1)))
Den = (1/Mp1_sol)*(2/(gamma+1)*(1+((gamma-1)/2*Mp1_sol**2)))**((gamma+1)/(2*(gamma-1)))
Apy = Ap1*Num/Den
dpy = math.sqrt(Apy*4/math.pi)
d3 = 1*10**(-3)

def razão_d3(d3_c):
    #global dt, Pg, Tg, Pe, Te, np, ns, phi_p, phi_m, Cp, dp1, gamma, R

    try:
        A3_c = math.pi * d3_c**2 / 4 # Usando d3_c
        Asy = A3_c - Apy

        if Asy <= 0: # Área de fluxo secundário 
            return 0.0 # Retorna 0 se a área for inválida

        # Vazão mássica secundária (ms)
        ms = Pe * Asy / math.sqrt(Te) * math.sqrt(gamma / R * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))) * math.sqrt(ns)
        razao = ms / m_p
        return float(razao)
    except Exception as e:
       
        return 0.0 # Retorna 0.0 em caso de erro --> não atendeu à condição
razãoo = 0.1
d3_opt = d3  # Chute inicial 
d_3_passo = 0.00001  # Incrementa de 0.1 mm
max_d3_mm = 50.0  # Limite superior pra não ficar bizarro
d3_s = None #Contagem
razão_s = 0.0

# Iteração para encontrar d3
while d3_opt <= max_d3_mm:
    d3_c_m = d3_opt  # 
    razão_opt = razão_d3(d3_c_m)

    if razão_opt > razãoo:
        d3_s = d3_opt
        razão_s = razão_opt
        break
    d3_opt += d_3_passo

if d3_s is not None:
    d3_status = f"Diâmetro d3 otimizado: {d3_opt * 1000:.2f} mm"
else:
    d3_status = "Não foi possível encontrar um d3 na faixa selecionada."

A3_opt = d3_opt**2/4*math.pi
Asy = A3_opt - Apy
dsy = math.sqrt(Asy*4/math.pi)

#Vazão Sucção
ms = Pe*Asy/math.sqrt(Te)*math.sqrt(gamma/R*(2/(gamma+1))**((gamma+1)/(gamma-1)))*math.sqrt(ns)
#Razão

#Temperatura 
Tpy = Tg/(1+(gamma-1)/2*Mpy_sol**2)
Tsy = Te/(1+(gamma-1)/2*Msy**2)

#
a_py = math.sqrt(gamma*R*Tpy) 
Vpy = Mpy_sol*a_py
a_sy = math.sqrt(gamma*R*Tsy)
Vsy = a_sy*Msy
#Balanço de massa
Vm = phi_m*(m_p*Vpy+ms*Vsy)/(m_p+ms)
#Balanço de Energia
Tm = symbols('Tm')
expr3 = m_p*(Cp*Tpy+Vpy**2/2)+ms*(Cp*Tsy+Vsy**2/2)-(m_p+ms)*(Cp*Tm+Vm**2/2)
Tm_sol = nsolve(expr3, Tm,300)
am = math.sqrt(gamma*R*Tm_sol)
Mm = Vm/am

Pm = Ppy
P3 = Pm*(1+2*gamma/(gamma+1)*(Mm**2-1))
M3 = math.sqrt((1+((gamma-1)/2*Mm**2))/(gamma*Mm**2-((gamma-1)/2)))
#Saida --> Pc é obtido experimentalmente, esse valor é o critico
Pc = P3*(1+(gamma-1)/2*M3**2)**(gamma/gamma-1) # ---> Como já fizemos para ter um omega maximo/Critico não precisa refazer o Loop

print(f"""\
========== RESUMO DOS RESULTADOS ==========
Consumo de ar informado: {consumo:.6g} kg/s
Vazão mássica primária (m_p): {m_p:.6g} kg/s
Área da garganta (At): {At:.6g} m²
Área de saída do bocal 1 (Ap1): {Ap1:.6g} m²
Razão de áreas Ap1/At: {Ap1 / At:.6g}
Número de Mach na saída do bocal 1 (Mp1): {float(Mp1_sol):.6g}
Pressão do fluido primário na saída do bocal 1 (Pp1): {float(Pp1):.6g} Pa
Pressão no encontro dos fluidos (Psy): {float(Psy):.6g} Pa
Número de Mach do fluido primário no encontro (Mpy): {float(Mpy_sol):.6g}
Área do escoamento primário no encontro (Apy): {float(Apy):.6g} m²
Diâmetro primário no encontro (dpy): {dpy * 1000:.6g} mm
{d3_status}
Área da seção de mistura (A3): {A3_opt:.6g} m²
Área do escoamento secundário (Asy): {Asy:.6g} m²
Diâmetro do escoamento secundário (dsy): {dsy * 1000:.6g} mm
Razão de áreas A3/At: {A3_opt / At:.6g}
Vazão mássica secundária (ms): {ms:.6g} kg/s
Razão de arraste (ms/m_p): {ms / m_p:.6g}
Temperatura do fluido primário no encontro (Tpy): {float(Tpy):.6g} K
Temperatura do fluido secundário no encontro (Tsy): {float(Tsy):.6g} K
Velocidade do fluido primário (Vpy): {float(Vpy):.6g} m/s
Velocidade do fluido secundário (Vsy): {float(Vsy):.6g} m/s
Velocidade de mistura (Vm): {float(Vm):.6g} m/s
Temperatura de mistura (Tm): {float(Tm_sol):.6g} K
Número de Mach na mistura (Mm): {float(Mm):.6g}
Pressão de mistura (Pm): {float(Pm):.6g} Pa
Pressão antes da saída (P3): {float(P3):.6g} Pa
Número de Mach na entrada da saída (M3): {M3:.6g}
Pressão crítica calculada (Pc): {float(Pc):.6g} Pa
===========================================""")

import numpy as np
import math
from sympy import symbols, nsolve

def achamento_d3_otimo(pg_val, dt_val, razãoo): 
    global Pe, Te, eta_p, ns, phi_p, phi_m, Cp, dp1, gamma, R, Tg

    try:
        # 1. 
        At = math.pi * dt_val**2 / 4
        if At <= 0: return np.nan

        m_p = pg_val * At / math.sqrt(Tg) * math.sqrt(gamma / R * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))) * math.sqrt(eta_p)
        if m_p <= 0: return np.nan

        Ap1 = math.pi * dp1**2 / 4
        Mp1 = symbols('Mp1')
        expr_mp1 = (Ap1 / At)**2 - (1 / Mp1**2 * (2 / (gamma + 1) * (1 + (gamma - 1) / 2 * Mp1**2))**((gamma + 1) / (gamma - 1)))
        
        # Tenta resolver para Mp1
        try:
            Mp1_sol_raw = nsolve(expr_mp1, Mp1, 3)
        except (ValueError, TypeError):
            try:
                Mp1_sol_raw = nsolve(expr_mp1, Mp1, 1.0)
            except (ValueError, TypeError):
                return np.nan

        Mp1_sol = float(Mp1_sol_raw) if isinstance(Mp1_sol_raw, (float, int)) else float(Mp1_sol_raw)
        if Mp1_sol <= 0 or not math.isfinite(Mp1_sol): return np.nan

        Pp1 = pg_val / (1 + (gamma - 1) / 2 * Mp1_sol**2)**(gamma / (gamma - 1))

        Msy = 1
        Psy = Pe / (1 + (gamma - 1) / 2 * Msy**2)**(gamma / (gamma - 1))
        Ppy = Psy

        Mpy = symbols('Mpy')
        expr_mpy = (Ppy / Pp1) - (((1 + ((gamma - 1) / 2 * Mp1_sol**2))**(gamma / (gamma - 1))) / ((1 + ((gamma - 1) / 2 * Mpy**2))**(gamma / (gamma - 1))))
        
        # Tenta resolver 
        try:
            Mpy_sol_raw = nsolve(expr_mpy, Mpy, 1.8)
        except (ValueError, TypeError):
            try:
                Mpy_sol_raw = nsolve(expr_mpy, Mpy, 0.5)
            except (ValueError, TypeError):
                return np.nan

        Mpy_sol = float(Mpy_sol_raw) if isinstance(Mpy_sol_raw, (float, int)) else float(Mpy_sol_raw)
        if Mpy_sol <= 0 or not math.isfinite(Mpy_sol): return np.nan

        Num = (phi_p / Mpy_sol) * (2 / (gamma + 1) * (1 + ((gamma - 1) / 2 * Mpy_sol**2)))**((gamma + 1) / (2 * (gamma - 1)))
        Den = (1 / Mp1_sol) * (2 / (gamma + 1) * (1 + ((gamma - 1) / 2 * Mp1_sol**2)))**((gamma + 1) / (2 * (gamma - 1)))
        Apy = Ap1 * Num / Den

        # 2. Iterar para encontrar o d3 otimizado
        d3_candidato_mm = 1.0 # Inicia a busca a partir de 1 mm
        d3_incremento_mm = 0.01 # Incrementa de 0.01 mm
        max_d3_mm = 50.0 # Limite superior para d3 (50 mm)

        d3_otimizado_m = np.nan # Inicializa como NaN (Not a Number)

        while d3_candidato_mm <= max_d3_mm:
            d3_candidato_m = d3_candidato_mm / 1000.0 # Converte mm para metros
            A3_candidate = math.pi * d3_candidato_m**2 / 4
            Asy = A3_candidate - Apy

            if Asy > 0: # A área secundária deve ser positiva
                # Calcula a vazão mássica secundária (ms) para o d3_candidate
                ms = Pe * Asy / math.sqrt(Te) * math.sqrt(gamma / R * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))) * math.sqrt(ns)
                razão_atual = ms / m_p

                # Se a razão atual for igual ou maior que a razão alvo, encontramos um d3 válido
                if razão_atual >= razãoo:
                    d3_otimizado_m = d3_candidato_m
                    break # Encontrou o d3, sai do loop
            d3_candidato_mm += d3_incremento_mm

        return d3_otimizado_m # Retorna o d3 em metros

    except Exception as e:
        # print(f"Erro em achamento_d3_otimo para Pg={pg_val/1e3:.0f}kPa, dt={dt_val*1000:.2f}mm: {e}")
        return np.nan # Retorna NaN se ocorrer um erro
                  
     
    


#Plot da influencia da Pg no d3
import matplotlib.pyplot as plt

# Definir os valores de dt para as curvas 
dt_valor_plotm = [1.00,1.5,2,2.5, 3] # 
dt_valor_plot =[d / 1000 for d in dt_valor_plotm] # 

# Faixa de valores de Pg para o gráfico (em Pa)
Pg_range_pa = np.linspace(0.1e6, 1.0e6, 30) # De 100 kPa a 1000 kPa (1 MPa), com 30 pontos

#razãoo = 0.7 # 

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Gerar uma curva para cada dt
for dt_val_m, dt_label_mm in zip(dt_valor_plot, dt_valor_plotm):
    d3_otimizado_mm = []
    for pg_val in Pg_range_pa:
        d3_opt_m = achamento_d3_otimo(pg_val, dt_val_m, razãoo)
        d3_otimizado_mm.append(d3_opt_m * 1000 if not np.isnan(d3_opt_m) else np.nan) # Converte para mm para plotar

    axes[0].plot(Pg_range_pa / 1e3, d3_otimizado_mm, linestyle='-', label=f'dt = {dt_label_mm:.2f} mm')

axes[0].set_title('Diâmetro ótimo d3 vs. pressão motriz Pg')
axes[0].set_xlabel('Pressão motriz Pg (kPa)')
axes[0].set_ylabel('Diâmetro ótimo d3 (mm)')
axes[0].grid(True, linestyle='--', alpha=0.3)
axes[0].legend(title='Diâmetro da garganta (dt)')
axes[0].tick_params(axis='both', which='major')
axes[0].set_ylim(bottom=0)
#plt.savefig("DotimoxPmotriz.png", dpi=300)

def achamento_d3_otimo_Pe(Pe_val, dt_val, razãoo): 
    global Pg, Te, eta_p, ns, phi_p, phi_m, Cp, dp1, gamma, R, Tg

    try:
        # 1. 
        At = math.pi * dt_val**2 / 4
        if At <= 0: return np.nan

        m_p = Pg * At / math.sqrt(Tg) * math.sqrt(gamma / R * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))) * math.sqrt(eta_p)
        if m_p <= 0: return np.nan

        Ap1 = math.pi * dp1**2 / 4
        Mp1 = symbols('Mp1')
        expr_mp1 = (Ap1 / At)**2 - (1 / Mp1**2 * (2 / (gamma + 1) * (1 + (gamma - 1) / 2 * Mp1**2))**((gamma + 1) / (gamma - 1)))
        
        # Tenta resolver para Mp1
        try:
            Mp1_sol_raw = nsolve(expr_mp1, Mp1, 3)
        except (ValueError, TypeError):
            try:
                Mp1_sol_raw = nsolve(expr_mp1, Mp1, 1.0)
            except (ValueError, TypeError):
                return np.nan

        Mp1_sol = float(Mp1_sol_raw) if isinstance(Mp1_sol_raw, (float, int)) else float(Mp1_sol_raw)
        if Mp1_sol <= 0 or not math.isfinite(Mp1_sol): return np.nan

        Pp1 = Pg / (1 + (gamma - 1) / 2 * Mp1_sol**2)**(gamma / (gamma - 1))

        Msy = 1
        Psy = Pe_val / (1 + (gamma - 1) / 2 * Msy**2)**(gamma / (gamma - 1))
        Ppy = Psy

        Mpy = symbols('Mpy')
        expr_mpy = (Ppy / Pp1) - (((1 + ((gamma - 1) / 2 * Mp1_sol**2))**(gamma / (gamma - 1))) / ((1 + ((gamma - 1) / 2 * Mpy**2))**(gamma / (gamma - 1))))
        
        # Tenta resolver 
        try:
            Mpy_sol_raw = nsolve(expr_mpy, Mpy, 1.8)
        except (ValueError, TypeError):
            try:
                Mpy_sol_raw = nsolve(expr_mpy, Mpy, 0.5)
            except (ValueError, TypeError):
                return np.nan

        Mpy_sol = float(Mpy_sol_raw) if isinstance(Mpy_sol_raw, (float, int)) else float(Mpy_sol_raw)
        if Mpy_sol <= 0 or not math.isfinite(Mpy_sol): return np.nan

        Num = (phi_p / Mpy_sol) * (2 / (gamma + 1) * (1 + ((gamma - 1) / 2 * Mpy_sol**2)))**((gamma + 1) / (2 * (gamma - 1)))
        Den = (1 / Mp1_sol) * (2 / (gamma + 1) * (1 + ((gamma - 1) / 2 * Mp1_sol**2)))**((gamma + 1) / (2 * (gamma - 1)))
        Apy = Ap1 * Num / Den

        # 2. Iterar para encontrar o d3 otimizado
        d3_candidato_mm = 1.0 # Inicia a busca a partir de 1 mm
        d3_incremento_mm = 0.01 # Incrementa de 0.01 mm
        max_d3_mm = 50.0 # Limite superior para d3 (50 mm)

        d3_otimizado_m = np.nan # Inicializa como NaN (Not a Number)

        while d3_candidato_mm <= max_d3_mm:
            d3_candidato_m = d3_candidato_mm / 1000.0 # Converte mm para metros
            A3_candidate = math.pi * d3_candidato_m**2 / 4
            Asy = A3_candidate - Apy

            if Asy > 0: # A área secundária deve ser positiva
                # Calcula a vazão mássica secundária (ms) para o d3_candidate
                ms = Pe_val * Asy / math.sqrt(Te) * math.sqrt(gamma / R * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))) * math.sqrt(ns)
                razão_atual = ms / m_p

                # Se a razão atual for igual ou maior que a razão alvo, encontramos um d3 válido
                if razão_atual >= razãoo:
                    d3_otimizado_m = d3_candidato_m
                    break # Encontrou o d3, sai do loop
            d3_candidato_mm += d3_incremento_mm

        return d3_otimizado_m # Retorna o d3 em metros

    except Exception as e:
        # print(f"Erro em achamento_d3_otimo para Pg={pg_val/1e3:.0f}kPa, dt={dt_val*1000:.2f}mm: {e}")
        return np.nan # Retorna NaN se ocorrer um erro

#Plot da Pe no d3
#Plot da influencia da Pg no d3
import matplotlib.pyplot as plt

# Definir os valores de dt para as curvas 
dt_valor_plotm = [1.00,1.5,2,2.5, 3] # 
dt_valor_plot =[d / 1000 for d in dt_valor_plotm] # [0.0025, 0.00275, 0.003]

# Faixa de valores de Pg para o gráfico (em Pa)
Pe_range_pa = np.linspace(10e3, 80e3, 30) # De 100 kPa a 1000 kPa (1 MPa), com 30 pontos

razãoo = 0.6 # 

# Gerar uma curva para cada dt
for dt_val_m, dt_label_mm in zip(dt_valor_plot, dt_valor_plotm):
    d3_otimizado_mm = []
    for Pe_val in Pe_range_pa:
        d3_opt_m = achamento_d3_otimo_Pe(Pe_val, dt_val_m, razãoo)
        d3_otimizado_mm.append(d3_opt_m * 1000 if not np.isnan(d3_opt_m) else np.nan) # Converte para mm para plotar

    axes[1].plot(Pe_range_pa / 1e3, d3_otimizado_mm, linestyle='-', label=f'dt = {dt_label_mm:.2f} mm')

axes[1].set_title('Diâmetro ótimo d3 vs. pressão de sucção Pe')
axes[1].set_xlabel('Pressão de sucção Pe (kPa)')
axes[1].set_ylabel('Diâmetro ótimo d3 (mm)')
axes[1].grid(True, linestyle='--', alpha=0.3)
axes[1].legend(title='Diâmetro da garganta (dt)')
axes[1].tick_params(axis='both', which='major')
axes[1].set_ylim(bottom=0)
#plt.savefig("DotimoxPsucçao.png", dpi=300)

def achamento_d3_otimo_Te(Te_val, dt_val, razãoo): 
    global Pg, Pe, eta_p, ns, phi_p, phi_m, Cp, dp1, gamma, R, Tg

    try:
        # 1. 
        At = math.pi * dt_val**2 / 4
        if At <= 0: return np.nan

        m_p = Pg * At / math.sqrt(Tg) * math.sqrt(gamma / R * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))) * math.sqrt(eta_p)
        if m_p <= 0: return np.nan

        Ap1 = math.pi * dp1**2 / 4
        Mp1 = symbols('Mp1')
        expr_mp1 = (Ap1 / At)**2 - (1 / Mp1**2 * (2 / (gamma + 1) * (1 + (gamma - 1) / 2 * Mp1**2))**((gamma + 1) / (gamma - 1)))
        
        # Tenta resolver para Mp1
        try:
            Mp1_sol_raw = nsolve(expr_mp1, Mp1, 3)
        except (ValueError, TypeError):
            try:
                Mp1_sol_raw = nsolve(expr_mp1, Mp1, 1.0)
            except (ValueError, TypeError):
                return np.nan

        Mp1_sol = float(Mp1_sol_raw) if isinstance(Mp1_sol_raw, (float, int)) else float(Mp1_sol_raw)
        if Mp1_sol <= 0 or not math.isfinite(Mp1_sol): return np.nan

        Pp1 = Pg / (1 + (gamma - 1) / 2 * Mp1_sol**2)**(gamma / (gamma - 1))

        Msy = 1
        Psy = Pe / (1 + (gamma - 1) / 2 * Msy**2)**(gamma / (gamma - 1))
        Ppy = Psy

        Mpy = symbols('Mpy')
        expr_mpy = (Ppy / Pp1) - (((1 + ((gamma - 1) / 2 * Mp1_sol**2))**(gamma / (gamma - 1))) / ((1 + ((gamma - 1) / 2 * Mpy**2))**(gamma / (gamma - 1))))
        
        # Tenta resolver 
        try:
            Mpy_sol_raw = nsolve(expr_mpy, Mpy, 1.8)
        except (ValueError, TypeError):
            try:
                Mpy_sol_raw = nsolve(expr_mpy, Mpy, 0.5)
            except (ValueError, TypeError):
                return np.nan

        Mpy_sol = float(Mpy_sol_raw) if isinstance(Mpy_sol_raw, (float, int)) else float(Mpy_sol_raw)
        if Mpy_sol <= 0 or not math.isfinite(Mpy_sol): return np.nan

        Num = (phi_p / Mpy_sol) * (2 / (gamma + 1) * (1 + ((gamma - 1) / 2 * Mpy_sol**2)))**((gamma + 1) / (2 * (gamma - 1)))
        Den = (1 / Mp1_sol) * (2 / (gamma + 1) * (1 + ((gamma - 1) / 2 * Mp1_sol**2)))**((gamma + 1) / (2 * (gamma - 1)))
        Apy = Ap1 * Num / Den

        # 2. Iterar para encontrar o d3 otimizado
        d3_candidato_mm = 1.0 # Inicia a busca a partir de 1 mm
        d3_incremento_mm = 0.01 # Incrementa de 0.01 mm
        max_d3_mm = 50.0 # Limite superior para d3 (50 mm)

        d3_otimizado_m = np.nan # Inicializa como NaN (Not a Number)

        while d3_candidato_mm <= max_d3_mm:
            d3_candidato_m = d3_candidato_mm / 1000.0 # Converte mm para metros
            A3_candidate = math.pi * d3_candidato_m**2 / 4
            Asy = A3_candidate - Apy

            if Asy > 0: # A área secundária deve ser positiva
                # Calcula a vazão mássica secundária (ms) para o d3_candidate
                ms = Pe * Asy / math.sqrt(Te_val) * math.sqrt(gamma / R * (2 / (gamma + 1))**((gamma + 1) / (gamma - 1))) * math.sqrt(ns)
                razão_atual = ms / m_p

                # Se a razão atual for igual ou maior que a razão alvo, encontramos um d3 válido
                if razão_atual >= razãoo:
                    d3_otimizado_m = d3_candidato_m
                    break # Encontrou o d3, sai do loop
            d3_candidato_mm += d3_incremento_mm

        return d3_otimizado_m # Retorna o d3 em metros

    except Exception as e:
        # print(f"Erro em achamento_d3_otimo para Pg={pg_val/1e3:.0f}kPa, dt={dt_val*1000:.2f}mm: {e}")
        return np.nan # Retorna NaN se ocorrer um erro

#dt_valor_plotm = [1.00,1.5,2,2.5, 3] # 
#dt_valor_plot =[d / 1000 for d in dt_valor_plotm] # [0.0025, 0.00275, 0.003]

# Faixa de valores de Pg para o gráfico (em Pa)
Te_range_K = np.linspace(250, 500, 30) # De 100 kPa a 1000 kPa (1 MPa), com 30 pontos

#razãoo = 0.6 # 

# Gerar uma curva para cada dt
for dt_val_m, dt_label_mm in zip(dt_valor_plot, dt_valor_plotm):
    d3_otimizado_mm_Te = []
    for Te_val in Te_range_K:
        d3_opt_m_Te = achamento_d3_otimo_Te(Te_val, dt_val_m, razãoo)
        d3_otimizado_mm_Te.append(d3_opt_m_Te * 1000 if not np.isnan(d3_opt_m_Te) else np.nan) # Converte para mm para plotar

    axes[2].plot(Te_range_K , d3_otimizado_mm_Te, linestyle='-', label=f'dt = {dt_label_mm:.2f} mm')

axes[2].set_title('Diâmetro ótimo d3 vs. temperatura de sucção Te')
axes[2].set_xlabel('Temperatura de sucção Te (K)')
axes[2].set_ylabel('Diâmetro ótimo d3 (mm)')
axes[2].grid(True, linestyle='--', alpha=0.3)
axes[2].legend(title='Diâmetro da garganta (dt)')
axes[2].tick_params(axis='both', which='major')
axes[2].set_ylim(bottom=0)
#plt.savefig("DotimoxPsucçao.png", dpi=300)

fig.tight_layout()
plt.show()