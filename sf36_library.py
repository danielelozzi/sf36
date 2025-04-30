# sf36_calculator_cli.py
# Library and Command-Line Tool for SF-36 Scoring V3
# Includes: 0-100 Scores, Z-Scores (USA), PCS/MCS (USA), T-Scores (ITA, Age/Sex Specific)

import math
import argparse
import json

# -----------------------------------------------------------------------------
# COSTANTI E DATI DI RIFERIMENTO (da script_ver3.py)
# -----------------------------------------------------------------------------

# --- Costanti Standardizzazione USA ---
US_MEANS = { 'PF': 84.52404, 'RP': 81.19907, 'BP': 75.49196, 'GH': 72.21316, 'VT': 61.05453, 'SF': 83.59753, 'RE': 81.29467, 'MH': 74.84212 }
US_SDS   = { 'PF': 22.89490, 'RP': 33.79729, 'BP': 23.55879, 'GH': 20.16964, 'VT': 20.86942, 'SF': 22.37642, 'RE': 33.02717, 'MH': 18.01189 }
WEIGHTS = {
    'PCS': { 'PF':  0.42402, 'RP':  0.35119, 'BP':  0.31754, 'GH':  0.24954, 'VT':  0.02877, 'SF': -0.00753, 'RE': -0.19206, 'MH': -0.22069 },
    'MCS': { 'PF': -0.22999, 'RP': -0.12329, 'BP': -0.09731, 'GH': -0.01571, 'VT':  0.23534, 'SF':  0.26876, 'RE':  0.43407, 'MH':  0.48581 }
}

