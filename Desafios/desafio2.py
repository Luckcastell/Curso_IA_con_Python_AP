int1 = int(input("Dime un número entero: "))
int2 = int(input("Dime otro número entero: "))
int3 = int(input("Dime un número entero más: "))

sumaInt = int1 + int2 + int3
print("La suma de los tres números es: ", sumaInt)


float1 = float(input("Dime un número con decimal: "))
float2 = float(input("Dime otro número con decimal: "))

restaFloat = float1 - float2
print("La resta de los dos números es: ", restaFloat)


int4 = int(input("Dime un número entero: "))
int5 = int(input("Dime otro número entero: "))

if(int4 > int5):
    print(f"{int4} es mayor que {int5}, y por ende {int5} es menor que {int4}")
elif(int5 > int4):
    print(f"{int5} es mayor que {int4}, y por ende {int4} es menor que {int5}")
else:
    print(f"{int4} y {int5} son iguales")
