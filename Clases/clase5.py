# peso = 50
# altura  = 1.70

# imc = peso / (altura **2)

# print(imc)

# if imc < 18 :
#     print('Tiene bajo peso')
# elif imc < 25:
#     print('Tiene peso normal')
# elif imc < 30 :
#     print('Tiene sobrepeso')
# else:
#     print('Tiene obesidad')


# nombre = 'TALENTO TECH TEENS' 
# i= 1

# while (i < 6) :
#     print(i)
#     i += 1 
#     i = i + 1
    # CODIGO A REALZIAR

    

# nombre = 'TALENTO TECH TEENs' 
# conteo = {}


# for i in  nombre:
#     if i in conteo:
#         conteo[i] += 1
#     else:
#         conteo[i] = 1

# def marcar_pares_impares (numero):
#     suma_pares = 0
#     suma_impares = 0
#     for i in range(1, numero + 1):
#         if i % 2 == 0:
#             suma_pares += i 
#         else:
#             suma_impares += i
#     return suma_impares, suma_pares


# while True:
#     numero_usuario = input("Ingresá un número entero positivo: ")
#     if numero_usuario.isdigit():
#         numero_usuario = int(numero_usuario)
#         break 
#     else:
#         print("Eso no es un número válido. Intentá de nuevo.")

# result_impares , result_pares = marcar_pares_impares(numero_usuario)
# print(f'La suma de los pares es : {result_pares}')
# print(f'La suma de los impares es : {result_impares}')



# def marcar_pares(n):
#     for i in range(n + 1):
#         if i % 2 == 0:
#             print(f"pares: {i}")
#         else:
#             print(i)
            


# while True:
#     n = input('Ingrese valor positivo entero')
#     if n.isdigit():
#         n = int(n)
#         marcar_pares(n)
#         break
#     else:
#         print('IOngresa un valor entero positivo')


# from random import randint, choice


# numero  = randint(1,5)
# print(f'el numero elejigo es: {numero}')


# frutas = ["Limon", "Frutilla"]
# fruta = choice(frutas)
# print(f'la Fruta elejida es: {fruta}')




    
def marcar_pares(n):
        for i in range (n + 1):
            if i % 2 == 0:
                print(f"{i}: par")
            else: 
                print(i)
        return "fin"


while True: 
    try:
        a = int(input("Dime un número entero positivo: "))
        if a < 1:
            print ("el numero no es positivo")
        else:
            print(marcar_pares(a))
            break
    except ValueError:
        print("Por favor, introduce un número entero válido.")