# --- Norme Italiane per Età/Sesso ---
AGE_SEX_NORMS = {
    1: { # Maschio
        2: {'PF':{'mean':96.4851,'sd':7.9544}, 'RP':{'mean':91.0891,'sd':19.8696}, 'BP':{'mean':90.9505,'sd':14.0124}, 'GH':{'mean':81.2079,'sd':13.1972}, 'VT':{'mean':73.1683,'sd':15.3252}, 'SF':{'mean':85.5198,'sd':17.9176}, 'RE':{'mean':84.8185,'sd':28.8770}, 'MH':{'mean':76.1980,'sd':12.7421}}, # <=24
        3: {'PF':{'mean':95.9172,'sd':10.3604}, 'RP':{'mean':90.2367,'sd':24.7175}, 'BP':{'mean':83.0888,'sd':23.1593}, 'GH':{'mean':76.9053,'sd':15.6849}, 'VT':{'mean':70.3748,'sd':15.2110}, 'SF':{'mean':84.8373,'sd':17.6337}, 'RE':{'mean':89.7436,'sd':23.8492}, 'MH':{'mean':75.3609,'sd':14.1781}}, # 25-34
        4: {'PF':{'mean':95.6915,'sd':8.0141}, 'RP':{'mean':90.5585,'sd':24.8112}, 'BP':{'mean':81.6064,'sd':22.8118}, 'GH':{'mean':71.5479,'sd':18.1271}, 'VT':{'mean':67.5709,'sd':16.9480}, 'SF':{'mean':82.9122,'sd':19.4269}, 'RE':{'mean':83.6007,'sd':31.3703}, 'MH':{'mean':73.6330,'sd':17.3180}}, # 35-44
        5: {'PF':{'mean':91.2641,'sd':14.0467}, 'RP':{'mean':88.0240,'sd':25.7183}, 'BP':{'mean':81.5621,'sd':21.8490}, 'GH':{'mean':68.3905,'sd':17.8583}, 'VT':{'mean':67.1687,'sd':18.4587}, 'SF':{'mean':80.1775,'sd':21.7579}, 'RE':{'mean':81.2121,'sd':34.1943}, 'MH':{'mean':70.7892,'sd':17.9112}}, # 45-54
        6: {'PF':{'mean':83.2193,'sd':23.8917}, 'RP':{'mean':73.0263,'sd':38.9943}, 'BP':{'mean':73.9105,'sd':27.9990}, 'GH':{'mean':61.1789,'sd':22.7691}, 'VT':{'mean':64.1534,'sd':22.1833}, 'SF':{'mean':79.2763,'sd':25.2756}, 'RE':{'mean':73.5088,'sd':39.3207}, 'MH':{'mean':69.2751,'sd':21.5863}}, # 55-64
        7: {'PF':{'mean':72.4609,'sd':26.4575}, 'RP':{'mean':65.1575,'sd':43.6615}, 'BP':{'mean':68.2656,'sd':29.3691}, 'GH':{'mean':55.4141,'sd':21.5152}, 'VT':{'mean':59.5703,'sd':21.5723}, 'SF':{'mean':76.0742,'sd':25.2949}, 'RE':{'mean':72.2222,'sd':38.8158}, 'MH':{'mean':64.5469,'sd':21.2576}}, # 65-74
        8: {'PF':{'mean':50.5556,'sd':31.2728}, 'RP':{'mean':50.9259,'sd':46.3180}, 'BP':{'mean':52.3704,'sd':31.5291}, 'GH':{'mean':41.9630,'sd':23.4376}, 'VT':{'mean':46.1111,'sd':23.4655}, 'SF':{'mean':62.2685,'sd':28.9855}, 'RE':{'mean':54.9383,'sd':44.9353}, 'MH':{'mean':57.9259,'sd':23.3722}}  # >74
    },
    2: { # Femmina
        2: {'PF':{'mean':96.8478,'sd':6.6182}, 'RP':{'mean':85.3261,'sd':31.9151}, 'BP':{'mean':82.5109,'sd':21.9452}, 'GH':{'mean':75.4239,'sd':14.1446}, 'VT':{'mean':64.2935,'sd':17.3614}, 'SF':{'mean':77.8533,'sd':23.9550}, 'RE':{'mean':74.2754,'sd':37.9908}, 'MH':{'mean':68.6957,'sd':17.8552}}, # <=24
        3: {'PF':{'mean':94.2172,'sd':13.6217}, 'RP':{'mean':90.2778,'sd':23.8342}, 'BP':{'mean':80.3182,'sd':24.5401}, 'GH':{'mean':74.3990,'sd':16.4093}, 'VT':{'mean':65.1263,'sd':17.5019}, 'SF':{'mean':78.9141,'sd':19.2784}, 'RE':{'mean':81.4815,'sd':31.9412}, 'MH':{'mean':69.8990,'sd':18.3090}}, # 25-34
        4: {'PF':{'mean':90.4054,'sd':14.4641}, 'RP':{'mean':81.4865,'sd':32.7388}, 'BP':{'mean':74.4000,'sd':24.6885}, 'GH':{'mean':69.2757,'sd':18.5749}, 'VT':{'mean':61.3514,'sd':18.5129}, 'SF':{'mean':76.7568,'sd':22.2378}, 'RE':{'mean':77.1171,'sd':37.7361}, 'MH':{'mean':63.4541,'sd':21.3136}}, # 35-44
        5: {'PF':{'mean':85.9074,'sd':16.8844}, 'RP':{'mean':75.8287,'sd':35.9302}, 'BP':{'mean':68.9560,'sd':27.1034}, 'GH':{'mean':64.1099,'sd':18.9535}, 'VT':{'mean':59.5185,'sd':19.2604}, 'SF':{'mean':76.5797,'sd':21.6724}, 'RE':{'mean':77.5641,'sd':36.1429}, 'MH':{'mean':64.3778,'sd':20.2981}}, # 45-54
        6: {'PF':{'mean':75.2448,'sd':24.5972}, 'RP':{'mean':72.8343,'sd':37.9604}, 'BP':{'mean':63.2712,'sd':28.8583}, 'GH':{'mean':58.2429,'sd':22.7831}, 'VT':{'mean':54.5198,'sd':21.5975}, 'SF':{'mean':74.5763,'sd':23.6082}, 'RE':{'mean':67.7966,'sd':41.8780}, 'MH':{'mean':57.8475,'sd':22.1273}}, # 55-64
        7: {'PF':{'mean':63.4487,'sd':27.8130}, 'RP':{'mean':55.3846,'sd':43.0189}, 'BP':{'mean':58.4231,'sd':30.9493}, 'GH':{'mean':47.4846,'sd':24.6367}, 'VT':{'mean':51.2949,'sd':23.0579}, 'SF':{'mean':70.0000,'sd':27.9118}, 'RE':{'mean':66.6667,'sd':41.2968}, 'MH':{'mean':56.3385,'sd':23.9484}}, # 65-74
        8: {'PF':{'mean':42.5000,'sd':28.5273}, 'RP':{'mean':42.0343,'sd':44.1061}, 'BP':{'mean':45.0882,'sd':29.0284}, 'GH':{'mean':38.8382,'sd':24.7390}, 'VT':{'mean':40.6618,'sd':23.4187}, 'SF':{'mean':55.5147,'sd':26.4842}, 'RE':{'mean':49.0196,'sd':46.5993}, 'MH':{'mean':48.5294,'sd':25.3351}}  # >74
    }
}

