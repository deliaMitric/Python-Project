import matplotlib.pyplot as plot
import os
import sys
def build_partition_path(partition):
    #Windows
    if sys.platform == "win64" or sys.platform == "win32":
        partition_path = partition + ":\\"
    print(partition_path)
    return partition_path


def analize(partition):
    number_of_files = 0
    number_of_dirs = 0
    extensions = {}

    try:
        partition_path = build_partition_path(partition)

        if not os.path.exists(partition_path):
            raise Exception("Partitia data nu exista")

        if os.access(partition_path, os.R_OK):
            try:
                for current_dir, sub_dirs, files in os.walk(partition_path):

                    #crestem numarul de directoare si de fisiere
                    number_of_dirs += 1;
                    number_of_files += len(files)

                    #Parcurgem files si daca gasim o noua extensie o adaugam ca si cheie la dictionatul extensions
                    #iar size ul fisierului ca valoare la aceasta cheie; daca extensia se gaseste in dictionar ca si cheie,
                    #vom adauga doar size-ul fisierului la lista de valori
                    for file in files:
                        file_path = os.path.join(current_dir, file)
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file)

                        if file_ext not in extensions:
                            extensions[file_ext] = [file_size]
                        else:
                            extensions[file_ext].append(file_size)

            except PermissionError as p:
                print(f"Directorul {current_dir} nu este accesibil.\nDoriti sa continuam prin excluderea acestuia? y/n\n")
                response = input()
                if response == "y" or response == "Y":
                    pass
                else:
                    raise SystemExit

    #Cazul in care partitia nu e accesibila
    except PermissionError as p:
        print("Partitia data nu e accesibila!")
        raise SystemExit

    # Cazul in care partitia data nu se gaseste sau cazuri neasteptate
    except Exception as e:
        if len(e.args) > 0:
            print(e.args[0])
        else:
            print("Eroare!")
        raise SystemExit
    finally:
        print(f"numar dir: {number_of_dirs}")
        print(f"numar files: {number_of_files}")



if __name__ == '__main__':
        if len(sys.argv) < 2:
            print("Prea putine argumente la linia de comanda!")
        elif len(sys.argv) == 2:
            partition = sys.argv[1]
            analize(partition)
        else:
            print("Prea multe argumente la linia de comanda!")