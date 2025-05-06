import subprocess
import ipaddress
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed


def ping(ip):
    try:
        result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except:
        return False


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


def main():
    ruta_archivo = r"C:\Users\jmabellaneda\Downloads\nombres2.txt"
    registros = []

    # Leer y almacenar los registros con IP y nombre
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

    # Ordenar por IP

    # Crear un diccionario IP -> nombre
    mapa_nombres = {ip: nombre for _, nombre, ip in registros}

    # Escanear la red en paralelo
    resultados = escanear_red("192.168.232.0/24", mapa_nombres)

    resultados.sort(key=lambda x: ipaddress.IPv4Address(x[0]))    
    # Guardar en CSV sobrescribiendo
    archivo_csv = "informe_actividad_dns.csv"
    with open(archivo_csv, mode="w", newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["IP", "Nombre"])
        writer.writerows(resultados)

    print("\n[+] Informe actualizado: informe_actividad_dns.csv")


if __name__ == "__main__":
    main()
