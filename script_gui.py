# VER3: Incorporates Age/Sex input, Italian Age/Sex Norms, Z-Scores, PCS/MCS
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import math
import os # Per ottenere il nome del file
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator # For integer ticks on Z-score chart

# -----------------------------------------------------------------------------
# FUNZIONE DI SCORING SF-36 (VER3 - Estesa con Standardizzazioni)
# -----------------------------------------------------------------------------

# --- Costanti per Standardizzazione USA (da index.html) ---
US_MEANS = { 'PF': 84.52404, 'RP': 81.19907, 'BP': 75.49196, 'GH': 72.21316, 'VT': 61.05453, 'SF': 83.59753, 'RE': 81.29467, 'MH': 74.84212 }
US_SDS   = { 'PF': 22.89490, 'RP': 33.79729, 'BP': 23.55879, 'GH': 20.16964, 'VT': 20.86942, 'SF': 22.37642, 'RE': 33.02717, 'MH': 18.01189 }
WEIGHTS = {
    'PCS': { 'PF':  0.42402, 'RP':  0.35119, 'BP':  0.31754, 'GH':  0.24954, 'VT':  0.02877, 'SF': -0.00753, 'RE': -0.19206, 'MH': -0.22069 },
    'MCS': { 'PF': -0.22999, 'RP': -0.12329, 'BP': -0.09731, 'GH': -0.01571, 'VT':  0.23534, 'SF':  0.26876, 'RE':  0.43407, 'MH':  0.48581 }
}

# --- Norme Italiane per Età/Sesso (da index.html) ---
# Struttura: AGE_SEX_NORMS[SEX][AGE_CLASS][SCALE].{mean, sd}
AGE_SEX_NORMS = {
    1: { # Sesso = 1 (Maschio)
        2: { # <=24
            'PF': { 'mean': 96.4851, 'sd': 7.9544 }, 'RP': { 'mean': 91.0891, 'sd': 19.8696 }, 'BP': { 'mean': 90.9505, 'sd': 14.0124 },
            'GH': { 'mean': 81.2079, 'sd': 13.1972 }, 'VT': { 'mean': 73.1683, 'sd': 15.3252 }, 'SF': { 'mean': 85.5198, 'sd': 17.9176 },
            'RE': { 'mean': 84.8185, 'sd': 28.8770 }, 'MH': { 'mean': 76.1980, 'sd': 12.7421 }
        },
        3: { # 25-34
            'PF': { 'mean': 95.9172, 'sd': 10.3604 }, 'RP': { 'mean': 90.2367, 'sd': 24.7175 }, 'BP': { 'mean': 83.0888, 'sd': 23.1593 },
            'GH': { 'mean': 76.9053, 'sd': 15.6849 }, 'VT': { 'mean': 70.3748, 'sd': 15.2110 }, 'SF': { 'mean': 84.8373, 'sd': 17.6337 },
            'RE': { 'mean': 89.7436, 'sd': 23.8492 }, 'MH': { 'mean': 75.3609, 'sd': 14.1781 }
        },
        4: { # 35-44
            'PF': { 'mean': 95.6915, 'sd': 8.0141 }, 'RP': { 'mean': 90.5585, 'sd': 24.8112 }, 'BP': { 'mean': 81.6064, 'sd': 22.8118 },
            'GH': { 'mean': 71.5479, 'sd': 18.1271 }, 'VT': { 'mean': 67.5709, 'sd': 16.9480 }, 'SF': { 'mean': 82.9122, 'sd': 19.4269 },
            'RE': { 'mean': 83.6007, 'sd': 31.3703 }, 'MH': { 'mean': 73.6330, 'sd': 17.3180 }
        },
        5: { # 45-54
            'PF': { 'mean': 91.2641, 'sd': 14.0467 }, 'RP': { 'mean': 88.0240, 'sd': 25.7183 }, 'BP': { 'mean': 81.5621, 'sd': 21.8490 },
            'GH': { 'mean': 68.3905, 'sd': 17.8583 }, 'VT': { 'mean': 67.1687, 'sd': 18.4587 }, 'SF': { 'mean': 80.1775, 'sd': 21.7579 },
            'RE': { 'mean': 81.2121, 'sd': 34.1943 }, 'MH': { 'mean': 70.7892, 'sd': 17.9112 }
        },
        6: { # 55-64
            'PF': { 'mean': 83.2193, 'sd': 23.8917 }, 'RP': { 'mean': 73.0263, 'sd': 38.9943 }, 'BP': { 'mean': 73.9105, 'sd': 27.9990 },
            'GH': { 'mean': 61.1789, 'sd': 22.7691 }, 'VT': { 'mean': 64.1534, 'sd': 22.1833 }, 'SF': { 'mean': 79.2763, 'sd': 25.2756 },
            'RE': { 'mean': 73.5088, 'sd': 39.3207 }, 'MH': { 'mean': 69.2751, 'sd': 21.5863 }
        },
        7: { # 65-74
            'PF': { 'mean': 72.4609, 'sd': 26.4575 }, 'RP': { 'mean': 65.1575, 'sd': 43.6615 }, 'BP': { 'mean': 68.2656, 'sd': 29.3691 },
            'GH': { 'mean': 55.4141, 'sd': 21.5152 }, 'VT': { 'mean': 59.5703, 'sd': 21.5723 }, 'SF': { 'mean': 76.0742, 'sd': 25.2949 },
            'RE': { 'mean': 72.2222, 'sd': 38.8158 }, 'MH': { 'mean': 64.5469, 'sd': 21.2576 }
        },
        8: { # >74
            'PF': { 'mean': 50.5556, 'sd': 31.2728 }, 'RP': { 'mean': 50.9259, 'sd': 46.3180 }, 'BP': { 'mean': 52.3704, 'sd': 31.5291 },
            'GH': { 'mean': 41.9630, 'sd': 23.4376 }, 'VT': { 'mean': 46.1111, 'sd': 23.4655 }, 'SF': { 'mean': 62.2685, 'sd': 28.9855 },
            'RE': { 'mean': 54.9383, 'sd': 44.9353 }, 'MH': { 'mean': 57.9259, 'sd': 23.3722 }
        }
    },
    2: { # Sesso = 2 (Femmina)
        2: { # <=24
            'PF': { 'mean': 96.8478, 'sd': 6.6182 }, 'RP': { 'mean': 85.3261, 'sd': 31.9151 }, 'BP': { 'mean': 82.5109, 'sd': 21.9452 },
            'GH': { 'mean': 75.4239, 'sd': 14.1446 }, 'VT': { 'mean': 64.2935, 'sd': 17.3614 }, 'SF': { 'mean': 77.8533, 'sd': 23.9550 },
            'RE': { 'mean': 74.2754, 'sd': 37.9908 }, 'MH': { 'mean': 68.6957, 'sd': 17.8552 }
        },
        3: { # 25-34
            'PF': { 'mean': 94.2172, 'sd': 13.6217 }, 'RP': { 'mean': 90.2778, 'sd': 23.8342 }, 'BP': { 'mean': 80.3182, 'sd': 24.5401 },
            'GH': { 'mean': 74.3990, 'sd': 16.4093 }, 'VT': { 'mean': 65.1263, 'sd': 17.5019 }, 'SF': { 'mean': 78.9141, 'sd': 19.2784 },
            'RE': { 'mean': 81.4815, 'sd': 31.9412 }, 'MH': { 'mean': 69.8990, 'sd': 18.3090 }
        },
        4: { # 35-44
            'PF': { 'mean': 90.4054, 'sd': 14.4641 }, 'RP': { 'mean': 81.4865, 'sd': 32.7388 }, 'BP': { 'mean': 74.4000, 'sd': 24.6885 },
            'GH': { 'mean': 69.2757, 'sd': 18.5749 }, 'VT': { 'mean': 61.3514, 'sd': 18.5129 }, 'SF': { 'mean': 76.7568, 'sd': 22.2378 },
            'RE': { 'mean': 77.1171, 'sd': 37.7361 }, 'MH': { 'mean': 63.4541, 'sd': 21.3136 }
        },
        5: { # 45-54
            'PF': { 'mean': 85.9074, 'sd': 16.8844 }, 'RP': { 'mean': 75.8287, 'sd': 35.9302 }, 'BP': { 'mean': 68.9560, 'sd': 27.1034 },
            'GH': { 'mean': 64.1099, 'sd': 18.9535 }, 'VT': { 'mean': 59.5185, 'sd': 19.2604 }, 'SF': { 'mean': 76.5797, 'sd': 21.6724 },
            'RE': { 'mean': 77.5641, 'sd': 36.1429 }, 'MH': { 'mean': 64.3778, 'sd': 20.2981 }
        },
        6: { # 55-64
            'PF': { 'mean': 75.2448, 'sd': 24.5972 }, 'RP': { 'mean': 72.8343, 'sd': 37.9604 }, 'BP': { 'mean': 63.2712, 'sd': 28.8583 },
            'GH': { 'mean': 58.2429, 'sd': 22.7831 }, 'VT': { 'mean': 54.5198, 'sd': 21.5975 }, 'SF': { 'mean': 74.5763, 'sd': 23.6082 },
            'RE': { 'mean': 67.7966, 'sd': 41.8780 }, 'MH': { 'mean': 57.8475, 'sd': 22.1273 }
        },
        7: { # 65-74
            'PF': { 'mean': 63.4487, 'sd': 27.8130 }, 'RP': { 'mean': 55.3846, 'sd': 43.0189 }, 'BP': { 'mean': 58.4231, 'sd': 30.9493 },
            'GH': { 'mean': 47.4846, 'sd': 24.6367 }, 'VT': { 'mean': 51.2949, 'sd': 23.0579 }, 'SF': { 'mean': 70.0000, 'sd': 27.9118 },
            'RE': { 'mean': 66.6667, 'sd': 41.2968 }, 'MH': { 'mean': 56.3385, 'sd': 23.9484 }
        },
        8: { # >74
            'PF': { 'mean': 42.5000, 'sd': 28.5273 }, 'RP': { 'mean': 42.0343, 'sd': 44.1061 }, 'BP': { 'mean': 45.0882, 'sd': 29.0284 },
            'GH': { 'mean': 38.8382, 'sd': 24.7390 }, 'VT': { 'mean': 40.6618, 'sd': 23.4187 }, 'SF': { 'mean': 55.5147, 'sd': 26.4842 },
            'RE': { 'mean': 49.0196, 'sd': 46.5993 }, 'MH': { 'mean': 48.5294, 'sd': 25.3351 }
        }
    }
}

