# GUI Script for SF-36 Scorer V6
# Uses sf36_library.py for calculations.
# Includes: 0-100 Scores, Z-Scores (USA), PCS/MCS (USA), T-Scores (ITA, Age/Sex Specific)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import math
import os # Per ottenere il nome del file
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator

# --- IMPORTA LA LIBRERIA DI CALCOLO ---
# Assicurati che sf36_library.py sia nella stessa cartella
try:
    import sf36_library
except ImportError:
    messagebox.showerror("Errore Importazione", "Errore: il file 'sf36_library.py' non è stato trovato.\nAssicurati che sia nella stessa cartella di questo script.")
    exit()

# --- Usa le costanti dalla libreria ---
SCALES_ORDER = sf36_library.SCALES_ORDER
SCALES_FOR_STD = sf36_library.SCALES_FOR_STD
ITEM_VALID_RANGES = sf36_library.ITEM_VALID_RANGES # Usiamo i range dalla libreria

# -----------------------------------------------------------------------------
# DEFINIZIONE DOMANDE (SOLO PER GUI Labels/Tooltips)
# Manteniamo questa per avere i testi delle domande nella GUI
# -----------------------------------------------------------------------------
questions_info = [
    # (indice 0-based, Testo Domanda GUI, Range Stringa (per tooltip), Range Tuple dalla libreria)
    (0, "1. Salute generale", "1-5", ITEM_VALID_RANGES.get(0)),
    (1, "2. Salute rispetto a 1 anno fa", "1-5", ITEM_VALID_RANGES.get(1)),
    (2, "3a. Attività fisicamente impegnative", "1-3", ITEM_VALID_RANGES.get(2)),
    (3, "3b. Attività moderato impegno fisico", "1-3", ITEM_VALID_RANGES.get(3)),
    (4, "3c. Sollevare/portare borse spesa", "1-3", ITEM_VALID_RANGES.get(4)),
    (5, "3d. Salire qualche piano scale", "1-3", ITEM_VALID_RANGES.get(5)),
    (6, "3e. Salire un piano scale", "1-3", ITEM_VALID_RANGES.get(6)),
    (7, "3f. Piegarsi/inginocchiarsi", "1-3", ITEM_VALID_RANGES.get(7)),
    (8, "3g. Camminare per 1 km", "1-3", ITEM_VALID_RANGES.get(8)),
    (9, "3h. Camminare per centinaia di metri", "1-3", ITEM_VALID_RANGES.get(9)),
    (10, "3i. Camminare per 100 metri", "1-3", ITEM_VALID_RANGES.get(10)),
    (11, "3j. Fare bagno/vestirsi", "1-3", ITEM_VALID_RANGES.get(11)),
    (12, "4a. Ridotto tempo (causa fisica)", "1-2", ITEM_VALID_RANGES.get(12)),
    (13, "4b. Reso meno (causa fisica)", "1-2", ITEM_VALID_RANGES.get(13)),
    (14, "4c. Limitato tipi lavoro (causa fisica)", "1-2", ITEM_VALID_RANGES.get(14)),
    (15, "4d. Difficoltà lavoro (causa fisica)", "1-2", ITEM_VALID_RANGES.get(15)),
    (16, "5a. Ridotto tempo (causa emotiva)", "1-2", ITEM_VALID_RANGES.get(16)),
    (17, "5b. Reso meno (causa emotiva)", "1-2", ITEM_VALID_RANGES.get(17)),
    (18, "5c. Calo concentrazione (causa emotiva)", "1-2", ITEM_VALID_RANGES.get(18)),
    (19, "6. Interferenza salute/emotività attività sociali?", "1-5", ITEM_VALID_RANGES.get(19)),
    (20, "7. Quanto dolore fisico?", "1-6", ITEM_VALID_RANGES.get(20)),
    (21, "8. Interferenza dolore nel lavoro?", "1-5", ITEM_VALID_RANGES.get(21)),
    (22, "9a. Sentito vivace?", "1-6", ITEM_VALID_RANGES.get(22)),
    (23, "9b. Sentito agitato?", "1-6", ITEM_VALID_RANGES.get(23)),
    (24, "9c. Sentito giù morale?", "1-6", ITEM_VALID_RANGES.get(24)),
    (25, "9d. Sentito calmo?", "1-6", ITEM_VALID_RANGES.get(25)),
    (26, "9e. Sentito pieno energia?", "1-6", ITEM_VALID_RANGES.get(26)),
    (27, "9f. Sentito scoraggiato?", "1-6", ITEM_VALID_RANGES.get(27)),
    (28, "9g. Sentito sfinito?", "1-6", ITEM_VALID_RANGES.get(28)),
    (29, "9h. Sentito felice?", "1-6", ITEM_VALID_RANGES.get(29)),
    (30, "9i. Sentito stanco?", "1-6", ITEM_VALID_RANGES.get(30)),
    (31, "10. Interferenza salute/emotività attività sociali (tempo)?", "1-5", ITEM_VALID_RANGES.get(31)),
    (32, "11a. Ammalarmi facilmente (V/F)", "1-5", ITEM_VALID_RANGES.get(32)),
    (33, "11b. Salute come altri (V/F)", "1-5", ITEM_VALID_RANGES.get(33)),
    (34, "11c. Salute peggiorerà (V/F)", "1-5", ITEM_VALID_RANGES.get(34)),
    (35, "11d. Ottima salute (V/F)", "1-5", ITEM_VALID_RANGES.get(35)),
]

