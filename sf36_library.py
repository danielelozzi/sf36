# sf36_library.py
# Library and Command-Line Tool for SF-36 Scoring V6
# Includes: 0-100 Scores, Z-Scores (USA), PCS/MCS (USA), T-Scores (ITA, Age/Sex Specific)
# Aligned with index.html Ver6 scoring logic.

import math
import argparse
import json

# -----------------------------------------------------------------------------
# COSTANTI E DATI DI RIFERIMENTO (da index.html Ver6)
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

# --- Mappatura Indici Item, Range e Ricodifica ---
SCALE_INDICES = {
    'PF': list(range(2, 12)), 'RP': list(range(12, 16)), 'RE': list(range(16, 19)),
    'VT': [22, 26, 28, 30], 'MH': [23, 24, 25, 27, 29], 'SF': [19, 31],
    'BP': [20, 21], 'GH': [0, 32, 33, 34, 35], 'HT': [1]
}

# Range validi per ogni item (indice 0-based) -> (min, max)
ITEM_VALID_RANGES = {
    0: (1, 5), 1: (1, 5), 2: (1, 3), 3: (1, 3), 4: (1, 3), 5: (1, 3), 6: (1, 3), 7: (1, 3), 8: (1, 3), 9: (1, 3), 10: (1, 3), 11: (1, 3),
    12: (1, 2), 13: (1, 2), 14: (1, 2), 15: (1, 2), 16: (1, 2), 17: (1, 2), 18: (1, 2),
    19: (1, 5), 20: (1, 6), 21: (1, 5),
    22: (1, 6), 23: (1, 6), 24: (1, 6), 25: (1, 6), 26: (1, 6), 27: (1, 6), 28: (1, 6), 29: (1, 6), 30: (1, 6),
    31: (1, 5), 32: (1, 5), 33: (1, 5), 34: (1, 5), 35: (1, 5)
}


# Tabelle di ricodifica (Raw -> Punteggio 0-100 per l'item)
RECODE_PF = {1: 0, 2: 50, 3: 100}
RECODE_RP_RE = {1: 0, 2: 100}
RECODE_Q9_POS = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0} # 1=Sempre (meglio)
RECODE_Q9_NEG = {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100} # 1=Sempre (peggio)
RECODE_SF1 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0} # CORRETTO: 1=Per nulla (meglio) -> 100
RECODE_SF2 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100} # 1=Sempre interferito (peggio) -> 0
RECODE_BP1 = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0} # 1=Nessuno -> 100
RECODE_BP2 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0} # 1=Per nulla -> 100
RECODE_GH1 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0} # 1=Eccellente -> 100
RECODE_GH2 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100} # 1=Ammalarmi CV (peggio) -> 0
RECODE_GH3 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0} # 1=Come altri CV (meglio) -> 100
RECODE_GH4 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100} # 1=Peggiorando CV (peggio) -> 0
RECODE_GH5 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0} # 1=Ottima salute CV (meglio) -> 100
RECODE_HT = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0} # 1=Migliore -> 100