SCALES_ORDER = ['PF', 'RP', 'BP', 'GH', 'VT', 'SF', 'RE', 'MH', 'HT']
SCALES_FOR_STD = ['PF', 'RP', 'BP', 'GH', 'VT', 'SF', 'RE', 'MH']

# --- Mappatura Indici Item e Ricodifica ---
SCALE_INDICES = {
    'PF': list(range(2, 12)), 'RP': list(range(12, 16)), 'RE': list(range(16, 19)),
    'VT': [22, 26, 28, 30], 'MH': [23, 24, 25, 27, 29], 'SF': [19, 31],
    'BP': [20, 21], 'GH': [0, 32, 33, 34, 35], 'HT': [1]
}
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

ITEM_RECODE_MAP = {
    **{i: RECODE_PF for i in SCALE_INDICES['PF']},
    **{i: RECODE_RP_RE for i in SCALE_INDICES['RP']},
    **{i: RECODE_RP_RE for i in SCALE_INDICES['RE']},
    22: RECODE_Q9_POS, 26: RECODE_Q9_POS, 28: RECODE_Q9_NEG, 30: RECODE_Q9_NEG, # VT
    23: RECODE_Q9_NEG, 24: RECODE_Q9_NEG, 25: RECODE_Q9_POS, 27: RECODE_Q9_NEG, 29: RECODE_Q9_POS, # MH
    19: RECODE_SF1, 31: RECODE_SF2, # SF
    20: RECODE_BP1, 21: RECODE_BP2, # BP
    0: RECODE_GH1, 32: RECODE_GH2, 33: RECODE_GH3, 34: RECODE_GH4, 35: RECODE_GH5, # GH
    1: RECODE_HT # HT
}


# -----------------------------------------------------------------------------
# FUNZIONE DI CALCOLO PRINCIPALE
# -----------------------------------------------------------------------------