# -----------------------------------------------------------------------------
# ETICHETTE BILINGUE PER IL GRAFICO (Stesse della versione precedente)
# -----------------------------------------------------------------------------
BILINGUAL_LABELS = {
    'PF': "PF\nPhysical Functioning", 'RP': "RP\nRole Physical", 'BP': "BP\nBodily Pain",
    'GH': "GH\nGeneral Health", 'VT': "VT\nVitality", 'SF': "SF\nSocial Functioning",
    'RE': "RE\nRole Emotional", 'MH': "MH\nMental Health", 'HT': "HT\nHealth Transition",
    'PCS': 'PCS\nPhysical Comp. Summary', 'MCS': 'MCS\nMental Comp. Summary'
}
CHART_SCALE_ORDER = ['PF', 'RP', 'BP', 'GH', 'VT', 'SF', 'RE', 'MH'] # Per grafici standardizzati


# -----------------------------------------------------------------------------
# CLASSE DELLA GUI (Aggiornata per usare sf36_library)
# -----------------------------------------------------------------------------
class SF36_GUI_V6: # Aggiornato nome classe per chiarezza
    def __init__(self, master):
        self.master = master
        master.title("SF-36 Scorer V6 (Libreria Esterna)") # Titolo aggiornato
        master.geometry("1100x900")
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
        self.demographic_vars = {
            'age': tk.StringVar(),
            'sex': tk.StringVar()
        }

        # --- Layout Principale (invariato) ---
        top_input_frame = ttk.Frame(master, padding=10)
        top_input_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        bottom_output_frame = ttk.Frame(master, padding=(10,0,10,10))
        bottom_output_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # --- Controlli File (invariato) ---
        file_frame = ttk.LabelFrame(top_input_frame, text="Carica da File", padding=10)
        file_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        browse_button = ttk.Button(file_frame, text="Sfoglia...", command=self.browse_file)
        browse_button.pack(side=tk.LEFT, padx=5)
        file_label = ttk.Label(file_frame, textvariable=self.filepath, relief=tk.SUNKEN, width=50)
        file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        calc_file_button = ttk.Button(file_frame, text="Calcola da File", command=self.calculate_from_file)
        calc_file_button.pack(side=tk.LEFT, padx=5)

        # --- Controlli Demografici (invariato) ---
        demo_frame = ttk.LabelFrame(top_input_frame, text="Dati Demografici (per Standardizzazione)", padding=10)
        demo_frame.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")
        ttk.Label(demo_frame, text="Età:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        age_entry = ttk.Entry(demo_frame, textvariable=self.demographic_vars['age'], width=5, justify=tk.CENTER)
        age_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        Tooltip(age_entry, "Inserire età in anni")
        ttk.Label(demo_frame, text="Sesso:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        sex_combo = ttk.Combobox(demo_frame, textvariable=self.demographic_vars['sex'], values=["", "Maschio (1)", "Femmina (2)"], width=12, state="readonly")
        sex_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        sex_combo.current(0)
        Tooltip(sex_combo, "Selezionare sesso biologico (1 o 2)")
        top_input_frame.columnconfigure(0, weight=1)
        top_input_frame.columnconfigure(1, weight=0)

        # --- Inserimento Manuale (invariato nella struttura) ---
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
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.create_manual_entries(self.scrollable_frame)

        # --- Bottone Calcolo Manuale (invariato) ---
        calc_manual_button = ttk.Button(master, text="Calcola da Inserimento Manuale", command=self.calculate_from_manual)
        calc_manual_button.pack(side=tk.TOP, pady=(0, 10))

        # --- Output Frame (invariato nella struttura) ---
        result_text_frame = ttk.LabelFrame(bottom_output_frame, text="Risultati Numerici", padding=10)
        result_text_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0,10))
        self.result_text = scrolledtext.ScrolledText(result_text_frame, height=25, width=55, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 9))
        self.result_text.pack(fill=tk.BOTH, expand=True)

        plot_notebook = ttk.Notebook(bottom_output_frame)
        plot_notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.plot_frames = {}
        tab_names = ["Scale 0-100", "Z-Score USA", "PCS/MCS USA", "T-Score Età/Sesso ITA"]
        for name in tab_names:
             frame = ttk.Frame(plot_notebook, padding=5)
             plot_notebook.add(frame, text=name)
             self.plot_frames[name] = frame

        plt.style.use('seaborn-v0_8-whitegrid')
        self.figs_axes = {}
        self.canvases = {}
        self.toolbars = {}

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
        figSum, axSum = plt.subplots(figsize=(4, 4), dpi=90)
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

        self.clear_all_outputs()

    # --- Metodi di supporto GUI (on_frame_configure, _on_mousewheel) invariati ---
    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        parent_width = self.canvas.winfo_width()
        entry_width_approx = 80
        scrollbar_width = self.scrollbar.winfo_width() if self.scrollbar.winfo_ismapped() else 0
        wrap_length = max(150, parent_width - entry_width_approx - scrollbar_width - 20)
        for item in self.scrollable_frame.winfo_children():
             if isinstance(item, ttk.Frame):
                 for widget in item.winfo_children():
                     if isinstance(widget, ttk.Label) and hasattr(widget, 'original_text'):
                         widget.configure(wraplength=wrap_length)

    def _on_mousewheel(self, event):
        if event.num == 4: delta = -1
        elif event.num == 5: delta = 1
        elif hasattr(event, 'delta'):
            if isinstance(event.delta, int): delta = -1 if event.delta > 0 else 1
            else: return
        else: return
        widget_under_mouse = self.master.winfo_containing(event.x_root, event.y_root)
        target_canvas = self.canvas
        parent = widget_under_mouse
        is_descendant = False
        while parent is not None:
            if parent == target_canvas: is_descendant = True; break
            if parent == self.master: break
            try: parent = parent.master
            except AttributeError: break
        if is_descendant: target_canvas.yview_scroll(delta, "units")

    # --- Metodo create_manual_entries (invariato nella logica, usa q_info aggiornato) ---
    def create_manual_entries(self, parent_frame):
        self.manual_entries = []
        initial_wrap_length = 600
        for i, (idx, q_text, q_range_str, q_range_tuple) in enumerate(questions_info):
            row_frame = ttk.Frame(parent_frame)
            row_frame.pack(fill=tk.X, pady=2, padx=5)
            q_label_text = f"{q_text} ({q_range_str})"
            lbl_q = ttk.Label(row_frame, text=q_label_text, anchor=tk.W, justify=tk.LEFT, wraplength=initial_wrap_length)
            lbl_q.original_text = q_text
            lbl_q.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
            entry_var = tk.StringVar()
            entry = ttk.Entry(row_frame, width=5, textvariable=entry_var, style="Valid.TEntry", justify=tk.CENTER)
            entry.pack(side=tk.LEFT, padx=(0, 5))
            self.manual_entries.append({'widget': entry, 'var': entry_var, 'index': idx, 'range': q_range_tuple, 'label': lbl_q})
            Tooltip(widget=lbl_q, text=f"Item {idx+1}: {q_text}\nRange: {q_range_str}")
            Tooltip(widget=entry, text=f"Inserire {q_range_str} o lasciare vuoto")
        parent_frame.update_idletasks()
        self.on_frame_configure()

    # --- Funzioni Plotting (invariate nella logica) ---
    def _plot_generic_bar(self, ax, fig, canvas, data, title, ylabel, labels_map, is_t_score=False, is_z_score=False):
        ax.clear()
        plot_data = {k: v for k, v in data.items() if v is not None and not (isinstance(v, float) and math.isnan(v))}
        if not plot_data:
            ax.text(0.5, 0.5, "Nessun dato valido", ha='center', va='center', transform=ax.transAxes, color='gray')
            ax.set_title(title, pad=15, fontsize=11); ax.set_ylabel(ylabel, fontsize=9); ax.set_yticks([]); ax.set_xticks([])
        else:
            scales_in_plot = list(plot_data.keys()); values = list(plot_data.values())
            bilingual_x_labels = [labels_map.get(scale, scale).replace('\n', ' ') for scale in scales_in_plot]
            colors = plt.cm.viridis([i/len(scales_in_plot) for i in range(len(scales_in_plot))])
            bars = ax.bar(bilingual_x_labels, values, color=colors, width=0.7)
            ax.set_ylabel(ylabel, fontsize=9); ax.set_title(title, pad=15, fontsize=11)
            ax.tick_params(axis='x', labelsize=8, rotation=45, ha='right'); ax.tick_params(axis='y', labelsize=8)
            ax.bar_label(bars, fmt='{:.1f}', padding=3, fontsize=7)
            if is_t_score:
                ax.set_ylim(0, 100); ax.axhline(50, color='grey', linestyle='--', linewidth=0.8)
                ax.text(ax.get_xlim()[0], 50, ' Media Ref.', color='grey', fontsize=7, ha='left', va='bottom')
            elif is_z_score:
                max_abs_z = max(abs(v) for v in values) if values else 2; limit = math.ceil(max_abs_z * 1.1)
                ax.set_ylim(-limit, limit); ax.axhline(0, color='grey', linestyle='--', linewidth=0.8)
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            else: ax.set_ylim(0, 105)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95]); canvas.draw()

    def plot_scores_0_100(self, scores):
        fig, ax = self.figs_axes["Scale 0-100"]; canvas = self.canvases["Scale 0-100"]
        data_to_plot = {k: v for k, v in scores.items() if k in SCALES_ORDER} # SCALES_ORDER from library
        self._plot_generic_bar(ax, fig, canvas, data_to_plot, "Punteggi Scale (0-100)", "Punteggio (0-100)", BILINGUAL_LABELS)

    def plot_z_scores(self, z_scores):
        fig, ax = self.figs_axes["Z-Score USA"]; canvas = self.canvases["Z-Score USA"]
        self._plot_generic_bar(ax, fig, canvas, z_scores, "Punteggi Z (vs Pop. USA)", "Z-Score (Media=0, DS=1)", BILINGUAL_LABELS, is_z_score=True)

    def plot_summaries(self, summaries):
        fig, ax = self.figs_axes["PCS/MCS USA"]; canvas = self.canvases["PCS/MCS USA"]
        self._plot_generic_bar(ax, fig, canvas, summaries, "Indici Sintetici (USA)", "Punteggio T (Media=50, DS=10)", BILINGUAL_LABELS, is_t_score=True)

    def plot_age_sex_t_scores(self, t_scores):
        fig, ax = self.figs_axes["T-Score Età/Sesso ITA"]; canvas = self.canvases["T-Score Età/Sesso ITA"]
        self._plot_generic_bar(ax, fig, canvas, t_scores, "Punteggi T (vs Pop. ITA Età/Sesso)", "Punteggio T (Media=50, DS=10)", BILINGUAL_LABELS, is_t_score=True)

    # --- Metodo clear_all_outputs (invariato) ---
    def clear_all_outputs(self):
         self.result_text.config(state=tk.NORMAL)
         self.result_text.delete('1.0', tk.END)
         self.result_text.insert(tk.END, "Inserire o caricare i dati per calcolare i punteggi.")
         self.result_text.config(state=tk.DISABLED)
         for name, (fig, ax) in self.figs_axes.items():
             ax.clear(); title = ""; ylabel = ""; is_t = "T-Score" in name or "PCS/MCS" in name; is_z = "Z-Score" in name
             if name == "Scale 0-100": title, ylabel = "Punteggi Scale (0-100)", "Punteggio (0-100)"
             elif name == "Z-Score USA": title, ylabel = "Punteggi Z (vs Pop. USA)", "Z-Score (Media=0, DS=1)"
             elif name == "PCS/MCS USA": title, ylabel = "Indici Sintetici (USA)", "Punteggio T (Media=50, DS=10)"
             elif name == "T-Score Età/Sesso ITA": title, ylabel = "Punteggi T (vs Pop. ITA Età/Sesso)", "Punteggio T (Media=50, DS=10)"
             ax.set_title(title, pad=15, fontsize=11); ax.set_ylabel(ylabel, fontsize=9)
             ax.text(0.5, 0.5, "Dati non disponibili", ha='center', va='center', transform=ax.transAxes, color='gray')
             if is_t: ax.set_ylim(0, 100)
             elif is_z: ax.set_ylim(-3, 3)
             else: ax.set_ylim(0, 105)
             ax.set_xticks([]); ax.set_yticks([])
             canvas = self.canvases[name]; fig.tight_layout(rect=[0, 0.03, 1, 0.95]); canvas.draw()

    # --- Metodo browse_file (invariato) ---
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Seleziona File Risposte SF-36",
            filetypes=(("Excel files", "*.xlsx;*.xls"), ("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            self.filepath.set(filename); self.clear_all_outputs()
            for entry_info in self.manual_entries: entry_info['var'].set("")
            self.demographic_vars['age'].set(""); self.demographic_vars['sex'].set("")
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, f"File selezionato: {os.path.basename(filename)}\nClicca 'Calcola da File'.")
            self.result_text.config(state=tk.DISABLED)
        else:
            self.filepath.set("Nessun file selezionato.")

    # --- Metodo display_results (Aggiornato per usare struttura risultati libreria) ---
    def display_results(self, results, source_info=""):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        if results is None: # Gestione errore generico (es. libreria non trovata)
             self.result_text.insert(tk.END, f"Calcolo fallito per {source_info}.\nControllare input/file o presenza di 'sf36_library.py'.")
             self.clear_all_outputs()
        elif isinstance(results, dict): # Verifica che results sia un dizionario atteso
            input_data = results.get('input_data', {})
            warnings = input_data.get('warnings', [])
            scores = results.get('scores_0_100', {})
            z_scores = results.get('z_scores_usa', {})
            summaries = results.get('summary_scores_usa', {})
            age_sex_t = results.get('t_scores_ita_age_sex', {})

            age_provided = input_data.get('age_provided', 'N/D')
            sex_provided = input_data.get('sex_provided', 'N/D')
            sex_display_map = {'1': 'Maschio', '2': 'Femmina'}
            sex_str = str(sex_provided).strip()
            sex_display = sex_display_map.get(sex_str, "N/D" if not sex_str else f"Inv({sex_str})")

            age_sex_calculated = any(v is not None for v in age_sex_t.values())

            # Header
            self.result_text.insert(tk.END, f"Risultati SF-36 per: {source_info}\n")
            self.result_text.insert(tk.END, f"Età Fornita: {age_provided}, Sesso Fornito: {sex_display}\n")
            self.result_text.insert(tk.END, "="*50 + "\n")

            # Tabella Risultati
            hdr_fmt = "{:<25} {:>10} {:>10} {:>10}\n"
            row_fmt = "{:<25} {:>10} {:>10} {:>10}\n"
            self.result_text.insert(tk.END, hdr_fmt.format("Dimensione", "Score 0-100", "Z-USA", "T-Ita(Età/S)"))
            self.result_text.insert(tk.END, "-"*50 + "\n")

            for scale in SCALES_FOR_STD: # Usa SCALES_FOR_STD dalla libreria
                label = BILINGUAL_LABELS.get(scale, scale).split('\n')[0]
                s_val = f"{scores.get(scale):.1f}" if scores.get(scale) is not None else "N/D"
                z_val = f"{z_scores.get(scale):.2f}" if z_scores.get(scale) is not None else "N/D"
                t_val = f"{age_sex_t.get(scale):.1f}" if age_sex_t.get(scale) is not None else "N/D"
                self.result_text.insert(tk.END, row_fmt.format(label, s_val, z_val, t_val))

            # HT
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
                self.result_text.insert(tk.END, "\nAVVISI INPUT/CALCOLO:\n")
                self.result_text.insert(tk.END, "\n".join(f"- {w}" for w in warnings) + "\n")

            if not age_sex_calculated and (age_provided or sex_provided) and \
               not any("Age/Sex T-Scores not calculated" in w for w in warnings):
                 # Aggiunge nota solo se età/sesso forniti ma T non calcolati per altre ragioni (es. SD=0)
                 self.result_text.insert(tk.END, "\nNOTA: T-Scores per Età/Sesso non calcolati (potrebbe mancare norma specifica o SD=0).\n")

            # Aggiorna Grafici
            self.plot_scores_0_100(scores)
            self.plot_z_scores(z_scores)
            self.plot_summaries(summaries)
            self.plot_age_sex_t_scores(age_sex_t)
        else:
             # Se 'results' non è un dizionario (errore inatteso)
             self.result_text.insert(tk.END, f"Errore inatteso durante il calcolo per {source_info}.\nTipo risultato: {type(results)}")
             self.clear_all_outputs()


        self.result_text.config(state=tk.DISABLED)


    # --- Metodo validate_input (semplificato, la libreria ora fa validazione range) ---
    def validate_input(self, value_str, allow_empty=True):
        """Valida se è vuoto o potenzialmente numerico (int/float)."""
        if not value_str and allow_empty:
            return None, True # Vuoto è valido (mancante)
        if not value_str and not allow_empty:
             return None, False # Vuoto non permesso
        try:
            float(value_str.replace(',', '.')) # Tenta conversione a float
            return value_str, True # Ritorna stringa originale se numerica
        except ValueError:
            return None, False # Non numerico

    # --- Metodo calculate_from_manual (Aggiornato per chiamare libreria) ---
    def calculate_from_manual(self):
        answers_raw = [] # Raccoglie le stringhe dalle entry
        has_input_error = False
        first_error_widget = None
        first_error_text = ""

        # 1. Raccolta Input e Validazione Formato Base (Non-vuoto vs Numerico)
        for entry_info in self.manual_entries:
            entry_widget = entry_info['widget']
            value_str = entry_info['var'].get().strip()
            answers_raw.append(value_str if value_str else None) # Passa None se vuoto

            # Validazione base per feedback GUI immediato
            _, is_valid_format = self.validate_input(value_str, allow_empty=True)
            if not is_valid_format:
                 has_input_error = True
                 entry_widget.configure(style="Error.TEntry")
                 if first_error_widget is None:
                     first_error_widget = entry_widget
                     item_index = entry_info['index']
                     q_info = questions_info[item_index]
                     q_text_short = q_info[1]
                     q_range_str = q_info[2]
                     first_error_text = f"Valore '{value_str}' non numerico per:\n'{q_text_short}' (Item {item_index+1}).\nInserire numero ({q_range_str}) o lasciare vuoto."
            else:
                 if entry_widget.cget("style") == "Error.TEntry": entry_widget.configure(style="Valid.TEntry")

        # Se ci sono errori di formato base, ferma e mostra messaggio
        if has_input_error:
             messagebox.showerror("Errore Input Risposte", first_error_text)
             self.display_results(None, "Inserimento Manuale") # Pulisce output
             if first_error_widget: first_error_widget.focus_set(); self.scroll_to_widget(first_error_widget)
             return

        # 2. Raccolta Dati Demografici (stringhe)
        age_str = self.demographic_vars['age'].get().strip()
        sex_str_raw = self.demographic_vars['sex'].get().strip()
        sex_str = None
        if sex_str_raw: # Estrai '1' o '2' se selezionato
             try: sex_str = sex_str_raw.split("(")[1].split(")")[0]
             except IndexError: pass # Lascia None se formato inatteso

        # 3. Chiama la Libreria (che farà validazione range e calcolo)
        try:
            results = sf36_library.calculate_sf36_all_scores(answers_raw, age=age_str, sex=sex_str)
            self.display_results(results, "Inserimento Manuale")

            # Aggiorna stile Age/Sex in base agli warnings della libreria
            age_entry_widget = self.master.nametowidget('.!frame.!labelframe2.!entry')
            sex_combo_widget = self.master.nametowidget('.!frame.!labelframe2.!combobox')
            age_had_warning = any("Age" in w for w in results.get('input_data',{}).get('warnings',[]))
            sex_had_warning = any("Sex" in w for w in results.get('input_data',{}).get('warnings',[]))
            age_entry_widget.configure(style="Error.TEntry" if age_had_warning else "Valid.TEntry")
            # Non c'è stile errore per combobox

        except Exception as e:
             messagebox.showerror("Errore Calcolo", f"Errore durante il calcolo SF-36:\n{type(e).__name__}: {e}")
             self.display_results(None, "Inserimento Manuale")
             import traceback; traceback.print_exc()


    # --- Metodo scroll_to_widget (invariato) ---
    def scroll_to_widget(self, widget):
         self.canvas.update_idletasks()
         try:
             rel_y = widget.winfo_y(); widget_height = widget.winfo_height(); canvas_height = self.canvas.winfo_height()
             scroll_region = self.canvas.bbox("all"); frame_height = scroll_region[3] - scroll_region[1] if scroll_region else canvas_height
             if frame_height == 0: return
             current_view = self.canvas.yview()
             widget_top_frac = rel_y / frame_height; widget_bottom_frac = (rel_y + widget_height) / frame_height
             if not (widget_top_frac >= current_view[0] and widget_bottom_frac <= current_view[1]):
                 scroll_fraction = max(0.0, min(1.0, (rel_y - canvas_height / 2) / frame_height))
                 self.canvas.yview_moveto(scroll_fraction)
         except Exception: pass


    # --- Metodo calculate_from_file (Aggiornato per chiamare libreria) ---
    def calculate_from_file(self):
        fpath = self.filepath.get()
        if not fpath or fpath == "Nessun file selezionato.":
            messagebox.showwarning("File Mancante", "Selezionare prima un file CSV o XLSX/XLS.")
            return

        file_basename = os.path.basename(fpath)
        try:
            df = None
            if fpath.lower().endswith('.csv'):
                try: df = pd.read_csv(fpath, header=None, dtype=object, sep=',', low_memory=False); assert df.shape[1] >= 36
                except Exception: df = None
                if df is None:
                     try: df = pd.read_csv(fpath, header=None, dtype=object, sep=';', low_memory=False); assert df.shape[1] >= 36
                     except Exception: df = None
                if df is None:
                    try: df = pd.read_csv(fpath, header=None, dtype=object, sep=None, engine='python', on_bad_lines='warn'); assert df.shape[1] >= 36
                    except Exception as e: raise ValueError(f"Impossibile leggere CSV: {e}")
            elif fpath.lower().endswith(('.xlsx', '.xls')):
                try:
                    engine = 'openpyxl' if fpath.lower().endswith('.xlsx') else None
                    df = pd.read_excel(fpath, header=None, dtype=object, engine=engine)
                except ImportError: messagebox.showerror("Libreria Mancante", "'openpyxl' necessaria per .xlsx. Installala con: pip install openpyxl"); return
                except Exception as e: raise ValueError(f"Errore lettura Excel: {e}")
            else:
                messagebox.showerror("Formato Non Supportato", "Selezionare file .csv, .xls o .xlsx"); return

            if df is None or df.empty: raise ValueError("File vuoto o illeggibile.")
            if df.shape[0] < 1: raise ValueError("Il file non contiene righe di dati.")
            if df.shape[1] < 36: raise ValueError(f"La prima riga contiene {df.shape[1]} colonne (richieste >= 36).")

            # Estrai dati (prima riga) come stringhe o None
            answers_raw = [str(df.iloc[0, i]).strip() if not pd.isna(df.iloc[0, i]) else None for i in range(36)]
            age_str = str(df.iloc[0, 36]).strip() if df.shape[1] > 36 and not pd.isna(df.iloc[0, 36]) else None
            sex_str = str(df.iloc[0, 37]).strip() if df.shape[1] > 37 and not pd.isna(df.iloc[0, 37]) else None

            # Chiama la libreria per calcolo e validazione interna
            results = sf36_library.calculate_sf36_all_scores(answers_raw, age=age_str, sex=sex_str)

            # Aggiorna GUI con risultati e warnings
            self.display_results(results, f"File: {file_basename} (Riga 1)")

            # Aggiorna campi Age/Sex nella GUI in base a cosa è stato effettivamente usato/validato dalla libreria
            used_input = results.get('input_data', {})
            age_used = used_input.get('age_provided') # Usa valore fornito per coerenza display
            sex_used = used_input.get('sex_provided')
            age_had_warning = any("Age" in w for w in used_input.get('warnings',[]))
            sex_had_warning = any("Sex" in w for w in used_input.get('warnings',[]))

            self.demographic_vars['age'].set(str(age_used) if age_used is not None and not age_had_warning else "")
            if sex_used is not None and not sex_had_warning:
                 sex_display_val = f"Maschio (1)" if str(sex_used) == '1' else f"Femmina (2)" if str(sex_used) == '2' else ""
                 self.demographic_vars['sex'].set(sex_display_val)
            else:
                 self.demographic_vars['sex'].set("")

            age_entry_widget = self.master.nametowidget('.!frame.!labelframe2.!entry')
            age_entry_widget.configure(style="Error.TEntry" if age_had_warning else "Valid.TEntry")


        except FileNotFoundError: messagebox.showerror("Errore", f"File non trovato: {fpath}"); self.filepath.set("Nessun file selezionato."); self.display_results(None, "File Non Trovato")
        except ValueError as ve: messagebox.showerror("Errore File", f"Errore lettura/formato file '{file_basename}':\n{ve}"); self.display_results(None, f"File: {file_basename} (Errore)")
        except Exception as e:
            messagebox.showerror("Errore Inaspettato", f"Errore elaborazione file '{file_basename}':\n{type(e).__name__}: {e}")
            import traceback; traceback.print_exc(); self.display_results(None, f"File: {file_basename} (Errore)")


# -----------------------------------------------------------------------------
# CLASSE HELPER PER TOOLTIP (Invariata)
# -----------------------------------------------------------------------------
class Tooltip:
    def __init__(self, widget, text='widget info'):
        self.widget = widget; self.text = text
        self.widget.bind("<Enter>", self.enter); self.widget.bind("<Leave>", self.close); self.widget.bind("<ButtonPress>", self.close)
        self.id = None; self.tw = None
    def enter(self, event=None): self.schedule()
    def close(self, event=None): self.unschedule(); self.hidetip()
    def schedule(self): self.unschedule(); self.id = self.widget.after(700, self.showtip)
    def unschedule(self): id = self.id; self.id = None; self.widget.after_cancel(id) if id else None
    def showtip(self, event=None):
        if not self.widget.winfo_exists(): return
        x, y, cx, cy = self.widget.bbox("insert"); x += self.widget.winfo_rootx() + 25; y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget); self.tw.wm_overrideredirect(True); self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tw, text=self.text, justify='left', background="#ffffe0", relief='solid', borderwidth=1, wraplength=450, font=("Segoe UI", 8, "normal"))
        label.pack(ipadx=2, ipady=2)
    def hidetip(self): tw = self.tw; self.tw = None; tw.destroy() if tw and tk.Toplevel.winfo_exists(tw) else None


# -----------------------------------------------------------------------------
# AVVIO APPLICAZIONE
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SF36_GUI_V6(root)
    root.mainloop()