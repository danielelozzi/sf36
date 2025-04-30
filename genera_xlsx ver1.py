import xlsxwriter
import os

# Definizione dei range validi per domanda (indice 0-based, (min, max))
# Estratto/Adattato da questions_info dello script originale
QUESTION_RANGES = [
    (0, (1, 5)), (1, (1, 5)),
    (2, (1, 3)), (3, (1, 3)), (4, (1, 3)), (5, (1, 3)), (6, (1, 3)),
    (7, (1, 3)), (8, (1, 3)), (9, (1, 3)), (10, (1, 3)), (11, (1, 3)),
    (12, (1, 2)), (13, (1, 2)), (14, (1, 2)), (15, (1, 2)),
    (16, (1, 2)), (17, (1, 2)), (18, (1, 2)),
    (19, (1, 5)), (20, (1, 6)), (21, (1, 5)),
    (22, (1, 6)), (23, (1, 6)), (24, (1, 6)), (25, (1, 6)), (26, (1, 6)),
    (27, (1, 6)), (28, (1, 6)), (29, (1, 6)), (30, (1, 6)),
    (31, (1, 5)),
    (32, (1, 5)), (33, (1, 5)), (34, (1, 5)), (35, (1, 5))
]
# Converti in un dizionario per accesso rapido: {indice_domanda: (min, max)}
QUESTION_RANGE_DICT = {idx: rng for idx, rng in QUESTION_RANGES}

def get_excel_col_name(col_index):
    """Converts a 0-based column index into an Excel column name (A, B, ..., Z, AA, AB...)."""
    if col_index < 0:
        return ""
    col_name = ""
    while True:
        if col_name == "":
            remainder = col_index % 26
            col_name = chr(65 + remainder) # 65 is ASCII for 'A'
            col_index = col_index // 26
        else:
            col_index -= 1 # Adjust because A=0, AA=26, but calculation needs 0-25 range
            if col_index < 0:
                break
            remainder = col_index % 26
            col_name = chr(65 + remainder) + col_name
            col_index = col_index // 26

        if col_index == 0:
            break
    return col_name

