from mip import Model, xsum, BINARY, minimize, CONTINUOUS, OptimizationStatus
from itertools import product
from istanze import leggi_istanza


def modello(n_real , m , g , tempi_processamento):
    n = n_real+1
    jobs = range(n)
    real_jobs = range(1, n)
    macchine = range(m)
    fabbriche = range(g)
    P_raw = tempi_processamento
    # P[0] è per il dummy job (tempo 0)
    P = [[0] * m] + P_raw

    # Big M: deve essere sufficientemente grande
    M = sum(sum(row) for row in P_raw) + 100


    model = Model(name="DPFSP_Model1")

    # --- VARIABILI ---
    x = [[[model.add_var(var_type=BINARY, name=f'x({k},{j},{f})')
           for f in fabbriche] for j in jobs] for k in jobs]

    y = [[model.add_var(var_type=BINARY, name=f'y({j},{f})')
          for f in fabbriche] for j in jobs]

    c = [[model.add_var(var_type=CONTINUOUS, name=f'C({j},{i})')
          for i in macchine] for j in jobs]

    Cmax = model.add_var(var_type=CONTINUOUS, name='Cmax')
    model.objective = minimize(Cmax)


    # --- VINCOLI

    # (5) Ogni job j deve avere esattamente un predecessore k
    for j in real_jobs:
        model += xsum(x[k][j][f] for k in jobs for f in fabbriche if k != j) == 1

    # (6) Ogni job j deve essere assegnato a esattamente una fabbrica
    for j in real_jobs:
        model += xsum(y[j][f] for f in fabbriche) == 1

    # (7) se il job j è in una fabbrica può avere al massimo un predecessore e un successore
    # se non è nella fabbrica non deve avere relazioni
    for j, f in product(real_jobs, fabbriche):
        model += xsum(x[k][j][f] for k in jobs if k != j) == y[j][f]
        model += xsum(x[j][k][f] for k in real_jobs if k != j) <= y[j][f]

    # (8) Ogni job k ha al massimo un successore
    for k in real_jobs:
        model += xsum(x[k][j][f] for j in real_jobs for f in fabbriche if j != k) <= 1

    # (9) Il dummy job 0 ha esattamente un successore in ogni fabbrica
    for f in fabbriche:
        model += xsum(x[0][j][f] for j in real_jobs) == 1

    # (11) un job deve finire prima sulla macchina i-1 prima di iniziare in i
    for j, i in product(real_jobs, range(1, m)):
        model += c[j][i] >= c[j][i-1] + P[j][i]

    # (12) Vincolo di precedenza: se j segue k, j finisce dopo k
    for k, j, i, f in product(jobs, real_jobs, macchine, fabbriche):
        if k != j:
            model += c[j][i] >= c[k][i] + P[j][i] - M * (1 - x[k][j][f])

    # (13) Definizione del Makespan
    for j in real_jobs:
        model += Cmax >= c[j][m-1]

    # 14) tempi positivi
    for (j , i ) in product(real_jobs, macchine):
        model += c[j][i] >=0

    # Condizioni iniziali per tempi e dummy job
    for j in real_jobs:
        model += c[j][0] >= P[j][0] # Il primo job in fabbrica inizia al tempo 0 + suo P
    for i in macchine:
        model += c[0][i] == 0 # Il dummy job finisce istantaneamente a 0

    # --- SOLUZIONE ---
    model.verbose = 0
    status = model.optimize(max_seconds=300)

    print("==============================================================")
    print(f"STATO OTTIMIZZAZIONE: {status}")
    print("==============================================================")

    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print(f"MAKESPAN TOTALE (Cmax): {model.objective_value}\n")

        for f in fabbriche:
            print(f"--- FABBRICA {f} ---")
            # Ricostruiamo la sequenza dei job nella fabbrica f
            sequenza = []
            curr = 0
            while True:
                prossimo = [j for j in real_jobs if x[curr][j][f].x > 0.5]
                if not prossimo:
                    break
                curr = prossimo[0]
                sequenza.append(curr)

            if not sequenza:
                print("Nessun job assegnato.")
                continue

            # Intestazione tabella
            header = f"{'Job':<8}"
            for i in macchine:
                header += f"| {'Macchina ' + str(i):<20} "
            print(header)
            print("-" * len(header))

            for j in sequenza:
                riga = f"Job {j:<4}"
                for i in macchine:
                    finito = c[j][i].x
                    durata = P_raw[j-1][i]

                    riga += f"| [{finito:>4.1f}] (dur: {durata:>2}) "
                print(riga)
            print("\n")

    else:
        print("Nessuna soluzione trovata.")

if __name__ == "__main__":
    nome_file = "istanze/istanze.csv"
    dati = leggi_istanza(nome_file)
    max = 2
    i = 0
    for istanza in dati:
        print(f"==============================================================")
        print(f"ISTANZA {i+1}")
        modello(istanza[0], istanza[1], istanza[2] , istanza[3])
        i +=1
        print(f"==============================================================")
        if i >=max:
            break

