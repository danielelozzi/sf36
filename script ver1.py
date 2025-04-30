import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import math
import os # Per ottenere il nome del file
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# -----------------------------------------------------------------------------
# FUNZIONE DI SCORING SF-36 (Invariata - con correzioni precedenti)
# -----------------------------------------------------------------------------
def score_sf36_python(answers):
    """
    Calcola i punteggi delle 8 scale dell'SF-36v1 e della Health Transition.
    Logica basata su ricodifica per item e media della dimensione.
    Gestisce fino al 50% di valori mancanti per dimensione.
    Include correzioni specifiche per lo scoring basato sui testi italiani forniti.
    """
    if not isinstance(answers, list) or len(answers) != 36:
        print("Errore input: la lista di risposte deve contenere 36 elementi.")
        return None # Indica errore di input

    # --- Mappatura Indici (0-based) -> Item e Scale ---
    scale_indices = {
        'PF': list(range(2, 12)),   # Q3a-j (10 items) -> Indici 2-11
        'RP': list(range(12, 16)),  # Q4a-d (4 items) -> Indici 12-15
        'RE': list(range(16, 19)),  # Q5a-c (3 items) -> Indici 16-18
        'VT': [22, 26, 28, 30],      # Q9a, Q9e, Q9g, Q9i (4 items) -> Indici 22, 26, 28, 30 (Testi Q23, Q27, Q29, Q31)
        'MH': [23, 24, 25, 27, 29],  # Q9b, Q9c, Q9d, Q9f, Q9h (5 items) -> Indici 23, 24, 25, 27, 29 (Testi Q24, Q25, Q26, Q28, Q30)
        'SF': [19, 31],             # Q6, Q10 (2 items) -> Indici 19, 31 (Testi Q20, Q32)
        'BP': [20, 21],             # Q7, Q8 (2 items) -> Indici 20, 21 (Testi Q21, Q22)
        'GH': [0, 32, 33, 34, 35],   # Q1, Q11a-d (5 items) -> Indici 0, 32, 33, 34, 35 (Testi Q1, Q33, Q34, Q35, Q36)
        'HT': [1]                    # Q2 (1 item) -> Indice 1 (Testo Q2)
    }

    # --- Tabelle di Ricodifica (Raw -> Punteggio Item 0-100) ---
    # Verificate e corrette secondo i testi italiani dove necessario (punteggio alto = salute migliore)
    RECODE_PF = {1: 0, 2: 50, 3: 100}       # Q3a-j (1=Limitato Molto, 2=Limitato Poco, 3=Non Limitato)
    RECODE_RP_RE = {1: 0, 2: 100}           # Q4a-d, Q5a-c (1=Sì [limitazione], 2=No [limitazione])
    RECODE_Q9_POS = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0} # Q9a,e,d,h -> Sentimenti positivi (1=Sempre, 6=Mai)
    RECODE_Q9_NEG = {1: 0, 2: 20, 3: 40, 4: 60, 5: 80, 6: 100} # Q9b,c,f,g,i -> Sentimenti negativi (1=Sempre(0), 6=Mai(100)) - invertito
    RECODE_SF1 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}            # Q6 (idx 19, testo Q20) Interferenza sociale (1=Moltissimo(0), 5=Per niente(100))
    RECODE_SF2 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}            # Q10 (idx 31, testo Q32) Interferenza sociale tempo (1=Sempre(0), 5=Mai(100))
    RECODE_BP1 = {1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 0}     # Q7 (idx 20, testo Q21) Intensità dolore (1=Nessuno(100), 6=Moltissimo(0))
    RECODE_BP2 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}            # Q8 (idx 21, testo Q22) Interferenza dolore (1=Per niente(100), 5=Moltissimo(0))
    RECODE_GH1 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}            # Q1 (idx 0, testo Q1) Salute generale (1=Ottima(100), 5=Pessima(0))
    RECODE_GH2 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}            # Q11a (idx 32, testo Q33) Ammalarsi (1=Vero(0), 5=Falso(100)) - invertito
    RECODE_GH3 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}            # Q11b (idx 33, testo Q34) Salute=altri (1=Vero(100), 5=Falso(0))
    RECODE_GH4 = {1: 0, 2: 25, 3: 50, 4: 75, 5: 100}            # Q11c (idx 34, testo Q35) Peggiorerà (1=Vero(0), 5=Falso(100)) - invertito
    RECODE_GH5 = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}            # Q11d (idx 35, testo Q36) Ottima salute (1=Vero(100), 5=Falso(0))
    RECODE_HT = {1: 100, 2: 75, 3: 50, 4: 25, 5: 0}            # Q2 (idx 1, testo Q2) Salute vs anno fa (1=Migliore(100), 5=Peggiore(0))

    # --- Dizionario delle Mappe di Ricodifica per Indice ---
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

    results = {}

    # --- Calcolo Punteggi Scale (escluso HT) ---
    for scale, indices in scale_indices.items():
        if scale == 'HT': continue

        num_items_in_scale = len(indices)
        raw_answers_for_scale = []
        for idx in indices:
             if 0 <= idx < len(answers):
                 raw_answers_for_scale.append(answers[idx])
             else:
                 raw_answers_for_scale.append(None) # Indice fuori range

        recoded_scores = []
        valid_item_count = 0
        missing_count = 0

        for i, raw_answer in enumerate(raw_answers_for_scale):
            item_index = indices[i]
            recode_map_for_item = item_recode_map.get(item_index)

            if raw_answer is not None and recode_map_for_item and raw_answer in recode_map_for_item:
                recoded_value = recode_map_for_item.get(raw_answer)
                if recoded_value is not None: # Doppia sicurezza
                     recoded_scores.append(recoded_value)
                     valid_item_count += 1
                else: # Caso strano: valore in mappa ma restituisce None
                     missing_count += 1
            else: # Risposta mancante o non valida per la ricodifica
                 missing_count += 1

        # Verifica se ci sono troppi valori mancanti
        if missing_count > num_items_in_scale / 2:
            results[scale] = None # Troppi mancanti, punteggio non calcolabile
        elif valid_item_count == 0:
             results[scale] = None # Nessun item valido (es. tutti mancanti ma <= 50%)
        else:
            # Calcola la media sui punteggi validi ricodificati
            results[scale] = sum(recoded_scores) / valid_item_count

    # --- Calcolo Health Transition (HT) ---
    ht_index = scale_indices['HT'][0]
    ht_raw = answers[ht_index] if 0 <= ht_index < len(answers) else None
    recode_map_ht = item_recode_map.get(ht_index)

    if ht_raw is not None and recode_map_ht and ht_raw in recode_map_ht:
        results['HT'] = recode_map_ht.get(ht_raw)
    else:
        results['HT'] = None # Mancante o non valido

    return results