SCALES_ORDER = ['PF', 'RP', 'BP', 'GH', 'VT', 'SF', 'RE', 'MH', 'HT']
SCALES_FOR_STD = ['PF', 'RP', 'BP', 'GH', 'VT', 'SF', 'RE', 'MH'] # Scales used in standardizations


def score_sf36_ver3(answers, age=None, sex=None):
    """
    Calcola punteggi SF-36 (0-100), Z-Scores (USA), PCS/MCS (USA),
    e T-Scores per Età/Sesso (ITA).
    Input:
        answers (list): Lista di 36 risposte (int o None).
        age (int, optional): Età del paziente. Default None.
        sex (int, optional): Sesso del paziente (1=Maschio, 2=Femmina). Default None.
    Output:
        dict: Contiene 'scores' (0-100), 'z_scores', 'summaries' (PCS/MCS), 'age_sex_t_scores'.
              Valori sono float o None se non calcolabili.
    """
    if not isinstance(answers, list) or len(answers) != 36:
        print("Errore input: la lista di risposte deve contenere 36 elementi.")
        return None

    results = {
        'scores': {scale: None for scale in SCALES_ORDER},
        'z_scores': {scale: None for scale in SCALES_FOR_STD},
        'summaries': {'PCS': None, 'MCS': None},
        'age_sex_t_scores': {scale: None for scale in SCALES_FOR_STD}
    }

    # --- Mappatura Indici (0-based) -> Item e Scale --- (Come script originale)
    scale_indices = {
        'PF': list(range(2, 12)), 'RP': list(range(12, 16)), 'RE': list(range(16, 19)),
        'VT': [22, 26, 28, 30], 'MH': [23, 24, 25, 27, 29], 'SF': [19, 31],
        'BP': [20, 21], 'GH': [0, 32, 33, 34, 35], 'HT': [1]
    }

    # --- Tabelle di Ricodifica (Raw -> Punteggio Item 0-100) --- (Come script originale)
    RECODE_PF = {1: 0, 2: 50, 3: 100}
    RECODE_RP_RE = {1: 0, 2: 100}
    RECODE_Q9_POS = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0}
    RECODE_Q9_NEG = {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100}
    RECODE_SF1 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}
    RECODE_SF2 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}
    RECODE_BP1 = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0}
    RECODE_BP2 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}
    RECODE_GH1 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}
    RECODE_GH2 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}
    RECODE_GH3 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}
    RECODE_GH4 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}
    RECODE_GH5 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}
    RECODE_HT = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}

    item_recode_map = {
        **{i: RECODE_PF for i in scale_indices['PF']},
        **{i: RECODE_RP_RE for i in scale_indices['RP']},
        **{i: RECODE_RP_RE for i in scale_indices['RE']},
        22: RECODE_Q9_POS, 26: RECODE_Q9_POS, 28: RECODE_Q9_NEG, 30: RECODE_Q9_NEG, # VT
        23: RECODE_Q9_NEG, 24: RECODE_Q9_NEG, 25: RECODE_Q9_POS, 27: RECODE_Q9_NEG, 29: RECODE_Q9_POS, # MH
        19: RECODE_SF1, 31: RECODE_SF2, # SF
        20: RECODE_BP1, 21: RECODE_BP2, # BP
        0: RECODE_GH1, 32: RECODE_GH2, 33: RECODE_GH3, 34: RECODE_GH4, 35: RECODE_GH5, # GH
        1: RECODE_HT # HT
    }

    # 1. --- Calcolo Punteggi Scale 0-100 ---
    for scale, indices in scale_indices.items():
        if scale == 'HT': continue # HT calcolato separatamente

        num_items_in_scale = len(indices)
        raw_answers_for_scale = [answers[idx] if 0 <= idx < len(answers) else None for idx in indices]

        recoded_scores = []
        valid_item_count = 0
        missing_count = 0

        for i, raw_answer in enumerate(raw_answers_for_scale):
            item_index = indices[i]
            recode_map_for_item = item_recode_map.get(item_index)

            if raw_answer is not None and recode_map_for_item and raw_answer in recode_map_for_item:
                recoded_value = recode_map_for_item.get(raw_answer)
                if recoded_value is not None:
                     recoded_scores.append(recoded_value)
                     valid_item_count += 1
                else: missing_count += 1
            else: missing_count += 1

        if missing_count > num_items_in_scale / 2:
            results['scores'][scale] = None
        elif valid_item_count == 0:
             results['scores'][scale] = None
        else:
            results['scores'][scale] = sum(recoded_scores) / valid_item_count

    # Calcolo HT (0-100)
    ht_index = scale_indices['HT'][0]
    ht_raw = answers[ht_index] if 0 <= ht_index < len(answers) else None
    recode_map_ht = item_recode_map.get(ht_index)
    if ht_raw is not None and recode_map_ht and ht_raw in recode_map_ht:
        results['scores']['HT'] = recode_map_ht.get(ht_raw)
    else:
        results['scores']['HT'] = None

    # 2. --- Calcolo Z-Scores (Standardizzazione USA) ---
    all_scores_valid_for_summaries = True
    for scale in SCALES_FOR_STD:
        score = results['scores'].get(scale)
        if score is not None and not math.isnan(score) and scale in US_MEANS and scale in US_SDS:
            try:
                results['z_scores'][scale] = (score - US_MEANS[scale]) / US_SDS[scale]
            except ZeroDivisionError:
                results['z_scores'][scale] = None
                all_scores_valid_for_summaries = False
        else:
            results['z_scores'][scale] = None
            all_scores_valid_for_summaries = False

    # 3. --- Calcolo Indici Sintetici USA (PCS/MCS) ---
    if all_scores_valid_for_summaries:
        try:
            pcs_raw = sum(results['z_scores'][scale] * WEIGHTS['PCS'][scale] for scale in SCALES_FOR_STD)
            mcs_raw = sum(results['z_scores'][scale] * WEIGHTS['MCS'][scale] for scale in SCALES_FOR_STD)
            results['summaries']['PCS'] = (pcs_raw * 10) + 50
            results['summaries']['MCS'] = (mcs_raw * 10) + 50
        except Exception as e:
            print(f"Errore nel calcolo PCS/MCS: {e}")
            results['summaries']['PCS'] = None
            results['summaries']['MCS'] = None
    else:
        results['summaries']['PCS'] = None
        results['summaries']['MCS'] = None

    # 4. --- Calcolo Punteggi T Standardizzati per Età/Sesso (ITA) ---
    age_num = None
    sex_num = None
    age_class = 0
    can_calculate_age_sex = False

    try:
        if age is not None: age_num = int(age)
        if sex is not None: sex_num = int(sex)
    except (ValueError, TypeError):
        print("Età o Sesso non validi per la standardizzazione.")
        age_num = None
        sex_num = None

    # Determina classe di età
    if age_num is not None and age_num > 0:
        if age_num <= 24: age_class = 2
        elif age_num <= 34: age_class = 3
        elif age_num <= 44: age_class = 4
        elif age_num <= 54: age_class = 5
        elif age_num <= 64: age_class = 6
        elif age_num <= 74: age_class = 7
        else: age_class = 8 # > 74

    # Verifica se abbiamo Sesso e Classe Età validi
    if sex_num in [1, 2] and age_class in range(2, 9):
         can_calculate_age_sex = True

    if can_calculate_age_sex:
        for scale in SCALES_FOR_STD:
            score_0100 = results['scores'].get(scale)
            try:
                norms = AGE_SEX_NORMS[sex_num][age_class][scale]
                mean = norms['mean']
                sd = norms['sd']
                if score_0100 is not None and not math.isnan(score_0100) and sd is not None and sd != 0:
                    t_score = (((score_0100 - mean) / sd) * 10) + 50
                    results['age_sex_t_scores'][scale] = t_score
                else:
                    results['age_sex_t_scores'][scale] = None
            except (KeyError, TypeError, ZeroDivisionError) as e:
                print(f"Errore nel recupero norme o calcolo T-score per {scale} (Sesso={sex_num}, ClasseEtà={age_class}): {e}")
                results['age_sex_t_scores'][scale] = None
    else:
         # Lascia i T-scores a None se età/sesso non validi
         print("Età o Sesso mancanti o non validi, T-scores per età/sesso non calcolati.")

    return results