ITEM_RECODE_MAP = {
    **{i: RECODE_PF for i in SCALE_INDICES['PF']},
    **{i: RECODE_RP_RE for i in SCALE_INDICES['RP']},
    **{i: RECODE_RP_RE for i in SCALE_INDICES['RE']},
    22: RECODE_Q9_POS, 26: RECODE_Q9_POS, 28: RECODE_Q9_NEG, 30: RECODE_Q9_NEG, # VT (Pos: 9a, 9e; Neg: 9g, 9i)
    23: RECODE_Q9_NEG, 24: RECODE_Q9_NEG, 25: RECODE_Q9_POS, 27: RECODE_Q9_NEG, 29: RECODE_Q9_POS, # MH (Pos: 9d, 9h; Neg: 9b, 9c, 9f)
    19: RECODE_SF1, 31: RECODE_SF2, # SF (Q6 ora corretto, Q10)
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
        answers (list): Lista di 36 risposte (int, float, str convertibile a int, o None).
        age (int, str, optional): Età del paziente. Default None.
        sex (int, str, optional): Sesso del paziente (1='Male', 2='Female'). Default None.

    Returns:
        dict: Contiene 'scores_0_100', 'z_scores_usa', 'summary_scores_usa' (PCS/MCS),
              't_scores_ita_age_sex'. Valori sono float o None se non calcolabili.
              Include anche 'input_data' con i valori usati e eventuali 'warnings'.
    """
    if not isinstance(answers, list) or len(answers) != 36:
        raise ValueError("Input 'answers' must be a list of 36 elements.")

    processed_answers = [None] * 36
    input_warnings = []

    # 1. Process and Validate Answers
    for i, ans in enumerate(answers):
        item_range = ITEM_VALID_RANGES.get(i)
        min_val, max_val = item_range if item_range else (None, None)

        if ans is None or (isinstance(ans, str) and ans.strip().lower() in ['none', 'null', 'na', '']):
            processed_answers[i] = None
            continue

        try:
            val_num = float(str(ans).replace(',', '.')) # Handle potential float/comma input first
            if val_num != math.floor(val_num):
                 raise ValueError("Not an integer") # Consider non-integer as invalid
            val_int = int(val_num)

            if min_val is not None and max_val is not None:
                if not (min_val <= val_int <= max_val):
                     input_warnings.append(f"Answer {i+1} ('{ans}') out of range ({min_val}-{max_val}). Treated as missing.")
                     processed_answers[i] = None
                else:
                     processed_answers[i] = val_int
            else: # Should not happen with ITEM_VALID_RANGES defined
                 processed_answers[i] = val_int # Store if no range check possible

        except (ValueError, TypeError):
            input_warnings.append(f"Invalid answer {i+1} ('{ans}'). Must be integer or None. Treated as missing.")
            processed_answers[i] = None

    answers = processed_answers # Use validated & processed answers

    # 2. Process and Validate Age/Sex
    age_num = None
    sex_num = None
    if age is not None and str(age).strip() != "":
        try:
            age_num = int(float(str(age).strip()))
            if age_num <= 0:
                 input_warnings.append(f"Age '{age}' is not positive. Age/Sex T-Scores not calculated.")
                 age_num = None
        except (ValueError, TypeError):
            input_warnings.append(f"Age '{age}' is not a valid integer. Age/Sex T-Scores not calculated.")
    if sex is not None and str(sex).strip() != "":
        try:
            sex_num = int(float(str(sex).strip()))
            if sex_num not in [1, 2]:
                input_warnings.append(f"Sex '{sex}' is not 1 (Male) or 2 (Female). Age/Sex T-Scores not calculated.")
                sex_num = None
        except (ValueError, TypeError):
            input_warnings.append(f"Sex '{sex}' is not a valid integer (1 or 2). Age/Sex T-Scores not calculated.")


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

    # 3. --- Calcolo Punteggi Scale 0-100 ---
    # Uses the method of averaging the 0-100 recoded scores of valid items
    for scale, indices in SCALE_INDICES.items():
        if scale == 'HT': continue # HT calculated separately

        num_items_in_scale = len(indices)
        raw_answers_for_scale = [answers[idx] for idx in indices] # Use already validated answers

        recoded_scores = []
        valid_item_count = 0

        for i, raw_answer in enumerate(raw_answers_for_scale):
            item_index = indices[i]
            recode_map_for_item = ITEM_RECODE_MAP.get(item_index)

            # Check if raw_answer is valid (not None after initial validation)
            if raw_answer is not None and recode_map_for_item:
                recoded_value = recode_map_for_item.get(raw_answer)
                # Check if recode value exists (should always if range check passed)
                if recoded_value is not None:
                     recoded_scores.append(recoded_value)
                     valid_item_count += 1
            # else: treat None or value not in recode map (due to earlier range error) as missing

        # Calculate score if enough valid items
        min_valid = math.ceil(num_items_in_scale / 2.0) if num_items_in_scale > 1 else 1
        if valid_item_count >= min_valid:
            # Score is the average of the 0-100 contributions of the valid items
            results['scores_0_100'][scale] = sum(recoded_scores) / valid_item_count
        else:
            results['scores_0_100'][scale] = None

    # Calcolo HT (0-100)
    ht_index = SCALE_INDICES['HT'][0]
    ht_raw = answers[ht_index] # Already validated
    recode_map_ht = ITEM_RECODE_MAP.get(ht_index)
    if ht_raw is not None and recode_map_ht:
        results['scores_0_100']['HT'] = recode_map_ht.get(ht_raw)
    else:
        results['scores_0_100']['HT'] = None

    # 4. --- Calcolo Z-Scores (Standardizzazione USA) ---
    all_scores_valid_for_summaries = True
    for scale in SCALES_FOR_STD:
        score = results['scores_0_100'].get(scale)
        if score is not None and not math.isnan(score) and scale in US_MEANS and scale in US_SDS:
            try:
                if US_SDS[scale] == 0: raise ZeroDivisionError
                results['z_scores_usa'][scale] = (score - US_MEANS[scale]) / US_SDS[scale]
            except ZeroDivisionError:
                results['z_scores_usa'][scale] = None
                all_scores_valid_for_summaries = False
        else:
            results['z_scores_usa'][scale] = None
            all_scores_valid_for_summaries = False

    # 5. --- Calcolo Indici Sintetici USA (PCS/MCS) ---
    if all_scores_valid_for_summaries:
        try:
            pcs_raw = sum(results['z_scores_usa'][scale] * WEIGHTS['PCS'][scale] for scale in SCALES_FOR_STD)
            mcs_raw = sum(results['z_scores_usa'][scale] * WEIGHTS['MCS'][scale] for scale in SCALES_FOR_STD)
            results['summary_scores_usa']['PCS'] = (pcs_raw * 10) + 50
            results['summary_scores_usa']['MCS'] = (mcs_raw * 10) + 50
        except Exception: # Catch any potential issues during calculation
            results['summary_scores_usa']['PCS'] = None
            results['summary_scores_usa']['MCS'] = None
    else:
        results['summary_scores_usa']['PCS'] = None
        results['summary_scores_usa']['MCS'] = None

    # 6. --- Calcolo Punteggi T Standardizzati per Età/Sesso (ITA) ---
    # Uses age_num and sex_num validated in step 2
    age_class = 0
    can_calculate_age_sex = False

    if age_num is not None: # Already validated > 0
        if age_num <= 24: age_class = 2
        elif age_num <= 34: age_class = 3
        elif age_num <= 44: age_class = 4
        elif age_num <= 54: age_class = 5
        elif age_num <= 64: age_class = 6
        elif age_num <= 74: age_class = 7
        else: age_class = 8 # > 74

    if sex_num is not None and age_class > 0: # Sex already validated as 1 or 2
         can_calculate_age_sex = True

    if can_calculate_age_sex:
        for scale in SCALES_FOR_STD:
            score_0100 = results['scores_0_100'].get(scale)
            try:
                # Ensure keys exist before accessing
                if sex_num in AGE_SEX_NORMS and \
                   age_class in AGE_SEX_NORMS[sex_num] and \
                   scale in AGE_SEX_NORMS[sex_num][age_class]:

                    norms = AGE_SEX_NORMS[sex_num][age_class][scale]
                    mean = norms.get('mean')
                    sd = norms.get('sd')

                    if score_0100 is not None and not math.isnan(score_0100) and \
                       mean is not None and sd is not None and sd != 0:
                        t_score = (((score_0100 - mean) / sd) * 10) + 50
                        results['t_scores_ita_age_sex'][scale] = t_score
                    else:
                        # Score missing, norms missing, or SD is zero
                        results['t_scores_ita_age_sex'][scale] = None
                else:
                    # Norms not found for this specific sex/age/scale combination
                     results['t_scores_ita_age_sex'][scale] = None

            except Exception: # Catch potential errors during calculation
                results['t_scores_ita_age_sex'][scale] = None
    # else: T-scores remain None if age/sex not valid or missing

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
            # Allow potential conversion from string int/float first
            try:
                 num_val = float(part_stripped.replace(',','.')) # Handle comma decimal just in case
                 if num_val == math.floor(num_val): # Check if it's effectively an integer
                     answers.append(int(num_val))
                 else:
                     raise ValueError(f"Value '{part}' at position {i+1} is not an integer.")
            except ValueError:
                raise ValueError(f"Invalid value '{part}' at position {i+1}. Must be integer or None/blank.")
    return answers

def format_results_text(results):
    """Formatta i risultati per output testuale leggibile."""
    output = []
    output.append("--- SF-36 Calculation Results ---")

    # Input Data Info
    output.append("\nInput Data:")
    answers_display = [str(a) if a is not None else 'None' for a in results['input_data']['answers']]
    if len(answers_display) > 10:
         answers_str = ",".join(answers_display[:5]) + ",...," + ",".join(answers_display[-5:])
    else:
         answers_str = ",".join(answers_display)
    output.append(f"  Answers Used: [{answers_str}]") # Indicate these are validated/used values
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
    t_scores_available = any(v is not None for v in results['t_scores_ita_age_sex'].values())
    if not t_scores_available:
         output.append("  (Not calculated - check Age/Sex input or validity)")
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
        description="Calculate SF-36 scores (0-100, Z-USA, PCS/MCS-USA, T-ITA Age/Sex). Version 6.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--answers",
        required=True,
        help="REQUIRED. 36 comma-separated integer answers.\nUse 'None', 'null', 'na' or empty string for missing values.\nExample: '3,2,1,1,2,3,3,2,1,2,2,1,2,1,2,1,2,1,2,5,1,3,4,6,2,3,5,6,1,5,2,4,3,5,1,2'"
    )
    parser.add_argument(
        "--age",
        help="OPTIONAL. Patient's age in years (integer > 0)."
    )
    parser.add_argument(
        "--sex",
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
        # Pass age/sex directly as they might be None or strings
        results = calculate_sf36_all_scores(answers_list, age=args.age, sex=args.sex)

        if args.output_format == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(format_results_text(results))

    except ValueError as e:
        print(f"Input Error: {e}")
        parser.print_usage() # Show how to use
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# Example Usage from command line:
# python sf36_library.py --answers "3,2,1,1,2,3,3,2,1,2,2,1,2,1,2,1,2,1,2,5,1,3,4,6,2,3,5,6,1,5,2,4,3,5,1,2" --age 45 --sex 1
# python sf36_library.py --answers "...,None,..." --age 30 --sex 2 --output-format json