# -----------------------------------------------------------------------------
# DEFINIZIONE DOMANDE E RANGE VALIDI (Invariata)
# -----------------------------------------------------------------------------
questions_info = [
    # (indice 0-based, Testo Domanda, Range Atteso Stringa, Range Atteso Tuple (min, max))
    (0, "1. In generale direbbe che la Sua salute è....", "1-5", (1, 5)),
    (1, "2. Rispetto a un anno fa, come giudicherebbe, ora, la Sua salute in generale?", "1-5", (1, 5)),
    (2, "3a. Attività fisicamente impegnative, come correre, sollevare oggetti pesanti...", "1-3", (1, 3)), # PF1
    (3, "3b. Attività di moderato impegno fisico, come spostare un tavolo, usare l'aspirapolvere...", "1-3", (1, 3)), # PF2
    (4, "3c. Sollevare o portare le borse della spesa", "1-3", (1, 3)), # PF3
    (5, "3d. Salire qualche piano di scale", "1-3", (1, 3)), # PF4
    (6, "3e. Salire un piano di scale", "1-3", (1, 3)), # PF5
    (7, "3f. Piegarsi, inginocchiarsi o chinarsi", "1-3", (1, 3)), # PF6
    (8, "3g. Camminare per un chilometro", "1-3", (1, 3)), # PF7
    (9, "3h. Camminare per qualche centinaia di metri", "1-3", (1, 3)), # PF8
    (10, "3i. Camminare per circa cento metri", "1-3", (1, 3)), # PF9
    (11, "3j. Fare il bagno o vestirsi da soli", "1-3", (1, 3)), # PF10
    (12, "4a. (Nelle ultime 4 sett.) Ha ridotto il tempo dedicato al lavoro o ad altre attività [causa salute fisica]?", "1-2", (1, 2)), # RP1
    (13, "4b. (Nelle ultime 4 sett.) Ha reso meno di quanto avrebbe voluto [causa salute fisica]?", "1-2", (1, 2)), # RP2
    (14, "4c. (Nelle ultime 4 sett.) Ha dovuto limitare alcuni tipi di lavoro o di altre attività [causa salute fisica]?", "1-2", (1, 2)), # RP3
    (15, "4d. (Nelle ultime 4 sett.) Ha avuto difficoltà nell'eseguire il lavoro o altre attività [causa salute fisica]?", "1-2", (1, 2)), # RP4
    (16, "5a. (Nelle ultime 4 sett.) Ha ridotto il tempo dedicato al lavoro o ad altre attività [causa stato emotivo]?", "1-2", (1, 2)), # RE1
    (17, "5b. (Nelle ultime 4 sett.) Ha reso meno di quanto avrebbe voluto [causa stato emotivo]?", "1-2", (1, 2)), # RE2
    (18, "5c. (Nelle ultime 4 sett.) Ha avuto un calo di concentrazione sul lavoro o in altre attività [causa stato emotivo]?", "1-2", (1, 2)), # RE3
    (19, "6. (Nelle ultime 4 sett.) In che misura la Sua salute fisica o il Suo stato emotivo hanno interferito con le normali attività sociali?", "1-5", (1, 5)), # SF1
    (20, "7. Quanto dolore fisico ha provato nelle ultime 4 settimane?", "1-6", (1, 6)), # BP1
    (21, "8. (Nelle ultime 4 sett.) In che misura il dolore L'ha ostacolata nel lavoro che svolge abitualmente?", "1-5", (1, 5)), # BP2
    (22, "9a. (Nelle ultime 4 sett., per quanto tempo) si è sentito vivace brillante?", "1-6", (1, 6)), # VT1
    (23, "9b. (Nelle ultime 4 sett., per quanto tempo) si è sentito molto agitato?", "1-6", (1, 6)), # MH1
    (24, "9c. (Nelle ultime 4 sett., per quanto tempo) si è sentito così giù di morale che niente avrebbe potuto tirarLa su?", "1-6", (1, 6)), # MH2
    (25, "9d. (Nelle ultime 4 sett., per quanto tempo) si è sentito calmo e sereno?", "1-6", (1, 6)), # MH3
    (26, "9e. (Nelle ultime 4 sett., per quanto tempo) si è sentito pieno di energia?", "1-6", (1, 6)), # VT2
    (27, "9f. (Nelle ultime 4 sett., per quanto tempo) si è sentito scoraggiato e triste?", "1-6", (1, 6)), # MH4
    (28, "9g. (Nelle ultime 4 sett., per quanto tempo) si è sentito sfinito?", "1-6", (1, 6)), # VT3
    (29, "9h. (Nelle ultime 4 sett., per quanto tempo) si è sentito felice?", "1-6", (1, 6)), # MH5
    (30, "9i. (Nelle ultime 4 sett., per quanto tempo) si è sentito stanco?", "1-6", (1, 6)), # VT4
    (31, "10. (Nelle ultime 4 sett.) Per quanto tempo la Sua salute fisica o il Suo stato emotivo hanno interferito nelle Sue attività sociali, in famiglia, con gli amici?", "1-5", (1, 5)), # SF2 (Nota: Questo corrisponde a Q10 standard, ma nel testo fornito è Q32 con indice 31)
    (32, "11a. Mi pare di ammalarmi un po' più facilmente degli altri", "1-5", (1, 5)), # GH1
    (33, "11b. La mia salute è come quella degli altri", "1-5", (1, 5)), # GH2
    (34, "11c. Mi aspetto che la mia salute andrà peggiorando", "1-5", (1, 5)), # GH3
    (35, "11d. Godo di ottima salute", "1-5", (1, 5)), # GH4
]