def calculate_sf36_all_scores(answers, age=None, sex=None):
    """
    Calcola punteggi SF-36 (0-100), Z-Scores (USA), PCS/MCS (USA),
    e T-Scores per Età/Sesso (ITA).

    Args:
        answers (list): Lista di 36 risposte (int o None).
        age (int, optional): Età del paziente. Default None.
        sex (int, optional): Sesso del paziente (1=Maschio, 2=Femmina). Default None.

    Returns:
        dict: Contiene 'scores_0_100', 'z_scores_usa', 'summary_scores_usa' (PCS/MCS),
              't_scores_ita_age_sex'. Valori sono float o None se non calcolabili.
              Include anche 'input_data' con i valori usati.
              Restituisce None se l'input 'answers' non è valido.
    """
    if not isinstance(answers, list) or len(answers) != 36:
        # print("Errore input: la lista di risposte deve contenere 36 elementi.")
        raise ValueError("Input 'answers' must be a list of 36 elements (int or None).")

    # Verifica tipi in input answers
    processed_answers = []
    for i, ans in enumerate(answers):
        if ans is None:
            processed_answers.append(None)
        elif isinstance(ans, int):
            processed_answers.append(ans)
        else:
            try: # Prova a convertire in int, utile se arrivano da stringa
                processed_answers.append(int(ans))
            except (ValueError, TypeError):
                 raise ValueError(f"Answer at index {i} ('{ans}') is not a valid integer or None.")

    answers = processed_answers # Usa le risposte processate

    # Verifica età e sesso
    age_num = None
    sex_num = None
    input_warnings = []
    if age is not None:
        try:
            age_num = int(age)
            if age_num <= 0:
                 input_warnings.append(f"Age '{age}' is not positive. Age/Sex T-Scores may not be calculated.")
                 age_num = None # Tratta come non valido per il calcolo T-score
        except (ValueError, TypeError):
            input_warnings.append(f"Age '{age}' is not a valid integer. Age/Sex T-Scores may not be calculated.")
    if sex is not None:
        try:
            sex_num = int(sex)
            if sex_num not in [1, 2]:
                input_warnings.append(f"Sex '{sex}' is not 1 (Male) or 2 (Female). Age/Sex T-Scores may not be calculated.")
                sex_num = None # Tratta come non valido per il calcolo T-score
        except (ValueError, TypeError):
            input_warnings.append(f"Sex '{sex}' is not a valid integer. Age/Sex T-Scores may not be calculated.")


    results = {
        'input_data': {
            'answers': answers, # Le risposte effettivamente usate
            'age_provided': age,
            'sex_provided': sex,
            'warnings': input_warnings
        },
        'scores_0_100': {scale: None for scale in SCALES_ORDER},
        'z_scores_usa': {scale: None for scale in SCALES_FOR_STD},
        'summary_scores_usa': {'PCS': None, 'MCS': None},
        't_scores_ita_age_sex': {scale: None for scale in SCALES_FOR_STD}
    }

    # 1. --- Calcolo Punteggi Scale 0-100 ---
    for scale, indices in SCALE_INDICES.items():
        if scale == 'HT': continue # HT calcolato separatamente

        num_items_in_scale = len(indices)
        # Usa le 'answers' già validate
        raw_answers_for_scale = [answers[idx] if 0 <= idx < len(answers) else None for idx in indices]

        recoded_scores = []
        valid_item_count = 0
        missing_count = 0

        for i, raw_answer in enumerate(raw_answers_for_scale):
            item_index = indices[i]
            recode_map_for_item = ITEM_RECODE_MAP.get(item_index)

            if raw_answer is not None and recode_map_for_item and raw_answer in recode_map_for_item:
                recoded_value = recode_map_for_item.get(raw_answer)
                if recoded_value is not None:
                     recoded_scores.append(recoded_value)
                     valid_item_count += 1
                else: missing_count += 1
            elif raw_answer is None:
                 missing_count += 1
            # Ignora valori non None ma non nella mappa (errore input gestito prima)

        # Calcola punteggio se abbastanza item validi
        min_valid = math.ceil(num_items_in_scale / 2.0) if num_items_in_scale > 1 else 1
        if valid_item_count >= min_valid:
            results['scores_0_100'][scale] = sum(recoded_scores) / valid_item_count
        else:
            results['scores_0_100'][scale] = None

    # Calcolo HT (0-100)
    ht_index = SCALE_INDICES['HT'][0]
    ht_raw = answers[ht_index] if 0 <= ht_index < len(answers) else None
    recode_map_ht = ITEM_RECODE_MAP.get(ht_index)
    if ht_raw is not None and recode_map_ht and ht_raw in recode_map_ht:
        results['scores_0_100']['HT'] = recode_map_ht.get(ht_raw)
    else:
        results['scores_0_100']['HT'] = None

    # 2. --- Calcolo Z-Scores (Standardizzazione USA) ---
    all_scores_valid_for_summaries = True
    for scale in SCALES_FOR_STD:
        score = results['scores_0_100'].get(scale)
        if score is not None and not math.isnan(score) and scale in US_MEANS and scale in US_SDS:
            try:
                if US_SDS[scale] == 0: raise ZeroDivisionError # Evita divisione per zero
                results['z_scores_usa'][scale] = (score - US_MEANS[scale]) / US_SDS[scale]
            except ZeroDivisionError:
                results['z_scores_usa'][scale] = None
                all_scores_valid_for_summaries = False
        else:
            results['z_scores_usa'][scale] = None
            all_scores_valid_for_summaries = False

    # 3. --- Calcolo Indici Sintetici USA (PCS/MCS) ---
    if all_scores_valid_for_summaries:
        try:
            pcs_raw = sum(results['z_scores_usa'][scale] * WEIGHTS['PCS'][scale] for scale in SCALES_FOR_STD)
            mcs_raw = sum(results['z_scores_usa'][scale] * WEIGHTS['MCS'][scale] for scale in SCALES_FOR_STD)
            results['summary_scores_usa']['PCS'] = (pcs_raw * 10) + 50
            results['summary_scores_usa']['MCS'] = (mcs_raw * 10) + 50
        except Exception as e:
            # print(f"Errore nel calcolo PCS/MCS: {e}") # Log interno
            results['summary_scores_usa']['PCS'] = None
            results['summary_scores_usa']['MCS'] = None
    else:
        results['summary_scores_usa']['PCS'] = None
        results['summary_scores_usa']['MCS'] = None

    # 4. --- Calcolo Punteggi T Standardizzati per Età/Sesso (ITA) ---
    # Usa age_num e sex_num validati all'inizio
    age_class = 0
    can_calculate_age_sex = False

    if age_num is not None and age_num > 0:
        if age_num <= 24: age_class = 2
        elif age_num <= 34: age_class = 3
        elif age_num <= 44: age_class = 4
        elif age_num <= 54: age_class = 5
        elif age_num <= 64: age_class = 6
        elif age_num <= 74: age_class = 7
        else: age_class = 8 # > 74

    if sex_num in [1, 2] and age_class in range(2, 9):
         can_calculate_age_sex = True

    if can_calculate_age_sex:
        for scale in SCALES_FOR_STD:
            score_0100 = results['scores_0_100'].get(scale)
            try:
                norms = AGE_SEX_NORMS[sex_num][age_class][scale]
                mean = norms['mean']
                sd = norms['sd']
                if score_0100 is not None and not math.isnan(score_0100) and sd is not None and sd != 0:
                    t_score = (((score_0100 - mean) / sd) * 10) + 50
                    results['t_scores_ita_age_sex'][scale] = t_score
                else:
                    results['t_scores_ita_age_sex'][scale] = None # Mancante o SD=0
            except (KeyError, TypeError, ZeroDivisionError) as e:
                # Log interno opzionale
                # print(f"Errore T-score ITA per {scale} (S={sex_num}, AC={age_class}): {e}")
                results['t_scores_ita_age_sex'][scale] = None
    # else: T-scores restano None se age/sex non validi o mancanti

    return results


