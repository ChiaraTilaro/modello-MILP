import copy
import os
import time

from istanze import leggi_istanza
from risultati import genera_file_risultati


def makespan(sequenza, P):

    if len(sequenza) == 0:
        return 0

    m = len(P[0])

    fine = [[0] * m for _ in range(len(sequenza))]

    for i, job in enumerate(sequenza):

        for macchina in range(m):

            if i == 0 and macchina == 0:
                fine[i][macchina] = P[job][macchina]

            elif i == 0:
                fine[i][macchina] = (
                    fine[i][macchina - 1]
                    + P[job][macchina]
                )

            elif macchina == 0:
                fine[i][macchina] = (
                    fine[i - 1][macchina]
                    + P[job][macchina]
                )

            else:
                fine[i][macchina] = (
                    max(
                        fine[i - 1][macchina],
                        fine[i][macchina - 1]
                    )
                    + P[job][macchina]
                )

    return fine[-1][-1]

def best_insertion(sequenza, job, P):

    best_seq = None
    best_cmax = float("inf")


    for i in range(len(sequenza) + 1):

        nuova_seq = sequenza[:i] + [job] + sequenza[i:]

        cmax = makespan(nuova_seq, P)

        if cmax < best_cmax:
            best_cmax = cmax
            best_seq = nuova_seq

    return best_seq, best_cmax

def NEH2(n_real , m , g , tempi_processamento):
    #real_jobs = range(1, n)
    macchine = range(m)
    fabbriche = range(g)
    P_raw = tempi_processamento

    tempi_sulle_macchine = {}
    i = 0
    #  il tempo di processamento totale per ogni job su tutte le macchine è calcolato
    for row in P_raw:
        tempi_sulle_macchine[i] = sum(row)
        i += 1

    # i job sono ordinati in ordine decrescente del tempo prima calcolato
    dizionario_ordinato = dict(sorted(tempi_sulle_macchine.items(), key=lambda item: item[1] , reverse=True))



    # assegnazione
    fabbriche = {f: [] for f in range(g)}
    for job in dizionario_ordinato:

        best_global_seq = None
        best_global_f = None
        best_global_cmax = float("inf")

        # prova tutte le fabbriche
        for f in range(g):

            seq = fabbriche[f]

            nuova_seq, cmax = best_insertion(seq, job, P_raw)

            if cmax < best_global_cmax:
                best_global_cmax = cmax
                best_global_seq = nuova_seq
                best_global_f = f

        fabbriche[best_global_f] = best_global_seq

    print("Soluzione finale:")
    for f in fabbriche:
        print(f, fabbriche[f], "Cmax =", makespan(fabbriche[f], P_raw))

    print(fabbriche)
    return fabbriche , P_raw

def intra_factory_improvement(fabbriche, P):

    improved = True

    while improved:
        improved = False

        for f in fabbriche:

            seq = fabbriche[f][:]
            improved_seq = seq[:]

            for i in range(len(seq)):
                for j in range(len(seq)):

                    if i == j:
                        continue

                    new_seq = improved_seq[:]
                    job = new_seq.pop(i)
                    new_seq.insert(j, job)

                    if makespan(new_seq, P) < makespan(improved_seq, P):
                        improved_seq = new_seq

            if makespan(improved_seq, P) < makespan(seq, P):
                improved = True

            fabbriche[f] = improved_seq

    return fabbriche

def inter_factory_improvement(fabbriche, P):
    improved = True

    while improved:
        improved = False

        factories = list(fabbriche.keys())

        for f1 in factories:
            for f2 in factories:

                if f1 == f2:
                    continue

                for i in range(len(fabbriche[f1])):

                    job = fabbriche[f1][i]

                    new_f1 = fabbriche[f1][:]
                    new_f2 = fabbriche[f2][:]

                    new_f1.pop(i)
                    new_f2.append(job)

                    new_solution = copy.deepcopy(fabbriche)
                    new_solution[f1] = new_f1
                    new_solution[f2] = new_f2

                    current_cmax = max(
                        makespan(new_solution[f], P)
                        for f in new_solution
                    )

                    best_cmax = max(
                        makespan(fabbriche[f], P)
                        for f in fabbriche
                    )

                    if current_cmax < best_cmax:
                        fabbriche = new_solution
                        improved = True
                        break

    return fabbriche



def metaeuristica(fabbriche , P):

    start_time = time.time()
    time_limit = 300  # 5 minuti



    best_solution = copy.deepcopy(fabbriche)

    best_cmax = max(
        makespan(fabbriche[f], P)
        for f in fabbriche
    )

    while True:

        # TIMER CHECK
        if time.time() - start_time > time_limit:
            print("\n Tempo scaduto (5 minuti)")
            break

        fabbriche = intra_factory_improvement(fabbriche, P)
        fabbriche = inter_factory_improvement(fabbriche, P)

        current_cmax = max(
            makespan(fabbriche[f], P)
            for f in fabbriche
        )

        if current_cmax < best_cmax:
            best_cmax = current_cmax
            best_solution = copy.deepcopy(fabbriche)

        else:
            break

    # 🔥 STAMPA SEMPRE LA MIGLIORE SOLUZIONE
    print("\n Miglior soluzione trovata:")
    for f in best_solution:
        print(f, best_solution[f], "Cmax =", makespan(best_solution[f], P))

    end_time = time.time()
    execution_time = end_time - start_time

    return best_cmax, execution_time


if __name__ == "__main__":
    #n = 6 # numero di job (5 job + 1 dummy job)
    #jobs = range(n)
    #real_n = range(1 , n)
    #m = 2 # numero di macchine
    #g = 2 # numero di fabbriche
    #P = [[10 , 5], [6 , 7], [8 , 4] , [9 , 6], [3 , 11]] # tempi di processamento di esempio

    nome_file = "istanze/istanze.csv"
    dati = leggi_istanza(nome_file)

    risultati = []
    cartella = "risultatiAlgoritmo"
    os.makedirs(cartella, exist_ok=True)

    max_istanze = 2
    i = 0

    
    for istanza in dati:
        print(f"==============================================================")
        print(f"ISTANZA {i+1}")
        soluzione_iniziale , P = NEH2(istanza[0] , istanza[1] , istanza[2] , istanza[3])
        cmax , tempo_esec = metaeuristica(soluzione_iniziale , P)
        i +=1
        print(f"==============================================================")
        risultati.append((istanza[0] , istanza[1], istanza[2] , istanza[3] , cmax , tempo_esec , status))
        genera_file_risultati(f"{cartella}/risultatiAlgoritmo.csv",risultati)
        if i >= max_istanze:
            break