# -----------------------------------------------------------------------------
# DEFINIZIONE DOMANDE E RANGE VALIDI (Come script originale)
# -----------------------------------------------------------------------------
questions_info = [
    # (indice 0-based, Testo Domanda, Range Atteso Stringa, Range Atteso Tuple (min, max))
    (0, "1. In generale direbbe che la Sua salute è....", "1-5", (1, 5)),
    (1, "2. Rispetto a un anno fa, come giudicherebbe, ora, la Sua salute in generale?", "1-5", (1, 5)),
    (2, "3a. Attività fisicamente impegnative...", "1-3", (1, 3)), # PF1
    (3, "3b. Attività di moderato impegno fisico...", "1-3", (1, 3)), # PF2
    (4, "3c. Sollevare o portare le borse della spesa", "1-3", (1, 3)), # PF3
    (5, "3d. Salire qualche piano di scale", "1-3", (1, 3)), # PF4
    (6, "3e. Salire un piano di scale", "1-3", (1, 3)), # PF5
    (7, "3f. Piegarsi, inginocchiarsi o chinarsi", "1-3", (1, 3)), # PF6
    (8, "3g. Camminare per un chilometro", "1-3", (1, 3)), # PF7
    (9, "3h. Camminare per qualche centinaia di metri", "1-3", (1, 3)), # PF8
    (10, "3i. Camminare per circa cento metri", "1-3", (1, 3)), # PF9
    (11, "3j. Fare il bagno o vestirsi da soli", "1-3", (1, 3)), # PF10
    (12, "4a. (N4S) Ridotto tempo lavoro/attività [causa salute fisica]?", "1-2", (1, 2)), # RP1
    (13, "4b. (N4S) Reso meno [causa salute fisica]?", "1-2", (1, 2)), # RP2
    (14, "4c. (N4S) Limitato tipi lavoro/attività [causa salute fisica]?", "1-2", (1, 2)), # RP3
    (15, "4d. (N4S) Difficoltà lavoro/attività [causa salute fisica]?", "1-2", (1, 2)), # RP4
    (16, "5a. (N4S) Ridotto tempo lavoro/attività [causa stato emotivo]?", "1-2", (1, 2)), # RE1
    (17, "5b. (N4S) Reso meno [causa stato emotivo]?", "1-2", (1, 2)), # RE2
    (18, "5c. (N4S) Calo concentrazione lavoro/attività [causa stato emotivo]?", "1-2", (1, 2)), # RE3
    (19, "6. (N4S) Interferenza salute/emotività con attività sociali?", "1-5", (1, 5)), # SF1
    (20, "7. (N4S) Quanto dolore fisico?", "1-6", (1, 6)), # BP1
    (21, "8. (N4S) Interferenza dolore nel lavoro abituale?", "1-5", (1, 5)), # BP2
    (22, "9a. (N4S, tempo) Sentito vivace brillante?", "1-6", (1, 6)), # VT1
    (23, "9b. (N4S, tempo) Sentito molto agitato?", "1-6", (1, 6)), # MH1
    (24, "9c. (N4S, tempo) Sentito così giù che niente La tirava su?", "1-6", (1, 6)), # MH2
    (25, "9d. (N4S, tempo) Sentito calmo e sereno?", "1-6", (1, 6)), # MH3
    (26, "9e. (N4S, tempo) Sentito pieno di energia?", "1-6", (1, 6)), # VT2
    (27, "9f. (N4S, tempo) Sentito scoraggiato e triste?", "1-6", (1, 6)), # MH4
    (28, "9g. (N4S, tempo) Sentito sfinito?", "1-6", (1, 6)), # VT3
    (29, "9h. (N4S, tempo) Sentito felice?", "1-6", (1, 6)), # MH5
    (30, "9i. (N4S, tempo) Sentito stanco?", "1-6", (1, 6)), # VT4
    (31, "10. (N4S) Interferenza salute/emotività in attività sociali (famiglia, amici)?", "1-5", (1, 5)), # SF2
    (32, "11a. Ammalarmi più facilmente degli altri", "1-5", (1, 5)), # GH1 -> Item index 32 in answers list
    (33, "11b. Salute come quella degli altri", "1-5", (1, 5)), # GH2 -> Item index 33
    (34, "11c. Aspetto che la mia salute peggiorerà", "1-5", (1, 5)), # GH3 -> Item index 34
    (35, "11d. Godo di ottima salute", "1-5", (1, 5)), # GH4 -> Item index 35
]