# -----------------------------------------------------------------------------
# FUNZIONI HELPER PER CLI
# -----------------------------------------------------------------------------

def parse_answers(answers_str):
    """Converte stringa '1,2,None,3,...' in lista [1, 2, None, 3, ...]."""
    if not answers_str:
        raise ValueError("Answers string cannot be empty.")
    parts = answers_str.split(',')
    if len(parts) != 36:
        raise ValueError(f"Expected 36 comma-separated answers, but got {len(parts)}.")

    answers = []
    for i, part in enumerate(parts):
        part_stripped = part.strip().lower()
        if part_stripped in ['none', 'null', 'na', '']:
            answers.append(None)
        else:
            try:
                answers.append(int(part_stripped))
            except ValueError:
                raise ValueError(f"Invalid value '{part}' at position {i+1}. Must be integer or None/blank.")
    return answers

def format_results_text(results):
    """Formatta i risultati per output testuale leggibile."""
    output = []
    output.append("--- SF-36 Calculation Results ---")

    # Input Data Info
    output.append("\nInput Data:")
    # Mostra solo i primi/ultimi item per brevità
    answers_display = [str(a) if a is not None else 'None' for a in results['input_data']['answers']]
    if len(answers_display) > 10:
         answers_str = ",".join(answers_display[:5]) + ",...," + ",".join(answers_display[-5:])
    else:
         answers_str = ",".join(answers_display)
    output.append(f"  Answers: [{answers_str}]")
    output.append(f"  Age Provided: {results['input_data']['age_provided']}")
    output.append(f"  Sex Provided: {results['input_data']['sex_provided']}")
    if results['input_data']['warnings']:
        output.append("  Input Warnings:")
        for warn in results['input_data']['warnings']:
             output.append(f"    - {warn}")

    # Scores 0-100
    output.append("\nScores (0-100):")
    for scale in SCALES_ORDER:
        score = results['scores_0_100'].get(scale)
        output.append(f"  {scale:<4}: {score:.2f}" if score is not None else f"  {scale:<4}: N/D")

    # Z-Scores USA
    output.append("\nZ-Scores (USA Norms):")
    for scale in SCALES_FOR_STD:
        score = results['z_scores_usa'].get(scale)
        output.append(f"  {scale:<4}: {score:.3f}" if score is not None else f"  {scale:<4}: N/D")

    # Summary Scores USA
    output.append("\nSummary Scores (USA Norms, T-Score):")
    pcs = results['summary_scores_usa'].get('PCS')
    mcs = results['summary_scores_usa'].get('MCS')
    output.append(f"  PCS: {pcs:.2f}" if pcs is not None else "  PCS: N/D")
    output.append(f"  MCS: {mcs:.2f}" if mcs is not None else "  MCS: N/D")

    # T-Scores ITA
    output.append("\nT-Scores (Italian Norms, Age/Sex Specific):")
    # Verifica se sono stati calcolati
    t_scores_available = any(v is not None for v in results['t_scores_ita_age_sex'].values())
    if not t_scores_available:
         output.append("  (Not calculated - check Age/Sex input)")
    else:
        for scale in SCALES_FOR_STD:
            score = results['t_scores_ita_age_sex'].get(scale)
            output.append(f"  {scale:<4}: {score:.2f}" if score is not None else f"  {scale:<4}: N/D")

    output.append("\n---------------------------------")
    return "\n".join(output)

