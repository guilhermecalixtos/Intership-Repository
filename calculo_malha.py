import math

def calcular_y1_e_layers(U, L_ref, target_yplus, L_meioo, rho=1.225, mu=1.789e-5, transition_ratio=0.272, growth_rate=1.2):
    """
    Calcula a altura da primeira camada (y1) baseada no Y+ desejado e, em seguida,
    determina o número de camadas necessário no método Smooth Transition do Ansys Meshing.
    
    Parâmetros:
    U (float): Velocidade do escoamento (m/s). No ejetor, use a velocidade máxima estimada.
    L_ref (float): Comprimento de referência (m). No ejetor, use o diâmetro da garganta ou câmara.
    target_yplus (float): O Y+ alvo (ex: 1.0 para k-omega SST, ~30 a 100 para k-epsilon).
    L_meioo (float): Tamanho do elemento da malha volumétrica (em mm).
    rho (float): Densidade do fluido (kg/m³). Padrão do ar: 1.225
    mu (float): Viscosidade dinâmica (kg/m·s). Padrão do ar: 1.789e-5
    transition_ratio (float): Fator de transição do Ansys (padrão 0.272).
    growth_rate (float): Taxa de crescimento do inflation (padrão 1.2).
    """
    
    # 1. Cálculo do Número de Reynolds
    Re = (rho * U * L_ref) / mu
    
    # 2. Estimativa do coeficiente de atrito de (Skin Friction Coefficient - Schlichting)
    # Válido para escoamentos turbulentos
    cf = 0.058 * (Re ** -0.2)
    
    # 3. Cálculo da tensão de cisalhamento na parede (Wall Shear Stress)
    tau_w = 0.5 * cf * rho * (U ** 2)
    
    # 4. Velocidade de fricção (Friction Velocity)
    u_tau = math.sqrt(tau_w / rho)
    
    # 5. Distância do centro da primeira célula até a parede (y) em metros
    y_centro_m = (target_yplus * mu) / (rho * u_tau)
    
    # 6. Altura total da primeira célula (y1) em metros e depois convertida para milímetros (mm)
    # Como as calculadoras padrão dão a distância do centro, a altura total da célula é 2 * y
    y1_m = 2 * y_centro_m
    y1_mm = y1_m * 1000.0
    
    # 7. Cálculo do número de camadas (Smooth Transition)
    if y1_mm >= (L_meioo * transition_ratio):
        N = 5
    else:
        numerador = math.log(y1_mm / (L_meioo * transition_ratio))
        denominador = math.log(1 / growth_rate)
        N = math.ceil(1 + (numerador / denominador))
        
    return Re, y1_mm, N

# ==============================================================================
# CONFIGURAÇÃO DOS SEUS DADOS (Altere os valores abaixo de acordo com seu projeto)
# ==============================================================================
VELOCIDADE_MAX_ESTIMADA = 491      # m/s (Ar na saída do bocal motriz supersônico)
DIAMETRO_REFERENCIA = 0.0016*0.07           # metros (Ex: Diâmetro da garganta do bocal ou câmara)
YPLUS_ALVO = 1.0                     # Requisito para k-omega SST 
TAMANHO_ELEMENTO_MEAN = 0.228571   # milímetros (Element Size definido no corpo/sizing local)

# Propriedades do ar (mude se operar em pressões/temperaturas muito diferentes)
DENSIDADE_AR = (11.18-0.5)/2                # kg/m³ --> Densidade média do ar na saída do bocal (entre 0.5 e 11.18 kg/m³)
VISCOSIDADE_AR = 1.789e-5            # kg/m·s

# Configurações do Inflation no Ansys
TAXA_CRESCIMENTO = 1.2               # Padrão: 1.2 (ou 1.15)
FATOR_TRANSICAO = 0.272              # Padrão do Ansys Meshing

# Execução do script
reynolds, y1_calculado, camadas = calcular_y1_e_layers(
    U=VELOCIDADE_MAX_ESTIMADA,
    L_ref=DIAMETRO_REFERENCIA,
    target_yplus=YPLUS_ALVO,
    L_meioo=TAMANHO_ELEMENTO_MEAN,
    rho=DENSIDADE_AR,
    mu=VISCOSIDADE_AR,
    transition_ratio=FATOR_TRANSICAO,
    growth_rate=TAXA_CRESCIMENTO
)

# Exibição dos resultados formatados para o Ansys Meshing
print("="*60)
print("             RESULTADOS DO CÁLCULO DA MALHA")
print("="*60)
print(f"Número de Reynolds Estimado: {reynolds:.2e}")
print(f"Altura Calculada da 1ª Camada (y1): {y1_calculado:.6f} mm")
print("="*60)
print("     PAINEL DE CONFIGURAÇÃO - ANSYS MESHING (Smooth Transition)")
print("="*60)
print(f"-> Inflation Option: Smooth Transition")
print(f"-> Transition Ratio: {FATOR_TRANSICAO}")
print(f"-> Growth Rate:      {TAXA_CRESCIMENTO}")
print(f"-> Number of Layers: {camadas}")
print("="*60)