# -----------------------------------------------------------------------------
# ETICHETTE BILINGUE PER IL GRAFICO (Come script originale)
# -----------------------------------------------------------------------------
BILINGUAL_LABELS = {
    'PF': "PF\nPhysical Functioning", 'RP': "RP\nRole Physical", 'BP': "BP\nBodily Pain",
    'GH': "GH\nGeneral Health", 'VT': "VT\nVitality", 'SF': "SF\nSocial Functioning",
    'RE': "RE\nRole Emotional", 'MH': "MH\nMental Health", 'HT': "HT\nHealth Transition",
    'PCS': 'PCS\nPhysical Comp. Summary', 'MCS': 'MCS\nMental Comp. Summary'
}
CHART_SCALE_ORDER = ['PF', 'RP', 'BP', 'GH', 'VT', 'SF', 'RE', 'MH'] # Per grafici standardizzati


# -----------------------------------------------------------------------------
# CLASSE DELLA GUI (VER3)
# -----------------------------------------------------------------------------
class SF36_GUI_V3:
    def __init__(self, master):
        self.master = master
        master.title("SF-36 Scorer V3 (Standardizzazione Età/Sesso ITA + USA)")
        master.geometry("1100x900") # Aumentata larghezza per nuovi grafici
        master.minsize(1000, 850)

        self.style = ttk.Style()
        try: self.style.theme_use('clam')
        except tk.TclError: print("Tema 'clam' non disponibile, usando default.")
        self.style.configure("Error.TEntry", fieldbackground="#ffecec", foreground="red")
        self.style.map("Error.TEntry", fieldbackground=[('focus', '#ffdddd')])
        self.style.configure("Valid.TEntry", foreground="black")
        self.style.configure("TNotebook.Tab", padding=[12, 5], font=('Segoe UI', 9))
        self.style.configure("TLabelframe.Label", font=('Segoe UI', 10, 'bold'))


        self.filepath = tk.StringVar(value="Nessun file selezionato.")
        self.manual_entries = []
        self.demographic_vars = { # Variabili per età e sesso
            'age': tk.StringVar(),
            'sex': tk.StringVar()
        }

        # --- Layout Principale ---
        # Frame superiore per input (file e manuale + demo)
        top_input_frame = ttk.Frame(master, padding=10)
        top_input_frame.pack(side=tk.TOP, fill=tk.X, expand=False)

        # Frame inferiore per output (risultati testo e grafici in notebook)
        bottom_output_frame = ttk.Frame(master, padding=(10,0,10,10))
        bottom_output_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # --- Controlli File (in top_input_frame) ---
        file_frame = ttk.LabelFrame(top_input_frame, text="Carica da File", padding=10)
        file_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")

        browse_button = ttk.Button(file_frame, text="Sfoglia...", command=self.browse_file)
        browse_button.pack(side=tk.LEFT, padx=5)
        file_label = ttk.Label(file_frame, textvariable=self.filepath, relief=tk.SUNKEN, width=50) # Ridotta un po'
        file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        calc_file_button = ttk.Button(file_frame, text="Calcola da File", command=self.calculate_from_file)
        calc_file_button.pack(side=tk.LEFT, padx=5)

        # --- Controlli Demografici (in top_input_frame) ---
        demo_frame = ttk.LabelFrame(top_input_frame, text="Dati Demografici (per Standardizzazione)", padding=10)
        demo_frame.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")

        ttk.Label(demo_frame, text="Età:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        age_entry = ttk.Entry(demo_frame, textvariable=self.demographic_vars['age'], width=5, justify=tk.CENTER)
        age_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        Tooltip(age_entry, "Inserire età in anni")

        ttk.Label(demo_frame, text="Sesso:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        sex_combo = ttk.Combobox(demo_frame, textvariable=self.demographic_vars['sex'], values=["", "Maschio (1)", "Femmina (2)"], width=12, state="readonly")
        sex_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        sex_combo.current(0) # Seleziona vuoto all'inizio
        Tooltip(sex_combo, "Selezionare sesso biologico (1 o 2)")

        # Configura espansione colonne nel top_input_frame
        top_input_frame.columnconfigure(0, weight=1)
        top_input_frame.columnconfigure(1, weight=0) # Non espandere demo frame

        # --- Inserimento Manuale (sotto i frame file/demo) ---
        manual_outer_frame = ttk.LabelFrame(master, text="Inserimento Manuale Risposte (1-36)", padding=10)
        manual_outer_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(manual_outer_frame, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(manual_outer_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="scrollable_frame")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel) # Linux scroll
        self.canvas.bind_all("<Button-5>", self._on_mousewheel) # Linux scroll

        self.create_manual_entries(self.scrollable_frame)

        # --- Bottone Calcolo Manuale ---
        calc_manual_button = ttk.Button(master, text="Calcola da Inserimento Manuale", command=self.calculate_from_manual)
        calc_manual_button.pack(side=tk.TOP, pady=(0, 10)) # Sotto il frame manuale


        # --- Output Frame (bottom_output_frame) ---
        # Risultati Testuali a Sinistra
        result_text_frame = ttk.LabelFrame(bottom_output_frame, text="Risultati Numerici", padding=10)
        result_text_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0,10))

        self.result_text = scrolledtext.ScrolledText(result_text_frame, height=25, width=55, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 9)) # Monospace font
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # Grafici a Destra (dentro un Notebook)
        plot_notebook = ttk.Notebook(bottom_output_frame)
        plot_notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Creazione dei frame per i grafici
        self.plot_frames = {}
        tab_names = ["Scale 0-100", "Z-Score USA", "PCS/MCS USA", "T-Score Età/Sesso ITA"]
        for name in tab_names:
             frame = ttk.Frame(plot_notebook, padding=5)
             plot_notebook.add(frame, text=name)
             self.plot_frames[name] = frame

        # Creazione Figure e Canvas per i grafici
        plt.style.use('seaborn-v0_8-whitegrid')
        self.figs_axes = {}
        self.canvases = {}
        self.toolbars = {} # Per aggiungere toolbar ai grafici

        # Grafico Scale 0-100
        fig0100, ax0100 = plt.subplots(figsize=(6, 4.5), dpi=90)
        fig0100.subplots_adjust(bottom=0.25, top=0.9, left=0.12, right=0.95)
        self.figs_axes["Scale 0-100"] = (fig0100, ax0100)
        canvas0100 = FigureCanvasTkAgg(fig0100, master=self.plot_frames["Scale 0-100"])
        self.canvases["Scale 0-100"] = canvas0100
        toolbar0100 = NavigationToolbar2Tk(canvas0100, self.plot_frames["Scale 0-100"], pack_toolbar=False)
        self.toolbars["Scale 0-100"] = toolbar0100
        toolbar0100.pack(side=tk.BOTTOM, fill=tk.X)
        canvas0100.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Grafico Z-Score USA
        figZ, axZ = plt.subplots(figsize=(6, 4.5), dpi=90)
        figZ.subplots_adjust(bottom=0.25, top=0.9, left=0.12, right=0.95)
        self.figs_axes["Z-Score USA"] = (figZ, axZ)
        canvasZ = FigureCanvasTkAgg(figZ, master=self.plot_frames["Z-Score USA"])
        self.canvases["Z-Score USA"] = canvasZ
        toolbarZ = NavigationToolbar2Tk(canvasZ, self.plot_frames["Z-Score USA"], pack_toolbar=False)
        self.toolbars["Z-Score USA"] = toolbarZ
        toolbarZ.pack(side=tk.BOTTOM, fill=tk.X)
        canvasZ.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Grafico PCS/MCS USA
        figSum, axSum = plt.subplots(figsize=(4, 4), dpi=90) # Più piccolo
        figSum.subplots_adjust(bottom=0.15, top=0.9, left=0.15, right=0.95)
        self.figs_axes["PCS/MCS USA"] = (figSum, axSum)
        canvasSum = FigureCanvasTkAgg(figSum, master=self.plot_frames["PCS/MCS USA"])
        self.canvases["PCS/MCS USA"] = canvasSum
        toolbarSum = NavigationToolbar2Tk(canvasSum, self.plot_frames["PCS/MCS USA"], pack_toolbar=False)
        self.toolbars["PCS/MCS USA"] = toolbarSum
        toolbarSum.pack(side=tk.BOTTOM, fill=tk.X)
        canvasSum.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Grafico T-Score Età/Sesso ITA
        figT, axT = plt.subplots(figsize=(6, 4.5), dpi=90)
        figT.subplots_adjust(bottom=0.25, top=0.9, left=0.12, right=0.95)
        self.figs_axes["T-Score Età/Sesso ITA"] = (figT, axT)
        canvasT = FigureCanvasTkAgg(figT, master=self.plot_frames["T-Score Età/Sesso ITA"])
        self.canvases["T-Score Età/Sesso ITA"] = canvasT
        toolbarT = NavigationToolbar2Tk(canvasT, self.plot_frames["T-Score Età/Sesso ITA"], pack_toolbar=False)
        self.toolbars["T-Score Età/Sesso ITA"] = toolbarT
        toolbarT.pack(side=tk.BOTTOM, fill=tk.X)
        canvasT.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.clear_all_outputs() # Pulisce testo e grafici inizialmente


    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        parent_width = self.canvas.winfo_width()
        entry_width_approx = 80
        scrollbar_width = self.scrollbar.winfo_width() if self.scrollbar.winfo_ismapped() else 0
        wrap_length = max(150, parent_width - entry_width_approx - scrollbar_width - 20) # Aggiunto padding extra
        for item in self.scrollable_frame.winfo_children():
             if isinstance(item, ttk.Frame):
                 for widget in item.winfo_children():
                     if isinstance(widget, ttk.Label) and hasattr(widget, 'original_text'):
                         widget.configure(wraplength=wrap_length)

    def _on_mousewheel(self, event):
        # Determina la direzione dello scroll
        if event.num == 4: delta = -1 # Linux scroll up
        elif event.num == 5: delta = 1  # Linux scroll down
        elif hasattr(event, 'delta'): # Windows/Mac
            if isinstance(event.delta, int): # Assicurati sia intero
                 delta = -1 if event.delta > 0 else 1
            else: return # Ignora se delta non è int
        else: return # Evento non riconosciuto

        # Trova il widget sotto il mouse
        widget_under_mouse = self.master.winfo_containing(event.x_root, event.y_root)
        target_canvas = self.canvas

        # Verifica se il widget sotto il mouse è il canvas target o un suo discendente
        parent = widget_under_mouse
        is_descendant = False
        while parent is not None:
            if parent == target_canvas:
                is_descendant = True
                break
            if parent == self.master: break # Uscita se si arriva alla root
            try:
                parent = parent.master # Sali nella gerarchia
            except AttributeError: # Se parent non ha master (es. Toplevel)
                 break

        # Applica lo scroll solo se il mouse è sopra il canvas o un suo figlio
        if is_descendant:
            target_canvas.yview_scroll(delta, "units")


    def create_manual_entries(self, parent_frame):
        """Crea le 36 label e entry per l'inserimento manuale."""
        self.manual_entries = []
        initial_wrap_length = 600

        for i, (idx, q_text, q_range_str, q_range_tuple) in enumerate(questions_info):
            row_frame = ttk.Frame(parent_frame)
            row_frame.pack(fill=tk.X, pady=2, padx=5)

            q_label_text = f"{q_text} ({q_range_str})"
            lbl_q = ttk.Label(row_frame, text=q_label_text, anchor=tk.W, justify=tk.LEFT, wraplength=initial_wrap_length)
            lbl_q.original_text = q_text # Memorizza testo originale per tooltip/wrap
            lbl_q.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

            entry_var = tk.StringVar()
            entry = ttk.Entry(row_frame, width=5, textvariable=entry_var, style="Valid.TEntry", justify=tk.CENTER)
            entry.pack(side=tk.LEFT, padx=(0, 5))
            self.manual_entries.append({'widget': entry, 'var': entry_var, 'index': idx, 'range': q_range_tuple, 'label': lbl_q})

            Tooltip(widget=lbl_q, text=f"Item {idx+1}: {q_text}\nRange: {q_range_str}")
            Tooltip(widget=entry, text=f"Inserire {q_range_str} o lasciare vuoto")

        parent_frame.update_idletasks()
        self.on_frame_configure()

    # --- Funzioni Plotting ---
    def _plot_generic_bar(self, ax, fig, canvas, data, title, ylabel, labels_map, is_t_score=False, is_z_score=False):
        """Funzione generica per disegnare grafici a barre."""
        ax.clear()
        plot_data = {scale: val for scale, val in data.items() if val is not None and not (isinstance(val, float) and math.isnan(val))}

        if not plot_data:
            ax.text(0.5, 0.5, "Nessun dato valido", ha='center', va='center', transform=ax.transAxes, color='gray')
            ax.set_title(title, pad=15, fontsize=11)
            ax.set_ylabel(ylabel, fontsize=9)
            ax.set_yticks([])
            ax.set_xticks([])
        else:
            scales_in_plot = list(plot_data.keys())
            values = list(plot_data.values())
            # Usa etichette bilingue se disponibili, altrimenti la chiave della scala
            bilingual_x_labels = [labels_map.get(scale, scale).replace('\n', ' ') for scale in scales_in_plot]

            colors = plt.cm.viridis([i/len(scales_in_plot) for i in range(len(scales_in_plot))]) # Colormap
            bars = ax.bar(bilingual_x_labels, values, color=colors, width=0.7)

            ax.set_ylabel(ylabel, fontsize=9)
            ax.set_title(title, pad=15, fontsize=11)
            ax.tick_params(axis='x', labelsize=8, rotation=45, ha='right') # Ruota etichette x
            ax.tick_params(axis='y', labelsize=8)

            # Aggiungi etichette valori
            ax.bar_label(bars, fmt='{:.1f}', padding=3, fontsize=7)

            # Imposta limiti Y specifici
            if is_t_score:
                ax.set_ylim(0, 100)
                ax.axhline(50, color='grey', linestyle='--', linewidth=0.8) # Linea media T-score
                ax.text(ax.get_xlim()[0], 50, ' Media Ref.', color='grey', fontsize=7, ha='left', va='bottom')
            elif is_z_score:
                max_abs_z = max(abs(v) for v in values) if values else 2
                limit = math.ceil(max_abs_z * 1.1) # Limite dinamico +10%
                ax.set_ylim(-limit, limit)
                ax.axhline(0, color='grey', linestyle='--', linewidth=0.8) # Linea media Z-score
                ax.yaxis.set_major_locator(MaxNLocator(integer=True)) # Ticks interi asse Y Z-score
            else: # Scale 0-100
                ax.set_ylim(0, 105)

        fig.tight_layout(rect=[0, 0.03, 1, 0.95]) # Aggiusta layout per fare spazio a toolbar
        canvas.draw()

    def plot_scores_0_100(self, scores):
        fig, ax = self.figs_axes["Scale 0-100"]
        canvas = self.canvases["Scale 0-100"]
        data_to_plot = {k: v for k, v in scores.items() if k in CHART_SCALE_ORDER + ['HT']} # Include HT
        self._plot_generic_bar(ax, fig, canvas, data_to_plot, "Punteggi Scale (0-100)", "Punteggio (0-100)", BILINGUAL_LABELS)

    def plot_z_scores(self, z_scores):
        fig, ax = self.figs_axes["Z-Score USA"]
        canvas = self.canvases["Z-Score USA"]
        self._plot_generic_bar(ax, fig, canvas, z_scores, "Punteggi Z (vs Pop. USA)", "Z-Score (Media=0, DS=1)", BILINGUAL_LABELS, is_z_score=True)

    def plot_summaries(self, summaries):
        fig, ax = self.figs_axes["PCS/MCS USA"]
        canvas = self.canvases["PCS/MCS USA"]
        self._plot_generic_bar(ax, fig, canvas, summaries, "Indici Sintetici (USA)", "Punteggio T (Media=50, DS=10)", BILINGUAL_LABELS, is_t_score=True)

    def plot_age_sex_t_scores(self, t_scores):
        fig, ax = self.figs_axes["T-Score Età/Sesso ITA"]
        canvas = self.canvases["T-Score Età/Sesso ITA"]
        self._plot_generic_bar(ax, fig, canvas, t_scores, "Punteggi T (vs Pop. ITA Età/Sesso)", "Punteggio T (Media=50, DS=10)", BILINGUAL_LABELS, is_t_score=True)

    def clear_all_outputs(self):
         """Pulisce area testo e tutti i grafici."""
         # Pulisci testo
         self.result_text.config(state=tk.NORMAL)
         self.result_text.delete('1.0', tk.END)
         self.result_text.insert(tk.END, "Inserire o caricare i dati per calcolare i punteggi.")
         self.result_text.config(state=tk.DISABLED)
         # Pulisci grafici
         for name, (fig, ax) in self.figs_axes.items():
             ax.clear()
             title = ""
             ylabel = ""
             is_t = "T-Score" in name or "PCS/MCS" in name
             is_z = "Z-Score" in name
             if name == "Scale 0-100": title, ylabel = "Punteggi Scale (0-100)", "Punteggio (0-100)"
             elif name == "Z-Score USA": title, ylabel = "Punteggi Z (vs Pop. USA)", "Z-Score (Media=0, DS=1)"
             elif name == "PCS/MCS USA": title, ylabel = "Indici Sintetici (USA)", "Punteggio T (Media=50, DS=10)"
             elif name == "T-Score Età/Sesso ITA": title, ylabel = "Punteggi T (vs Pop. ITA Età/Sesso)", "Punteggio T (Media=50, DS=10)"

             ax.set_title(title, pad=15, fontsize=11)
             ax.set_ylabel(ylabel, fontsize=9)
             ax.text(0.5, 0.5, "Dati non disponibili", ha='center', va='center', transform=ax.transAxes, color='gray')
             if is_t: ax.set_ylim(0, 100)
             elif is_z: ax.set_ylim(-3, 3)
             else: ax.set_ylim(0, 105)
             ax.set_xticks([])
             ax.set_yticks([])
             canvas = self.canvases[name]
             fig.tight_layout(rect=[0, 0.03, 1, 0.95])
             canvas.draw()

    # --- Funzioni Logiche GUI ---
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Seleziona File Risposte SF-36",
            filetypes=(("Excel files", "*.xlsx;*.xls"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            self.filepath.set(filename)
            # Pulisci input manuale e demografico se carico da file
            for entry_info in self.manual_entries: entry_info['var'].set("")
            self.demographic_vars['age'].set("")
            self.demographic_vars['sex'].set("")
            self.clear_all_outputs()
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, f"File selezionato: {os.path.basename(filename)}\nClicca 'Calcola da File'.")
            self.result_text.config(state=tk.DISABLED)
        else:
            self.filepath.set("Nessun file selezionato.")

    def display_results(self, results, source_info="", warnings=None):
        """Visualizza i punteggi calcolati nell'area di testo e aggiorna i grafici."""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        if results is None:
             self.result_text.insert(tk.END, f"Calcolo fallito per {source_info}.\n")
             if warnings:
                 self.result_text.insert(tk.END, "\nAVVISI:\n")
                 self.result_text.insert(tk.END, "\n".join(f"- {w}" for w in warnings))
             else:
                self.result_text.insert(tk.END, "Controllare l'input o il file.")
             self.clear_all_outputs()
        else:
            scores = results.get('scores', {})
            z_scores = results.get('z_scores', {})
            summaries = results.get('summaries', {})
            age_sex_t = results.get('age_sex_t_scores', {})
            age = self.demographic_vars['age'].get()
            sex_raw = self.demographic_vars['sex'].get()
            sex_display = sex_raw.split("(")[0].strip() if sex_raw else "N/D"
            age_sex_calculated = any(v is not None for v in age_sex_t.values())

            # Header
            self.result_text.insert(tk.END, f"Risultati SF-36 per: {source_info}\n")
            self.result_text.insert(tk.END, f"Età: {age if age else 'N/D'}, Sesso: {sex_display}\n")
            self.result_text.insert(tk.END, "="*50 + "\n")

            # Tabella Risultati
            hdr_fmt = "{:<25} {:>10} {:>10} {:>10}\n"
            row_fmt = "{:<25} {:>10} {:>10} {:>10}\n"
            self.result_text.insert(tk.END, hdr_fmt.format("Dimensione", "Score 0-100", "Z-USA", "T-Ita(Età/S)"))
            self.result_text.insert(tk.END, "-"*50 + "\n")

            for scale in SCALES_FOR_STD:
                label = BILINGUAL_LABELS.get(scale, scale).split('\n')[0] # Solo nome scala
                s_val = f"{scores.get(scale):.1f}" if scores.get(scale) is not None else "N/D"
                z_val = f"{z_scores.get(scale):.2f}" if z_scores.get(scale) is not None else "N/D"
                t_val = f"{age_sex_t.get(scale):.1f}" if age_sex_t.get(scale) is not None else "N/D"
                self.result_text.insert(tk.END, row_fmt.format(label, s_val, z_val, t_val))

            # HT (non ha Z o T)
            ht_label = BILINGUAL_LABELS.get('HT', 'HT').split('\n')[0]
            ht_val = f"{scores.get('HT'):.1f}" if scores.get('HT') is not None else "N/D"
            self.result_text.insert(tk.END, row_fmt.format(ht_label, ht_val, "-", "-"))
            self.result_text.insert(tk.END, "-"*50 + "\n")

            # Indici Sintetici
            pcs_val = f"{summaries.get('PCS'):.1f}" if summaries.get('PCS') is not None else "N/D"
            mcs_val = f"{summaries.get('MCS'):.1f}" if summaries.get('MCS') is not None else "N/D"
            self.result_text.insert(tk.END, f"{'Indice Fisico (PCS USA):':<36} {pcs_val:>10}\n")
            self.result_text.insert(tk.END, f"{'Indice Mentale (MCS USA):':<36} {mcs_val:>10}\n")
            self.result_text.insert(tk.END, "="*50 + "\n")

            if warnings:
                self.result_text.insert(tk.END, "\nAVVISI:\n")
                self.result_text.insert(tk.END, "\n".join(f"- {w}" for w in warnings) + "\n")

            if not age_sex_calculated and (age or sex_raw):
                 self.result_text.insert(tk.END, "\nNOTA: T-Scores per Età/Sesso non calcolati. Verificare input Età/Sesso.\n")

            # Aggiorna Grafici
            self.plot_scores_0_100(scores)
            self.plot_z_scores(z_scores)
            self.plot_summaries(summaries)
            self.plot_age_sex_t_scores(age_sex_t)

        self.result_text.config(state=tk.DISABLED)


    def validate_input(self, value_str, valid_range, allow_empty=True):
        """Valida un singolo input. Ritorna (valore_int | None, is_valid)."""
        if not value_str and allow_empty:
            return None, True # Vuoto è valido (mancante)
        if not value_str and not allow_empty:
             return None, False # Vuoto non permesso
        try:
            # Prova a convertire prima in float per gestire "3.0", poi in int
            val_float = float(value_str.replace(',', '.')) # Gestisce virgola decimale
            if val_float == math.floor(val_float): # È un intero
                 value_int = int(val_float)
                 if valid_range:
                     min_val, max_val = valid_range
                     if not (min_val <= value_int <= max_val):
                         return None, False # Fuori range
                 return value_int, True # Valido (con o senza check range)
            else:
                 return None, False # Non intero
        except ValueError:
            return None, False # Non numerico

    def calculate_from_manual(self):
        """Raccoglie i dati manuali, valida, calcola e visualizza."""
        answers = [None] * 36
        all_valid = True
        first_error_entry = None
        first_error_info_text = ""
        demographic_warnings = []

        # 1. Validazione Risposte Questionario
        for entry_info in self.manual_entries:
            entry_widget = entry_info['widget']
            value_str = entry_info['var'].get().strip()
            item_index = entry_info['index']
            valid_range_tuple = entry_info['range']
            label_widget = entry_info['label']

            value_int, is_valid = self.validate_input(value_str, valid_range_tuple, allow_empty=True)
            answers[item_index] = value_int

            if not is_valid:
                all_valid = False
                entry_widget.configure(style="Error.TEntry")
                if first_error_entry is None:
                     first_error_entry = entry_widget
                     q_text_full = label_widget.cget("text")
                     q_text = q_text_full.split('(')[0].strip()
                     q_range_str = f"{valid_range_tuple[0]}-{valid_range_tuple[1]}"
                     first_error_info_text = (f"Valore '{value_str}' non valido o fuori range per:\n"
                                              f"'{q_text}' (Item {item_index+1})\n"
                                              f"Range atteso: {q_range_str} (o lasciare vuoto).")
            else: # Resetta stile se era errato e ora è valido
                 if entry_widget.cget("style") == "Error.TEntry":
                     entry_widget.configure(style="Valid.TEntry")

        # 2. Validazione Dati Demografici (Età, Sesso) - Non blocca, ma avvisa
        age_str = self.demographic_vars['age'].get().strip()
        sex_str_raw = self.demographic_vars['sex'].get().strip()
        age_val, age_valid = self.validate_input(age_str, (1, 120), allow_empty=True)
        sex_val = None
        sex_valid = True # Considera valido se vuoto o selezionato correttamente

        if sex_str_raw:
             try:
                 # Estrai il numero tra parentesi
                 sex_val = int(sex_str_raw.split("(")[1].split(")")[0])
                 if sex_val not in [1, 2]:
                      sex_valid = False
                      sex_val = None
             except (IndexError, ValueError):
                 sex_valid = False
                 sex_val = None

        age_entry_widget = self.master.nametowidget('.!frame.!labelframe2.!entry') # Trova widget età
        sex_combo_widget = self.master.nametowidget('.!frame.!labelframe2.!combobox') # Trova widget sesso

        if not age_valid:
             demographic_warnings.append(f"Età '{age_str}' non valida (inserire numero intero > 0).")
             age_entry_widget.configure(style="Error.TEntry")
             if not all_valid and first_error_entry is None: # Se non c'è errore nel questionario
                  first_error_entry = age_entry_widget
                  first_error_info_text = f"Età '{age_str}' non valida. Inserire un numero intero maggiore di 0."
             # NON bloccare il calcolo per errore età/sesso
        else:
             if age_entry_widget.cget("style") == "Error.TEntry": age_entry_widget.configure(style="Valid.TEntry")

        if not sex_valid:
             demographic_warnings.append(f"Selezione Sesso '{sex_str_raw}' non valida.")
             # Non c'è stile errore per Combobox, l'avviso basta
             if not all_valid and first_error_entry is None:
                  first_error_entry = sex_combo_widget
                  first_error_info_text = f"Selezione Sesso '{sex_str_raw}' non valida. Scegliere dalla lista."
             # NON bloccare
        # else: reset stile se necessario

        # 3. Blocco Calcolo solo se Errori nel Questionario
        if not all_valid and first_error_info_text and "Età" not in first_error_info_text and "Sesso" not in first_error_info_text:
            messagebox.showerror("Errore Input Risposte", first_error_info_text)
            self.display_results(None, "Inserimento Manuale", warnings=demographic_warnings)
            if first_error_entry:
                first_error_entry.focus_set()
                # Prova a scrollare
                self.scroll_to_widget(first_error_entry)
            return

        # 4. Esegui Calcolo se risposte OK (anche se demo errati)
        if len(answers) == 36:
            # Passa età e sesso validati (possono essere None)
            results = score_sf36_ver3(answers, age=age_val, sex=sex_val)
            self.display_results(results, "Inserimento Manuale", warnings=demographic_warnings)
        else:
             messagebox.showerror("Errore Interno", "Errore nella raccolta delle 36 risposte manuali.")
             self.display_results(None, "Inserimento Manuale", warnings=demographic_warnings)


    def scroll_to_widget(self, widget):
         """Scrolla il canvas per rendere visibile il widget."""
         self.canvas.update_idletasks() # Assicura che le dimensioni siano aggiornate
         try:
             # Coordinate relative al canvas
             rel_y = widget.winfo_y()
             widget_height = widget.winfo_height()
             canvas_height = self.canvas.winfo_height()
             scroll_region = self.canvas.bbox("all")
             if not scroll_region: return # Se non c'è scroll region
             frame_height = scroll_region[3] - scroll_region[1]

             # Calcola la frazione per portare l'elemento in vista
             # Posizione desiderata: cerca di mettere il widget un po' sotto la cima
             target_y_top = rel_y - int(canvas_height * 0.1)
             target_y_bottom = rel_y + widget_height + int(canvas_height * 0.1)

             # Ottieni la vista attuale (frazione)
             current_view = self.canvas.yview() # (top_fraction, bottom_fraction)

             # Verifica se è già visibile
             widget_top_frac = rel_y / frame_height
             widget_bottom_frac = (rel_y + widget_height) / frame_height

             if not (widget_top_frac >= current_view[0] and widget_bottom_frac <= current_view[1]):
                 # Non è visibile, scrolla per centrarlo se possibile
                 scroll_fraction = max(0.0, min(1.0, (rel_y - canvas_height / 2) / frame_height))
                 self.canvas.yview_moveto(scroll_fraction)

         except Exception as e:
              print(f"Errore nello scroll automatico: {e}")


    def calculate_from_file(self):
        fpath = self.filepath.get()
        if not fpath or fpath == "Nessun file selezionato.":
            messagebox.showwarning("File Mancante", "Selezionare prima un file CSV o XLSX/XLS.")
            return

        file_basename = os.path.basename(fpath)
        warnings = []
        try:
            df = None
            # Logica lettura file (come script originale)
            if fpath.lower().endswith('.csv'):
                try: # Tenta virgola
                    df = pd.read_csv(fpath, header=None, dtype=object, sep=',', low_memory=False)
                    if df.shape[1] < 36: df = None # Verifica colonne
                except Exception: df = None
                if df is None: # Tenta punto e virgola
                     try:
                         df = pd.read_csv(fpath, header=None, dtype=object, sep=';', low_memory=False)
                         if df.shape[1] < 36: df = None
                     except Exception: df = None
                if df is None: # Fallback con engine python
                    try:
                        df = pd.read_csv(fpath, header=None, dtype=object, sep=None, engine='python', on_bad_lines='warn')
                        if df.shape[1] < 36: df = None
                    except Exception as e: raise ValueError(f"Impossibile leggere CSV: {e}")
            elif fpath.lower().endswith(('.xlsx', '.xls')):
                try:
                    engine = 'openpyxl' if fpath.lower().endswith('.xlsx') else None
                    df = pd.read_excel(fpath, header=None, dtype=object, engine=engine)
                except ImportError:
                     messagebox.showerror("Libreria Mancante", "Per leggere file .xlsx è necessaria 'openpyxl'.\nInstallala con: pip install openpyxl")
                     return
                except Exception as e: raise ValueError(f"Errore lettura Excel: {e}")
            else:
                messagebox.showerror("Formato Non Supportato", "Selezionare file .csv, .xls o .xlsx")
                return

            # Validazione DataFrame
            if df is None or df.empty:
                 raise ValueError("File vuoto o illeggibile con separatori/formati comuni.")
            if df.shape[0] < 1:
                 raise ValueError("Il file non contiene righe di dati.")
            if df.shape[1] < 36:
                 raise ValueError(f"La prima riga contiene solo {df.shape[1]} colonne (richieste >= 36).")

            # Estrai prima riga di dati (prime 36 colonne)
            raw_answers_series = df.iloc[0, :36]
            answers = [None] * 36
            conversion_errors = []
            range_errors = []

            # Validazione dati risposte
            for i, item in enumerate(raw_answers_series):
                q_info = questions_info[i]
                valid_range_tuple = q_info[3]
                val_str = str(item).strip() if not pd.isna(item) else ""

                value_int, is_valid = self.validate_input(val_str, valid_range_tuple, allow_empty=True)
                answers[i] = value_int

                if not is_valid and val_str != "": # Segnala errore solo se non era vuoto
                     q_idx_1based = q_info[0] + 1
                     q_text_short = q_info[1][:30] + "..."
                     q_range_str = q_info[2]
                     if any(c.isalpha() for c in val_str): reason = "Non numerico"
                     elif '.' in val_str or ',' in val_str: reason = "Non intero"
                     else: reason = "Fuori range"
                     error_detail = {'col': q_idx_1based, 'value': val_str, 'range': q_range_str, 'question': q_text_short, 'reason': reason}
                     if reason == "Fuori range": range_errors.append(error_detail)
                     else: conversion_errors.append(error_detail)

            # Gestione errori validazione
            max_errors_to_show = 5
            if conversion_errors:
                warnings.append(f"{len(conversion_errors)} valori non numerici/interi (trattati come mancanti):")
                for err in conversion_errors[:max_errors_to_show]: warnings.append(f"  Col {err['col']} ('{err['question']}'): '{err['value']}'")
                if len(conversion_errors) > max_errors_to_show: warnings.append("  ...")
            if range_errors:
                warnings.append(f"{len(range_errors)} valori fuori range (trattati come mancanti):")
                for err in range_errors[:max_errors_to_show]: warnings.append(f"  Col {err['col']} ('{err['question']}'): {err['value']} (Range: {err['range']})")
                if len(range_errors) > max_errors_to_show: warnings.append("  ...")

            # Estrai Età e Sesso (se presenti oltre le 36 colonne) - Non bloccante
            age_val, sex_val = None, None
            if df.shape[1] >= 37: # Colonna 37 (indice 36) per Età?
                 age_str = str(df.iloc[0, 36]).strip() if not pd.isna(df.iloc[0, 36]) else ""
                 age_val, age_valid = self.validate_input(age_str, (1, 120), allow_empty=True)
                 if not age_valid and age_str != "": warnings.append(f"Età '{age_str}' (col 37) non valida.")
                 elif age_valid: self.demographic_vars['age'].set(str(age_val)) # Aggiorna GUI se valido
                 else: self.demographic_vars['age'].set("")

            if df.shape[1] >= 38: # Colonna 38 (indice 37) per Sesso?
                 sex_str = str(df.iloc[0, 37]).strip() if not pd.isna(df.iloc[0, 37]) else ""
                 sex_val, sex_valid = self.validate_input(sex_str, (1, 2), allow_empty=True)
                 if not sex_valid and sex_str != "": warnings.append(f"Sesso '{sex_str}' (col 38) non valido (usare 1 o 2).")
                 elif sex_valid: # Aggiorna GUI Combobox
                     sex_display = f"Maschio (1)" if sex_val == 1 else f"Femmina (2)" if sex_val == 2 else ""
                     self.demographic_vars['sex'].set(sex_display)
                 else: self.demographic_vars['sex'].set("")

            # Calcola punteggi
            if len(answers) == 36:
                results = score_sf36_ver3(answers, age=age_val, sex=sex_val)
                self.display_results(results, f"File: {file_basename} (Riga 1)", warnings=warnings)
            else:
                 raise ValueError("Errore interno nell'elaborazione delle risposte.")


        except FileNotFoundError:
            messagebox.showerror("Errore", f"File non trovato: {fpath}")
            self.filepath.set("Nessun file selezionato.")
            self.display_results(None, "File Non Trovato")
        except ValueError as ve: # Cattura errori specifici di lettura/formato/colonne
             messagebox.showerror("Errore File", f"Errore lettura/formato file '{file_basename}':\n{ve}")
             self.display_results(None, f"File: {file_basename} (Errore)", warnings=warnings)
        except Exception as e:
            messagebox.showerror("Errore Inaspettato", f"Errore elaborazione file '{file_basename}':\n{type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.display_results(None, f"File: {file_basename} (Errore)", warnings=warnings)


# -----------------------------------------------------------------------------
# CLASSE HELPER PER TOOLTIP (Come script originale)
# -----------------------------------------------------------------------------
class Tooltip:
    def __init__(self, widget, text='widget info'):
        self.widget = widget; self.text = text
        self.widget.bind("<Enter>", self.enter); self.widget.bind("<Leave>", self.close); self.widget.bind("<ButtonPress>", self.close)
        self.id = None; self.tw = None
    def enter(self, event=None): self.schedule()
    def close(self, event=None): self.unschedule(); self.hidetip()
    def schedule(self): self.unschedule(); self.id = self.widget.after(700, self.showtip) # Ritardo leggermente aumentato
    def unschedule(self): id = self.id; self.id = None; self.widget.after_cancel(id) if id else None
    def showtip(self, event=None):
        if not self.widget.winfo_exists(): return # Non mostrare se il widget è distrutto
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25; y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True); self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left', background="#ffffe0", relief='solid', borderwidth=1, wraplength=450, font=("Segoe UI", 8, "normal"))
        label.pack(ipadx=2, ipady=2)
    def hidetip(self): tw = self.tw; self.tw = None; tw.destroy() if tw and tk.Toplevel.winfo_exists(tw) else None


# -----------------------------------------------------------------------------
# AVVIO APPLICAZIONE
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SF36_GUI_V3(root)
    root.mainloop()