from mip import Model, xsum, BINARY, minimize , CONTINUOUS
from itertools import product

#PARAMETRI
n = 6 # numero di job (5 job + 1 dummy job)
jobs = range(n)
real_n = range(1 , n)
m = 2 # numero di macchine
g = 2 # numero di fabbriche
P = [[10 , 5], [6 , 7], [8 , 4] , [9 , 6], [3 , 11]] # tempi di processamento di esempio


def calcola_vincolo_big_M(P):
    M = 0
    for(j , i) in product(range(len(P)) , range(len(P[0]))):
        M += P[j][i]
    return M

M = calcola_vincolo_big_M(P)

model = Model()


# DEFINIZIONE VARIABILI
x = [[[model.add_var(var_type=BINARY ,
                     name= 'x( {} , {} , {})' .format(k, j, f))
       for f in range(g)] for j in range(n)] for k in range(n)]

y = [[model.add_var(var_type=BINARY,
                    name='y({} , {})' .format(j , f))
      for f in range(g)] for j in jobs]
c = [[model.add_var(var_type=CONTINUOUS,
                    name='C({} , {})' .format(j , i))
      for i in range(m)] for j in range(n)]

# MAKESPAN
Cmax = model.add_var(var_type=CONTINUOUS , name='Cmax')

# FUNZIONE OBIETTIVO
model.objective = minimize(Cmax)

# VINCOLI

# 5) ogni job deve avere esattamente un predecessore
for (j) in real_n:
    model += xsum(x[k][j][f] for(k , f) in product(jobs , range(g)) if k!=j) == 1

# 6) ogni job va in una sola fabbrica
for j in real_n:
    model += xsum(y[j][f] for f in range(g)) == 1

# 7) se il job j è in fabbrica f può avere al massimo un predecessore e un successore;
# se non è in quella fabbrica non deve avere relazionin li
for( j, f) in product(real_n , range(g)):
        model += xsum(x[k][j][f] + x[j][k][f] for k in jobs if k !=j) <= 2*y[j][f]

# 8) ogni job k può avere al massimo un successore
for(k) in real_n:
        model += xsum(x[k][j][f] for(j , f) in product(real_n , range(g))if j != k) <= 1

# 9) il dummy job 0 ha un solo successore per fabbrica
for(f) in range(g):
    model += xsum(x[0][j][f] for j in real_n) == 1

# 10) tra due job k e j, o k prima di j oppure j prima di k oppure nessuno dei due
for(f , k , j) in product(range(g) , jobs , jobs):
    if j > k:
        model += xsum([x[k][j][f] + x[j][k][f]]) <=1

# 11) un job deve finire la macchina i-1 prima di iniziare i
for(j , i) in product(real_n , range(1 , m)):
    model += c[j][i] >= c[j][i-1] + P[j-1][i] # indici di p shiftati perchè parte da job 1

# 12) una macchina lavora un solo job alla volta
for(k , j , i) in product(real_n , real_n , range(m)):
    if j !=k:
        model += c[j][i] >= c[k][i] + P[j-1][i] + (xsum(x[k][j][f] for f in range(g))-1)*M

# 13) il makespan è il massimo completamento
for(j) in real_n:
    model += Cmax>= c[j][m-1]

# 16) tempi positivi
for(j , i) in product(jobs , range(m)):
    model += c[j][i] >= 0

model.optimize()

#STAMPA DEI RISULTATI
print("==============================")
print("STAMPE")
print("==============================")
# stampa dello stato della soluzione
print(f"Status: {model.status}")

print("ASSEGNAZIONE FABBRICHE")
for (j , f) in product(real_n , range(g)):
    if y[j][f].x > 0.5:
        print(f"job {j} assegnato alla fabbrica {f}")

print("\nSCHEDULING:")
for j in real_n:
    print(f"Job {j}: ", end="")
    for i in range(m):
        print(f"Macchina {i} -> {c[j][i].x}", end=" | ")
    print()


