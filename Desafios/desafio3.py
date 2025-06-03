dicc = {}

cantidad = int(input("Cant. de personas en el dicc: "))
nombre = str(input("Ingrese un nombre: "))
edad = int(input("Ingrese una edad: "))

for i in range(1,cantidad):
    nombre = str(input("Ingrese un nombre: "))
    edad = int(input("Ingrese una edad: "))
    dicc[nombre] = edad

for name, age in dicc.items():
    print(f"Nombre: {nombre}, Edad: {edad}")

clave = input("Ingrese el nombre que desea buscar: ")

if (clave in dicc):
    print(f"La edad de {clave} es {dicc[clave]}")
else:
    print(f"No se encontro el nombre {clave} en el diccionario.")