def create_sf36_template_excel(filename="SF36_Calculator_Template_Validazione.xlsx", max_rows=100):
    """
    Genera un file Excel (.xlsx) con la struttura e le formule per calcolare
    i punteggi SF-36 basati sull'input manuale delle 36 risposte grezze.
    Include un istogramma dei punteggi per la prima riga di dati.
    Aggiunge formattazione condizionale per validare l'input nelle celle B2:AK{max_rows}.
    Le formule sono basate sulla logica dello script Python fornito.
    """
    try:
        # --- Crea Workbook e Worksheets ---
        workbook = xlsxwriter.Workbook(filename)
        input_ws = workbook.add_worksheet("Input & Risultati")
        recode_ws = workbook.add_worksheet("Ricodifica Items")

        # --- Formattazione ---
        bold_format = workbook.add_format({'bold': True})
        input_header_format = workbook.add_format({'bold': True, 'bg_color': '#FDE9D9', 'border': 1})
        result_header_format = workbook.add_format({'bold': True, 'bg_color': '#C5D9F1', 'border': 1})
        recode_header_format = workbook.add_format({'bold': True, 'bg_color': '#EBF1DE', 'border': 1})
        id_format = workbook.add_format({'align': 'left'})
        input_format = workbook.add_format({'align': 'center'}) # Per i numeri delle risposte
        result_format = workbook.add_format({'align': 'right', 'num_format': '0.00'}) # Per i punteggi
        nd_format = workbook.add_format({'align': 'center', 'italic': True, 'font_color': 'gray'})

        # --- NUOVI FORMATI PER VALIDAZIONE ---
        red_format = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
        green_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
        # --- ---

        # Applica formattazione condizionale per "N/D" ai risultati
        input_ws.conditional_format(f'AL2:AT{max_rows}', {'type': 'text',
                                                          'criteria': 'containing',
                                                          'value':    'N/D',
                                                          'format':   nd_format})


        # --- Definizioni Colonne e Intestazioni ---
        id_col = 0         # Col A
        input_start_col = 1 # Col B
        num_questions = 36
        input_end_col = input_start_col + num_questions - 1 # Col AK

        result_start_col = input_end_col + 1 # Col AL
        scale_names = ['PF', 'RP', 'BP', 'GH', 'VT', 'SF', 'RE', 'MH', 'HT']
        result_end_col = result_start_col + len(scale_names) - 1 # Col AT

        question_labels = [
            "Q1", "Q2", "Q3a", "Q3b", "Q3c", "Q3d", "Q3e", "Q3f", "Q3g", "Q3h", "Q3i", "Q3j",
            "Q4a", "Q4b", "Q4c", "Q4d", "Q5a", "Q5b", "Q5c", "Q6", "Q7", "Q8",
            "Q9a", "Q9b", "Q9c", "Q9d", "Q9e", "Q9f", "Q9g", "Q9h", "Q9i", "Q10",
            "Q11a", "Q11b", "Q11c", "Q11d"
        ]
        input_headers = ["ID Paziente"] + question_labels
        result_headers = scale_names
        input_ws.write_row(0, id_col, [input_headers[0]], bold_format)
        input_ws.write_row(0, input_start_col, input_headers[1:], input_header_format)
        input_ws.write_row(0, result_start_col, result_headers, result_header_format)

        recode_headers = ["ID Paziente"] + [f"Rec_{q}" for q in question_labels]
        recode_ws.write_row(0, id_col, [recode_headers[0]], bold_format)
        recode_ws.write_row(0, input_start_col, recode_headers[1:], recode_header_format)

        # --- Logica di Ricodifica (Invariata) ---
        # ... (codice delle formule di ricodifica omesso per brevità, è uguale a prima) ...
        recode_pf_formula = "IFS(val=1,0, val=2,50, val=3,100, TRUE, \"\")"
        recode_rp_re_formula = "IFS(val=1,0, val=2,100, TRUE, \"\")"
        recode_q9_pos_formula = "IFS(val=1,100, val=2,80, val=3,60, val=4,40, val=5,20, val=6,0, TRUE, \"\")"
        recode_q9_neg_formula = "IFS(val=1,0, val=2,20, val=3,40, val=4,60, val=5,80, val=6,100, TRUE, \"\")"
        recode_sf1_formula = "IFS(val=1,0, val=2,25, val=3,50, val=4,75, val=5,100, TRUE, \"\")"
        recode_sf2_formula = "IFS(val=1,0, val=2,25, val=3,50, val=4,75, val=5,100, TRUE, \"\")" # Uguale a SF1 nel python
        recode_bp1_formula = "IFS(val=1,100, val=2,80, val=3,60, val=4,40, val=5,20, val=6,0, TRUE, \"\")"
        recode_bp2_formula = "IFS(val=1,100, val=2,75, val=3,50, val=4,25, val=5,0, TRUE, \"\")"
        recode_gh1_formula = "IFS(val=1,100, val=2,75, val=3,50, val=4,25, val=5,0, TRUE, \"\")"
        recode_gh2_formula = "IFS(val=1,0, val=2,25, val=3,50, val=4,75, val=5,100, TRUE, \"\")" # Invertito
        recode_gh3_formula = "IFS(val=1,100, val=2,75, val=3,50, val=4,25, val=5,0, TRUE, \"\")"
        recode_gh4_formula = "IFS(val=1,0, val=2,25, val=3,50, val=4,75, val=5,100, TRUE, \"\")" # Invertito
        recode_gh5_formula = "IFS(val=1,100, val=2,75, val=3,50, val=4,25, val=5,0, TRUE, \"\")"
        recode_ht_formula = "IFS(val=1,100, val=2,75, val=3,50, val=4,25, val=5,0, TRUE, \"\")"

        index_to_recode_formula = {
            0: recode_gh1_formula, 1: recode_ht_formula,
            **{i: recode_pf_formula for i in range(2, 12)},
            **{i: recode_rp_re_formula for i in range(12, 16)},
            **{i: recode_rp_re_formula for i in range(16, 19)},
            19: recode_sf1_formula, 20: recode_bp1_formula, 21: recode_bp2_formula,
            22: recode_q9_pos_formula, 26: recode_q9_pos_formula, 28: recode_q9_neg_formula, 30: recode_q9_neg_formula,
            23: recode_q9_neg_formula, 24: recode_q9_neg_formula, 25: recode_q9_pos_formula, 27: recode_q9_neg_formula, 29: recode_q9_pos_formula,
            31: recode_sf2_formula,
            32: recode_gh2_formula, 33: recode_gh3_formula, 34: recode_gh4_formula, 35: recode_gh5_formula
        }
        recode_col_indices = {
            'PF': list(range(3, 13)), 'RP': list(range(13, 17)), 'RE': list(range(17, 20)),
            'VT': [23, 27, 29, 31], 'MH': [24, 25, 26, 28, 30], 'SF': [20, 32],
            'BP': [21, 22], 'GH': [1] + list(range(33, 37)), 'HT': [2]
        }

        # --- Scrittura Formule (Riga 2) ---
        target_row_excel = 2
        target_row_index = target_row_excel - 1
        id_link_formula = f"=IF('Input & Risultati'!A{target_row_excel}=\"\",\"\",'Input & Risultati'!A{target_row_excel})"
        recode_ws.write_formula(target_row_index, id_col, id_link_formula, id_format)
        for i in range(num_questions):
            input_col_index = input_start_col + i
            recode_col_index = input_start_col + i
            input_cell_addr = f"'Input & Risultati'!{get_excel_col_name(input_col_index)}{target_row_excel}"
            formula_template = index_to_recode_formula.get(i, "ERROR_NO_FORMULA")
            if formula_template != "ERROR_NO_FORMULA":
                 formula = formula_template.replace("val", input_cell_addr)
                 recode_ws.write_formula(target_row_index, recode_col_index, formula, input_format)
            else:
                 recode_ws.write(target_row_index, recode_col_index, "FORMULA MANCANTE")

        result_category_range = f"='Input & Risultati'!${get_excel_col_name(result_start_col)}$1:${get_excel_col_name(result_end_col)}$1"
        result_value_range_r2 = f"='Input & Risultati'!${get_excel_col_name(result_start_col)}${target_row_excel}:${get_excel_col_name(result_end_col)}${target_row_excel}"
        id_cell_r2 = f"='Input & Risultati'!$A${target_row_excel}"
        for i, scale in enumerate(scale_names):
            result_col_index = result_start_col + i
            recode_indices_for_scale = recode_col_indices.get(scale, [])
            if not recode_indices_for_scale:
                 formula = '"SCALA NON TROVATA"'
            else:
                 parts = []
                 start_range_idx = -1
                 sorted_recode_indices = sorted(recode_indices_for_scale)
                 for idx, current_col_idx in enumerate(sorted_recode_indices):
                     col_name = get_excel_col_name(current_col_idx)
                     cell_addr = f"'Ricodifica Items'!{col_name}{target_row_excel}"
                     is_start_of_potential_range = (start_range_idx == -1)
                     is_continuation_of_range = (idx + 1 < len(sorted_recode_indices) and
                                                 sorted_recode_indices[idx+1] == current_col_idx + 1)
                     if is_start_of_potential_range and is_continuation_of_range:
                         start_range_idx = current_col_idx
                     elif not is_continuation_of_range:
                         if start_range_idx != -1:
                             start_col_name = get_excel_col_name(start_range_idx)
                             end_col_name = col_name
                             parts.append(f"'Ricodifica Items'!{start_col_name}{target_row_excel}:{end_col_name}{target_row_excel}")
                             start_range_idx = -1
                         else:
                             parts.append(cell_addr)
                 average_ref = "; ".join(parts)
                 formula = f'=IFERROR(AVERAGE({average_ref}), "N/D")'
            input_ws.write_formula(target_row_index, result_col_index, formula, result_format)

        # --- AGGIUNTA GRAFICO (Invariato) ---
        chart_col = get_excel_col_name(result_end_col + 2)
        chart_cell = f"{chart_col}{target_row_excel}"
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name':       id_cell_r2,
            'categories': result_category_range,
            'values':     result_value_range_r2,
            'data_labels': {'value': True, 'num_format': '0.0'},
            'fill':       {'color': '#4F81BD'},
            'border':     {'color': '#385D8A'},
        })
        chart.set_title({'name': 'Punteggi Scale SF-36'})
        chart.set_y_axis({'name': 'Punteggio (0-100)', 'min': 0, 'max': 105, 'major_gridlines': {'visible': True}, 'line': {'color': '#999999'}})
        chart.set_x_axis({'line': {'color': '#999999'}})
        chart.set_legend({'position': 'none'})
        chart.set_size({'width': 550, 'height': 350})
        input_ws.insert_chart(chart_cell, chart)

        # --- AGGIUNTA FORMATTAZIONE CONDIZIONALE INPUT ---
        print("Applicazione formattazione condizionale per validazione input...")
        for question_idx in range(num_questions):
            col_idx_0based = input_start_col + question_idx # Indice colonna (0-based) in Excel
            col_letter = get_excel_col_name(col_idx_0based)
            cell_range = f"{col_letter}2:{col_letter}{max_rows}" # Range es: B2:B100
            top_left_cell = f"{col_letter}2" # Cella di riferimento per le formule

            valid_range = QUESTION_RANGE_DICT.get(question_idx)
            if valid_range:
                min_val, max_val = valid_range

                # 1. Regola VERDE: Se il valore è tra min e max
                input_ws.conditional_format(cell_range, {
                    'type': 'cell',
                    'criteria': 'between',
                    'minimum': min_val,
                    'maximum': max_val,
                    'format': green_format
                })

                # 2. Regola ROSSO: Se la cella NON è vuota E (NON è un numero O è < min O è > max)
                #    Usiamo nomi funzioni inglesi per compatibilità
                formula = f'=AND(NOT(ISBLANK({top_left_cell})), OR(NOT(ISNUMBER({top_left_cell})), {top_left_cell}<{min_val}, {top_left_cell}>{max_val}))'
                input_ws.conditional_format(cell_range, {
                     'type': 'formula',
                     'criteria': formula,
                     'format': red_format
                })
            else:
                print(f"Attenzione: Range non trovato per domanda indice {question_idx} (colonna {col_letter})")
        print("Formattazione condizionale applicata.")
        # --- FINE FORMATTAZIONE CONDIZIONALE ---


        # --- Impostazioni Finali Foglio ---
        input_ws.set_column(id_col, id_col, 15)
        input_ws.set_column(input_start_col, input_end_col, 5)
        input_ws.set_column(result_start_col, result_end_col, 8)
        # Aumenta larghezza per vedere il grafico
        input_ws.set_column(result_end_col + 1, result_end_col + 10, 8) # Colonne dopo i risultati
        input_ws.freeze_panes(1, 1)

        recode_ws.set_column(id_col, id_col, 15)
        recode_ws.set_column(input_start_col, input_end_col, 8)
        recode_ws.hide()

        input_ws.activate()

        # --- Chiusura Workbook ---
        workbook.close()
        print(f"File Excel '{filename}' creato con successo.")
        print(f"Percorso completo: {os.path.abspath(filename)}")

    except Exception as e:
        print(f"Errore durante la creazione del file Excel: {e}")
        import traceback
        traceback.print_exc()

# --- Esecuzione ---
if __name__ == "__main__":
    # Puoi aumentare max_rows se prevedi più di 100 pazienti
    create_sf36_template_excel(max_rows=100)
    # create_sf36_template_excel("Mio_Template_SF36_Validazione.xlsx", max_rows=500)
