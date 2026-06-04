import csv
import json


def genera_file_risultati(nome_file, risultati):

    with open(nome_file, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "num_job",
            "num_macchine",
            "num_fabbriche",
            "tempi_processamento",
            "Cmax",
            "tempo_esecuzione",
            "status"
        ])

        for j, m, g, p, cmax, t_e, s in risultati:
            writer.writerow([
                j,
                m,
                g,
                json.dumps(p),
                cmax,
                t_e,
                s
            ])



