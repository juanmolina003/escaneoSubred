# escaneoSubred
Script para el escaneo de hosts activos de una subred especifica utilizando una lista de registros dns.

EXPLICACION SCRIPT

IMPORTACION DE PAQUETES:
import subprocess
import ipaddress
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

subprocess: para ejecutar comandos del sistema (ping en este caso).
ipaddress: para manejar direcciones IP de forma segura y estructurada.
csv: para crear el informe CSV.
ThreadPoolExecutor: permite hacer múltiples tareas en paralelo (multithreading).

DEF PING
def ping(ip):
    try:
        result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except:
        return False

Hace un ping a la IP (1 intento, 1 segundo de espera).
Oculta la salida del comando.
Devuelve True si la IP responde, False si no.

DEF ESCANEAR_RED
def escanear_red(red, mapa_nombres, max_hilos=50):
    resultados = []
    with ThreadPoolExecutor(max_workers=max_hilos) as executor:
        futuros = {
            executor.submit(ping, str(ip)): str(ip)
            for ip in ipaddress.IPv4Network(red).hosts()
        }
        for futuro in as_completed(futuros):
            ip_str = futuros[futuro]
            try:
                if futuro.result():
                    nombre = mapa_nombres.get(ip_str, "No disponible")
                    resultados.append((ip_str, nombre))
            except:
                pass
    return resultados

Crea un pool de hilos (50 a la vez) que ejecutan ping() sobre cada IP del rango 192.168.232.1 a 192.168.232.254.
Al terminar cada ping, si la IP responde:
Busca su nombre en mapa_nombres.
Si no hay nombre, asigna "No disponible".
Añade (IP, Nombre) a la lista de resultados.
Esto permite escanear toda la red en paralelo, acelerando muchísimo el proceso.

DEF MAIN()
ruta_archivo = r"C:\Users\jmabellaneda\Downloads\nombres2.txt"
registros = []

Define la ruta del archivo de texto con los nombres y sus IPs.

with open(ruta_archivo, encoding="utf-8") as f:
    for linea in f:
        if "->" in linea:
            partes = linea.strip().split("->")
            if len(partes) == 2:
                nombre = partes[0].strip()
                ip = partes[1].strip()
                try:
                    ip_obj = ipaddress.IPv4Address(ip)
                    registros.append((ip_obj, nombre, ip))
                except ipaddress.AddressValueError:
                    continue

Lee el archivo línea por línea, esperando formato tipo:
PC-Juan -> 192.168.232.15
Se validan las IPs con IPv4Address(), lo que descarta líneas mal escritas.

Guarda una tupla: (ip_objeto, nombre, ip_str).

Creación de diccionario IP → nombre:
mapa_nombres = {ip: nombre for _, nombre, ip in registros}
Genera un diccionario para búsqueda rápida del nombre de host a partir de la IP (como string).

Escaneo de red:
resultados = escanear_red("192.168.232.0/24", mapa_nombres)
Ejecuta el escaneo con los hilos en paralelo (como vimos antes).

Devuelve una lista con solo las IPs activas y sus nombres.

Ordenación por IP real:
resultados.sort(key=lambda x: ipaddress.IPv4Address(x[0]))
Convierte las IPs a objetos IPv4Address para ordenarlas correctamente (y no como texto).

Escritura en CSV
archivo_csv = "informe_actividad_dns.csv"
with open(archivo_csv, mode="w", newline="") as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["IP", "Nombre"])
    writer.writerows(resultados)

Se sobrescribe el archivo anterior con el nuevo contenido.
Se escribe la cabecera y luego todas las filas con IP y nombre.