# -----------------------------------------------------------------------------
# INTERFACCIA COMMAND-LINE
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Calculate SF-36 scores (0-100, Z-USA, PCS/MCS-USA, T-ITA Age/Sex).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--answers",
        required=True,
        help="REQUIRED. 36 comma-separated integer answers.\nUse 'None', 'null', 'na' or empty string for missing values.\nExample: '3,2,1,1,2,3,3,2,1,2,2,1,2,1,2,1,2,1,2,5,1,3,4,6,2,3,5,6,1,5,2,4,3,5,1,2'"
    )
    parser.add_argument(
        "--age",
        type=int,
        help="OPTIONAL. Patient's age in years (integer > 0)."
    )
    parser.add_argument(
        "--sex",
        type=int,
        choices=[1, 2],
        help="OPTIONAL. Patient's sex (1 for Male, 2 for Female)."
    )
    parser.add_argument(
        "--output-format",
        choices=['text', 'json'],
        default='text',
        help="OPTIONAL. Output format ('text' or 'json'). Default: text."
    )

    args = parser.parse_args()

    try:
        answers_list = parse_answers(args.answers)
        results = calculate_sf36_all_scores(answers_list, age=args.age, sex=args.sex)

        if args.output_format == 'json':
            # Pulisci per JSON: rimuovi NaN, converti a tipi serializzabili se necessario
            # (In questo caso, i None sono già JSON validi)
            print(json.dumps(results, indent=2))
        else:
            print(format_results_text(results))

    except ValueError as e:
        print(f"Input Error: {e}")
        parser.print_usage() # Mostra come usare
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

# Example Usage from command line:
# python sf36_calculator_cli.py --answers "3,2,1,1,2,3,3,2,1,2,2,1,2,1,2,1,2,1,2,5,1,3,4,6,2,3,5,6,1,5,2,4,3,5,1,2" --age 45 --sex 1
# python sf36_calculator_cli.py --answers "...,None,..." --age 30 --sex 2 --output-format json

# Example Usage as library:
# import sf36_calculator_cli
# my_answers = [3, 2, 1, 1, 2, 3, 3, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 2, 5, 1, 3, 4, 6, 2, 3, 5, 6, 1, 5, 2, 4, 3, 5, 1, None]
# results_dict = sf36_calculator_cli.calculate_sf36_all_scores(my_answers, age=50, sex=2)
# print(results_dict['scores_0_100'])
# print(results_dict['t_scores_ita_age_sex']['PF'])