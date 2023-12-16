import matplotlib.pyplot as plot
import os
import sys
import re
def build_partition_path(partition):
    #Windows
    if sys.platform == "win64" or sys.platform == "win32":
        partition_path = partition + ":\\"
    print(partition_path)
    return partition_path

def make_barplot_number(extensions, number_files):
    #Deoarece in extensions sunt extensii ce corespund la foarte putine fisiere
    #vom lua in considerare doar procentele >= 0.35 pentru a nu incarca diagrama
    new_extensions = [ext for ext in extensions if ((len(extensions[ext]) / number_files) * 100) >= 0.35]
    percents_number = [((len(extensions[ext]) / number_files) * 100) for ext in new_extensions]

    #Ajustam dimensiunea imaginii
    plot.figure(figsize=(25, 8))

    #Realizarea barplotului
    plot.bar(new_extensions, percents_number, color='green')
    plot.xticks(rotation=45, ha='right')
    plot.show()

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
                        #Construim path ul fisierului pentru a folosi functia getsize
                        file_path = os.path.join(current_dir, file)
                        file_size = os.path.getsize(file_path)

                        #Extragem extensia fisierului
                        file_ext = os.path.splitext(file)[1]

                        #verificam daca fisierul nu e standard, adica contine o insiruire de valori precum version=.., culture-.. etc.
                        if "," in file_ext and "." in file_ext:
                            if "non_standard" not in extensions:
                                extensions["non_standard"] = [file_size]
                            else:
                                extensions["non_standard"].append(file_size)
                        # verificam daca extensia e un numar
                        elif file_ext[1:].isdigit():
                            if "number" not in extensions:
                                extensions["number"] = [file_size]
                            else:
                                extensions["number"].append(file_size)

                        # verificam daca fisierul nu are extensie
                        elif file_ext == "":
                            if "no_ext" not in extensions:
                                extensions["no_ext"] = [file_size]
                            else:
                                extensions["no_ext"].append(file_size)

                        else:
                            if file_ext not in extensions:
                                extensions[file_ext] = [file_size]
                            else:
                                extensions[file_ext].append(file_size)

            #Daca vreun director e inaccesibil, lasam utilizatorul sa aleaga daca, continuam sau nu
            except PermissionError as p:
                print(f"Directorul {current_dir} nu este accesibil.\nDoriti sa continuam prin excluderea acestuia? y/n\n")
                response = input()
                if response == "y" or response == "Y":
                    pass
                else:
                    raise SystemExit
            except Exception as e:
                print(e)

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
    else:
        print(f"numar dir: {number_of_dirs}")
        print(f"numar files: {number_of_files}")
        print(f"numar extensii: {len(extensions)}")

        # print("Extensiile si size urile:")
        # for ext in extensions:
        #     print(f"{ext} : {len(extensions[ext])}")

        make_barplot_number(extensions, number_of_files)




if __name__ == '__main__':
        if len(sys.argv) < 2:
            print("Prea putine argumente la linia de comanda!")
        elif len(sys.argv) == 2:
            partition = sys.argv[1]
            analize(partition)
        else:
            print("Prea multe argumente la linia de comanda!")