import os
import random
import csv
import json




def scrivi_istanze(nome_file , risultati):
    with open(nome_file, "w", newline="") as f:
        writer = csv.writer(f)

        # opzionale: intestazione
        writer.writerow(["num_job", "num_macchine", "num_fabbriche", "tempi_processamento"])

        for j , m , f , p in dati:
            writer.writerow([
                j,
                m,
                f,
                json.dumps(p)
            ])
def leggi_istanza(nome_file):

    dati = []
    with open(nome_file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            j = int(row["num_job"])
            m = int(row["num_macchine"])
            f = int(row["num_fabbriche"])
            p = json.loads(row["tempi_processamento"])

            dati.append((j , m , f , p))

    print(dati)
    return dati

if __name__ == "__main__":
    jobs = [20, 30, 50]
    macchine = [2 , 3 , 5]
    fabbriche = [2 , 3 , 5]

    # numero di istanze per comfigurazione
    num_istanze = 3

    # range tempi di processamento
    min_tempi = 1
    max_tempi = 100

    # Cartella output
    cartella = "istanze"

    os.makedirs(cartella, exist_ok=True)

    random.seed(42)

    dati = []

    for n in jobs:
        for m in macchine:
            for g in fabbriche:
                for idx in range(num_istanze):

                    P_raw = [
                        [random.randint(min_tempi, max_tempi)
                         for _ in range(m)]
                        for _ in range(n)
                    ]

                    dati.append(
                        (n, m, g, P_raw)
                    )

    scrivi_istanze(f"{cartella}/istanze.csv", dati)

