def marcar_pares(n):
    for i in range (n + 1):
        if i % 2 == 0:
            print(f"{i}: par")
        else: 
            print(i)
    return "fin"

while(True):
    a = int(input("Dime un número entero positivo: "))
    if a < 1:
        print ("el numero no es positivo")
    else:
        break
print(marcar_pares(a))