# -----------------------------------------------------------------------------
# ETICHETTE BILINGUE PER IL GRAFICO (Invariata)
# -----------------------------------------------------------------------------
BILINGUAL_LABELS = {
    'PF': "PF\nPhysical Functioning", # Attività Fisica
    'RP': "RP\nRole Physical",       # Limitazione Ruolo Fisico
    'BP': "BP\nBodily Pain",         # Dolore Fisico
    'GH': "GH\nGeneral Health",      # Salute Generale Percepita
    'VT': "VT\nVitality",            # Vitalità/Energia
    'SF': "SF\nSocial Functioning",  # Funzionamento Sociale
    'RE': "RE\nRole Emotional",      # Limitazione Ruolo Emotivo
    'MH': "MH\nMental Health",       # Salute Mentale
    'HT': "HT\nHealth Transition"    # Cambiamento Salute
}
SCALE_ORDER = ['PF', 'RP', 'BP', 'GH', 'VT', 'SF', 'RE', 'MH', 'HT'] # Ordine per display e grafico

# -----------------------------------------------------------------------------
# CLASSE DELLA GUI
# -----------------------------------------------------------------------------
class SF36_GUI:
    def __init__(self, master):
        self.master = master
        master.title("SF-36 Scorer (Python + Grafico)")
        # Aumentata altezza minima per assicurare visibilità bottone
        master.geometry("950x850")
        master.minsize(950, 800) # Altezza minima aumentata

        self.style = ttk.Style()
        try:
            self.style.theme_use('clam') # Tema consigliato
        except tk.TclError:
            print("Tema 'clam' non disponibile, usando default.")

        self.style.configure("Error.TEntry", fieldbackground="#ffecec", foreground="red")
        self.style.map("Error.TEntry", fieldbackground=[('focus', '#ffdddd')])
        self.style.configure("Valid.TEntry", foreground="black")

        self.filepath = tk.StringVar()
        self.manual_entries = []

        # --- Layout Principale ---
        # Frame superiore per input (file e manuale + bottone manuale)
        top_input_frame = ttk.Frame(master)
        top_input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Frame inferiore per output (risultati e grafico)
        results_frame = ttk.Frame(master)
        results_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 10)) # Aggiunto padding sotto

        # --- Controlli File (in top_input_frame) ---
        self.file_frame = ttk.LabelFrame(top_input_frame, text="Carica da File", padding=(10, 5))
        self.file_frame.pack(pady=5, fill=tk.X, side=tk.TOP, anchor='n') # In cima al frame input

        self.browse_button = ttk.Button(self.file_frame, text="Sfoglia...", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        self.file_label = ttk.Label(self.file_frame, textvariable=self.filepath, relief=tk.SUNKEN, width=60)
        self.file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.filepath.set("Nessun file selezionato.")
        self.calc_file_button = ttk.Button(self.file_frame, text="Calcola da File", command=self.calculate_from_file)
        self.calc_file_button.pack(side=tk.LEFT, padx=5)

        # --- Inserimento Manuale (in top_input_frame) ---
        self.manual_frame_container = ttk.LabelFrame(top_input_frame, text="Inserimento Manuale", padding=(10, 5))
        # Occupa lo spazio rimanente nel frame input dopo il file frame
        self.manual_frame_container.pack(pady=5, fill=tk.BOTH, expand=True, side=tk.TOP)

        self.canvas = tk.Canvas(self.manual_frame_container, borderwidth=0, background="#ffffff")
        self.scrollbar = ttk.Scrollbar(self.manual_frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="scrollable_frame")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.create_manual_entries(self.scrollable_frame)

        # --- Bottone Calcolo Manuale (in top_input_frame) ---
        # **POSIZIONATO QUI:** Sotto l'area di inserimento manuale, dentro lo stesso frame logico
        self.calc_manual_button = ttk.Button(top_input_frame, text="Calcola da Inserimento Manuale", command=self.calculate_from_manual)
        self.calc_manual_button.pack(side=tk.TOP, pady=(5, 10)) # Sotto manual_frame_container

        # --- Risultati Testuali (in results_frame) ---
        self.result_text_frame = ttk.LabelFrame(results_frame, text="Risultati Punteggi (0-100)", padding=(10, 5))
        self.result_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5, padx=(0,5))
        self.result_text = scrolledtext.ScrolledText(self.result_text_frame, height=12, width=45, wrap=tk.WORD, state=tk.DISABLED, font=("Segoe UI", 9))
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # --- Grafico (in results_frame) ---
        self.plot_frame = ttk.LabelFrame(results_frame, text="Grafico Punteggi", padding=(10, 5))
        self.plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5, padx=(5,0))

        plt.style.use('seaborn-v0_8-whitegrid')
        self.fig, self.ax = plt.subplots(figsize=(6, 4.5), dpi=100)
        # Spazio aggiustato per etichette asse X potenzialmente lunghe
        self.fig.subplots_adjust(bottom=0.28, top=0.9, left=0.12, right=0.95)

        self.ax.set_ylim(0, 105)
        self.ax.set_ylabel("Punteggio (0-100)")
        self.ax.set_title("Punteggi Scale SF-36", pad=15)

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_tk_widget = self.canvas_widget.get_tk_widget()
        self.canvas_tk_widget.pack(fill=tk.BOTH, expand=True)
        self.clear_plot() # Disegna grafico iniziale


    def on_frame_configure(self, event=None):
        """Chiamato quando scrollable_frame cambia dimensione."""
        # Aggiorna la scrollregion del canvas per adattarsi al contenuto
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Aggiorna il wraplength delle label delle domande
        # Calcola la larghezza disponibile nel frame scrollabile
        # La larghezza del canvas è una buona approssimazione se il frame lo riempie
        parent_width = self.canvas.winfo_width()
        # Sottrai spazio per scrollbar (se visibile) e padding/entry
        entry_width_approx = 80 # Stima generosa per entry+padding
        wrap_length = max(150, parent_width - entry_width_approx - self.scrollbar.winfo_width())

        # Aggiorna tutte le label nel frame scrollabile
        for item in self.scrollable_frame.winfo_children():
             if isinstance(item, ttk.Frame): # Ogni riga è un Frame
                 for widget in item.winfo_children():
                     if isinstance(widget, ttk.Label) and hasattr(widget, 'original_text'):
                         # Potrebbe essere necessario chiamare update_idletasks prima per avere la larghezza corretta
                         # Ma proviamo senza per ora per evitare potenziali loop
                         widget.configure(wraplength=wrap_length)

        # Riconfigura la larghezza della finestra nel canvas se necessario
        # self.canvas.itemconfig('scrollable_frame', width=self.canvas.winfo_width())


    def _on_mousewheel(self, event):
        """Gestisce lo scroll della rotellina del mouse sul canvas manuale."""
        if event.num == 4: delta = -1 # Linux scroll up
        elif event.num == 5: delta = 1  # Linux scroll down
        elif hasattr(event, 'delta'): # Windows/Mac
             delta = -1 if event.delta > 0 else 1
        else: return # Evento non riconosciuto

        # Applica lo scroll solo se il mouse è sopra il canvas o i suoi figli diretti
        widget_under_mouse = self.master.winfo_containing(event.x_root, event.y_root)
        target_canvas = self.canvas # Il canvas che vogliamo scrollare

        # Verifica se il widget sotto il mouse è il canvas target o un suo discendente
        parent = widget_under_mouse
        while parent is not None:
            if parent == target_canvas:
                target_canvas.yview_scroll(delta, "units")
                break
            # Evita loop infinito se arriva alla root senza trovare il canvas
            if parent == self.master:
                break
            parent = parent.master # Sali nella gerarchia dei widget


    def create_manual_entries(self, parent_frame):
        """Crea le 36 label e entry per l'inserimento manuale."""
        self.manual_entries = []
        initial_wrap_length = 600 # Valore iniziale, verrà aggiornato da on_frame_configure

        for i, (idx, q_text, q_range_str, q_range_tuple) in enumerate(questions_info):
            row_frame = ttk.Frame(parent_frame)
            row_frame.pack(fill=tk.X, pady=2, padx=5)

            # Label Domanda (testo completo, a capo automatico)
            # expand=True fa sì che prenda lo spazio extra orizzontale
            # fill=tk.X la fa allargare per riempire lo spazio assegnato
            lbl_q = ttk.Label(row_frame, text=f"{q_text} ({q_range_str})", anchor=tk.W, justify=tk.LEFT, wraplength=initial_wrap_length)
            lbl_q.original_text = q_text
            # NOTA: expand=True qui permette alla label di usare lo spazio extra quando la finestra si allarga
            lbl_q.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

            # Entry per Risposta (larghezza fissa)
            entry_var = tk.StringVar()
            entry = ttk.Entry(row_frame, width=5, textvariable=entry_var, style="Valid.TEntry", justify=tk.CENTER)
            entry.pack(side=tk.LEFT, padx=(0, 5)) # Allineata a sinistra dopo la label
            self.manual_entries.append({'widget': entry, 'var': entry_var, 'index': idx, 'range': q_range_tuple, 'label': lbl_q})

            Tooltip(widget=lbl_q, text=f"Item {idx+1}: {q_text}\nRange: {q_range_str}")
            Tooltip(widget=entry, text=f"Inserire {q_range_str} o lasciare vuoto")

        # Forza un configure iniziale per aggiustare wraplength dopo aver creato tutto
        parent_frame.update_idletasks()
        self.on_frame_configure()


    def plot_scores(self, scores):
        """Aggiorna il grafico a barre con i nuovi punteggi."""
        self.ax.clear()

        plot_data = {scale: scores[scale] for scale in SCALE_ORDER if (score := scores.get(scale)) is not None and not math.isnan(score)}

        if not plot_data:
            self.ax.text(0.5, 0.5, "Nessun punteggio valido calcolato", horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes, fontsize=10, color='gray')
            self.ax.set_title("Punteggi Scale SF-36", pad=15)
            self.ax.set_ylabel("Punteggio (0-100)", fontsize=10)
            self.ax.set_ylim(0, 105)
            self.ax.set_xticks([])
            self.ax.set_xticklabels([])
        else:
            scales_in_plot = list(plot_data.keys())
            values = list(plot_data.values())
            bilingual_x_labels = [BILINGUAL_LABELS.get(scale, scale) for scale in scales_in_plot]

            bars = self.ax.bar(bilingual_x_labels, values, color='cornflowerblue', width=0.7)
            self.ax.set_ylim(0, 105)
            self.ax.set_ylabel("Punteggio (0-100)", fontsize=10)
            self.ax.set_title("Punteggi Scale SF-36", pad=15, fontsize=12)
            # self.ax.grid(axis='y', linestyle='--', alpha=0.7) # Già incluso con stile seaborn

            self.ax.bar_label(bars, fmt='{:.1f}', padding=3, fontsize=9)

            self.ax.tick_params(axis='x', labelsize=9)
            self.ax.tick_params(axis='y', labelsize=9)

        # self.fig.tight_layout() # A volte utile, ma può confliggere con subplots_adjust
        self.canvas_widget.draw()

    def clear_plot(self):
         """Pulisce il grafico e mostra un messaggio placeholder."""
         self.ax.clear()
         self.ax.set_ylim(0, 105)
         self.ax.set_ylabel("Punteggio (0-100)", fontsize=10)
         self.ax.set_title("Punteggi Scale SF-36", pad=15, fontsize=12)
         self.ax.text(0.5, 0.5, "Inserire o caricare i dati\nper calcolare i punteggi",
                      horizontalalignment='center', verticalalignment='center',
                      transform=self.ax.transAxes, fontsize=10, color='gray', linespacing=1.5)
         self.ax.set_xticks([])
         self.ax.set_xticklabels([])
         # self.fig.tight_layout()
         self.canvas_widget.draw()


    def browse_file(self):
        """Apre la finestra di dialogo per selezionare il file."""
        filename = filedialog.askopenfilename(
            title="Seleziona File Risposte SF-36",
            filetypes=(("Excel files", "*.xlsx;*.xls"), ("CSV files", "*.csv"), ("All files", "*.*")) # Aggiunto .xls
        )
        if filename:
            self.filepath.set(filename)
            for entry_info in self.manual_entries:
                entry_info['var'].set("")
                entry_info['widget'].configure(style="Valid.TEntry")
            self.clear_plot()
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, f"File selezionato: {os.path.basename(filename)}\nClicca 'Calcola da File'.")
            self.result_text.config(state=tk.DISABLED)
        else:
            self.filepath.set("Nessun file selezionato.")

    def display_results(self, scores, source_info=""):
        """Visualizza i punteggi calcolati nell'area di testo e aggiorna il grafico."""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        if scores is None:
             self.result_text.insert(tk.END, f"Calcolo fallito per {source_info}.\nControllare l'input o il file (formato, valori mancanti, range).")
             self.clear_plot()
        else:
            self.result_text.insert(tk.END, f"Punteggi SF-36 ({source_info}):\n")
            self.result_text.insert(tk.END, "="*35 + "\n")
            for scale in SCALE_ORDER:
                score = scores.get(scale)
                score_str = f"{score:.2f}" if score is not None and not math.isnan(score) else "N/D"
                full_label = BILINGUAL_LABELS.get(scale, scale).replace('\n', ' - ')
                self.result_text.insert(tk.END, f"{full_label:<30}: {score_str:>6}\n")
            self.result_text.insert(tk.END, "="*35 + "\n")
            self.plot_scores(scores)

        self.result_text.config(state=tk.DISABLED)

    def validate_manual_input(self, value_str, valid_range):
        """Valida un singolo input manuale. Ritorna (valore_int | None, is_valid)."""
        if not value_str:
            return None, True # Vuoto è valido (mancante)
        try:
            value_int = int(float(value_str)) # Gestisce "3.0"
            min_val, max_val = valid_range
            if not (min_val <= value_int <= max_val):
                return None, False # Fuori range
            return value_int, True # Valido
        except ValueError:
            return None, False # Non numerico

    def calculate_from_manual(self):
        """Raccoglie i dati manuali, valida, calcola e visualizza."""
        answers = [None] * 36
        all_valid = True
        first_error_entry = None
        first_error_info_text = ""

        for entry_info in self.manual_entries:
            entry_widget = entry_info['widget']
            value_str = entry_info['var'].get().strip()
            item_index = entry_info['index']
            valid_range_tuple = entry_info['range']
            label_widget = entry_info['label']

            value_int, is_valid = self.validate_manual_input(value_str, valid_range_tuple)
            answers[item_index] = value_int

            if not is_valid:
                all_valid = False
                entry_widget.configure(style="Error.TEntry")
                if first_error_entry is None:
                     first_error_entry = entry_widget
                     q_text_full = label_widget.cget("text") # Prende testo completo con range
                     q_text = q_text_full.split('(')[0].strip()
                     q_range_str = f"{valid_range_tuple[0]}-{valid_range_tuple[1]}"
                     first_error_info_text = (f"Valore '{value_str}' non valido o fuori range per:\n"
                                              f"'{q_text}'\n"
                                              f"Inserire un numero intero tra {q_range_str} o lasciare vuoto.")
            else:
                 current_style = entry_widget.cget("style")
                 if current_style == "Error.TEntry":
                     entry_widget.configure(style="Valid.TEntry")

        if not all_valid:
            messagebox.showerror("Errore Input Manuale", first_error_info_text)
            self.display_results(None, "Inserimento Manuale (Errore Input)")
            if first_error_entry:
                first_error_entry.focus_set()
                # Scrolla al widget errato
                self.canvas.update_idletasks()
                try:
                    # Calcola y relativa all'interno dello scrollable_frame
                    widget_y = first_error_entry.winfo_y()
                    frame_height = self.scrollable_frame.winfo_height()
                    canvas_height = self.canvas.winfo_height()

                    # Calcola la frazione per portare l'elemento in cima
                    scroll_fraction_top = widget_y / frame_height
                    # Calcola la frazione per centrare (se possibile)
                    scroll_fraction_center = max(0.0, scroll_fraction_top - (canvas_height / (2 * frame_height)))

                    # Muovi la vista (prova a centrare)
                    self.canvas.yview_moveto(scroll_fraction_center)

                except Exception as e:
                     print(f"Errore nello scroll automatico all'errore: {e}")
            return

        # Se tutto valido, calcola
        if len(answers) == 36:
            scores = score_sf36_python(answers)
            self.display_results(scores, "Inserimento Manuale")
        else:
             messagebox.showerror("Errore Interno", "Errore nella raccolta delle 36 risposte manuali.")
             self.display_results(None, "Inserimento Manuale (Errore Interno)")


    def calculate_from_file(self):
        """Legge il file selezionato, estrae i dati, valida, calcola e visualizza."""
        fpath = self.filepath.get()
        if not fpath or fpath == "Nessun file selezionato.":
            messagebox.showwarning("File Mancante", "Selezionare prima un file CSV o XLSX/XLS.")
            return

        file_basename = os.path.basename(fpath)

        try:
            df = None # Inizializza df
            if fpath.lower().endswith('.csv'):
                try: # Tenta virgola
                    df_test = pd.read_csv(fpath, header=None, dtype=object, sep=',', nrows=1, on_bad_lines='skip')
                    if df_test.shape[1] >= 36: df = pd.read_csv(fpath, header=None, dtype=object, sep=',')
                except Exception: pass # Ignora errore e prova altro separatore
                if df is None: # Tenta punto e virgola
                     try:
                         df_test = pd.read_csv(fpath, header=None, dtype=object, sep=';', nrows=1, on_bad_lines='skip')
                         if df_test.shape[1] >= 36: df = pd.read_csv(fpath, header=None, dtype=object, sep=';')
                     except Exception: pass
                if df is None: # Fallback con engine python
                    try: df = pd.read_csv(fpath, header=None, dtype=object, sep=None, engine='python', on_bad_lines='warn')
                    except Exception as e: raise ValueError(f"Impossibile leggere il CSV con separatori comuni o engine Python: {e}")

            elif fpath.lower().endswith(('.xlsx', '.xls')):
                # Specifica engine='openpyxl' per .xlsx e verifica installazione
                try:
                    df = pd.read_excel(fpath, header=None, dtype=object, engine='openpyxl' if fpath.lower().endswith('.xlsx') else None)
                except ImportError:
                     messagebox.showerror("Libreria Mancante", "Per leggere file .xlsx è necessaria la libreria 'openpyxl'.\nInstallala con il comando:\npip install openpyxl")
                     return
                except Exception as e:
                     raise ValueError(f"Errore durante la lettura del file Excel: {e}")
            else:
                messagebox.showerror("Formato File Non Supportato", "Selezionare un file .csv, .xls o .xlsx")
                return

            if df is None or df.empty:
                 messagebox.showerror("Errore File", f"Il file '{file_basename}' è vuoto o non è stato possibile leggerlo correttamente.")
                 self.display_results(None, f"File: {file_basename} (Vuoto/Illeggibile)")
                 return

            if df.shape[0] < 1:
                 messagebox.showerror("Errore File", f"Il file '{file_basename}' non contiene righe di dati.")
                 self.display_results(None, f"File: {file_basename} (No Dati)")
                 return
            if df.shape[1] < 36:
                 messagebox.showerror("Errore File", f"La prima riga del file '{file_basename}' contiene solo {df.shape[1]} colonne. Ne sono richieste almeno 36.")
                 self.display_results(None, f"File: {file_basename} (Colonne Insuff.)")
                 return

            raw_answers_series = df.iloc[0, :36]
            answers = [None] * 36
            conversion_errors = []
            range_errors = []

            for i, item in enumerate(raw_answers_series):
                current_value = None
                q_info = questions_info[i]
                q_idx_1based = q_info[0] + 1
                q_text = q_info[1]
                valid_range_tuple = q_info[3]
                valid_range_str = q_info[2]

                if pd.isna(item) or str(item).strip() == '':
                    current_value = None
                else:
                    try:
                        val_str = str(item).strip().replace(',', '.')
                        val_float = float(val_str)
                        if val_float == math.floor(val_float):
                             val_int = int(val_float)
                             current_value = val_int
                             if not (valid_range_tuple[0] <= current_value <= valid_range_tuple[1]):
                                 range_errors.append({'col': q_idx_1based, 'value': current_value, 'range': valid_range_str, 'question': q_text})
                                 current_value = None
                        else:
                             conversion_errors.append({'col': q_idx_1based, 'value': item, 'question': q_text, 'reason': 'Non intero'})
                             current_value = None
                    except (ValueError, TypeError):
                         conversion_errors.append({'col': q_idx_1based, 'value': item, 'question': q_text, 'reason': 'Non numerico'})
                         current_value = None

                answers[i] = current_value

            error_messages = []
            max_errors_to_show = 5

            if conversion_errors:
                error_messages.append(f"ATTENZIONE: {len(conversion_errors)} valori non convertiti in numero intero (trattati come mancanti):")
                for err in conversion_errors[:max_errors_to_show]:
                     error_messages.append(f"  - Col {err['col']} ('{err['question'][:30]}...'): Valore '{err['value']}' ({err['reason']})")
                if len(conversion_errors) > max_errors_to_show: error_messages.append(f"  - ... e altri {len(conversion_errors) - max_errors_to_show}")

            if range_errors:
                error_messages.append(f"\nATTENZIONE: {len(range_errors)} valori fuori dal range atteso (trattati come mancanti):")
                for err in range_errors[:max_errors_to_show]:
                    error_messages.append(f"  - Col {err['col']} ('{err['question'][:30]}...'): Valore {err['value']} (Range: {err['range']})")
                if len(range_errors) > max_errors_to_show: error_messages.append(f"  - ... e altri {len(range_errors) - max_errors_to_show}")

            if error_messages:
                messagebox.showwarning("Problemi Dati nel File", "\n".join(error_messages))

            if len(answers) == 36:
                scores = score_sf36_python(answers)
                self.display_results(scores, f"File: {file_basename}")
            else:
                 messagebox.showerror("Errore Interno", "Errore nell'elaborazione delle risposte dal file dopo la validazione.")
                 self.display_results(None, f"File: {file_basename} (Errore Interno)")

        except FileNotFoundError:
            messagebox.showerror("Errore", f"File non trovato: {fpath}")
            self.filepath.set("Nessun file selezionato.")
            self.display_results(None, "File Non Trovato")
        except ValueError as ve: # Cattura errori specifici di lettura/formato
             messagebox.showerror("Errore Lettura File", f"Errore durante la lettura o l'interpretazione del file '{file_basename}':\n{ve}")
             self.display_results(None, f"File: {file_basename} (Errore Lettura/Formato)")
        except Exception as e:
            messagebox.showerror("Errore Inaspettato", f"Errore durante la lettura o elaborazione del file '{file_basename}':\n{type(e).__name__}: {e}")
            import traceback
            print("--- TRACEBACK ERRORE FILE ---")
            traceback.print_exc()
            print("-----------------------------")
            self.display_results(None, f"File: {file_basename} (Errore Elaborazione)")

# -----------------------------------------------------------------------------
# CLASSE HELPER PER TOOLTIP (Invariata - con fix precedente)
# -----------------------------------------------------------------------------
class Tooltip:
    """ Crea un tooltip per un widget Tkinter. """
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
        self.widget.bind("<ButtonPress>", self.close)
        self.id = None
        self.tw = None

    def enter(self, event=None): self.schedule()
    def close(self, event=None): self.unschedule(); self.hidetip()
    def schedule(self): self.unschedule(); self.id = self.widget.after(600, self.showtip)
    def unschedule(self): id = self.id; self.id = None; self.widget.after_cancel(id) if id else None

    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       wraplength = 450, font=("Segoe UI", 8, "normal"))
        label.pack(ipadx=2, ipady=2)

    def hidetip(self):
        tw = self.tw; self.tw = None
        if tw: tw.destroy()

# -----------------------------------------------------------------------------
# AVVIO APPLICAZIONE
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SF36_GUI(root)
    root.mainloop()
