import matplotlib.pyplot as plot
import os
import sys
from tqdm import tqdm

def build_partition_path(partition):
    partition_path = ""
    separator = os.path.sep

    #Windows: primim o litera -> litera:\
    if sys.platform.startswith("win"):
        partition_path = os.path.join(partition + ":", separator)

    #Linux: primim un sir (ex: sda1) -> \dev\sda1
    elif sys.platform == "linux":
        partition_path = os.path.join(separator + "dev", partition)
    else:
        print("Platforma nu este suportata!")

    print(partition_path)
    return partition_path

def make_plots_number_size(extensions, number_files, percentage_number_limit, percentage_size_limit):
    try:
        # -----------------------------------DUPA NUMAR----------------------------------
        # Deoarece in extensions sunt extensii ce corespund la foarte putine fisiere
        # vom lua in considerare doar procentele > <limita>(percentage_number_limit) pentru a nu incarca diagrama
        new_extensions1 = [ext for ext in extensions if ((len(extensions[ext]) / number_files) * 100) > percentage_number_limit]
        percents_number = [((len(extensions[ext]) / number_files) * 100) for ext in new_extensions1]

        #Tipurile de fisiere pentru care procentul e <= <limita> vor fi clasificate la un loc, cu eticheta "others"
        small_percents1 = [((len(extensions[ext]) / number_files) * 100) for ext in extensions if ((len(extensions[ext]) / number_files) * 100) <= percentage_number_limit]
        small_percents_sum1 = sum(small_percents1)

        percents_number.append(small_percents_sum1)
        new_extensions1.append("others")

        figure1, ax1 = plot.subplots(figsize=(25, 8))

        #Realizarea bar chart ului
        ax1.bar(new_extensions1, percents_number, color='green')
        ax1.set_xticks(range(len(new_extensions1)))
        ax1.set_xticklabels(new_extensions1, rotation=45, ha='right')
        ax1.set_xlabel("Extensii:")
        ax1.set_ylabel("Procente:")
        ax1.set_title("Proporția fiecărui tip ca numar:")

        # -----------------------------------DUPA SIZE----------------------------------
        sizes = [sum(extensions[ext]) for ext in extensions]
        total_size = sum(sizes)

        new_extensions2 = [ext for ext in extensions if ((sum(extensions[ext]) / total_size) * 100) > percentage_size_limit]
        percents_size = [((sum(extensions[ext]) / total_size) * 100) for ext in new_extensions2]

        # Tipurile de fisiere pentru care procentul e <= <limita> vor fi clasificate la un loc cu eticheta "others"
        small_percents2 = [((sum(extensions[ext]) / total_size) * 100) for ext in extensions if ((sum(extensions[ext]) / total_size) * 100) <= percentage_size_limit]
        small_percents_sum2 = sum(small_percents2)

        percents_size.append(small_percents_sum2)
        new_extensions2.append("others")

        figure, ax2 = plot.subplots(figsize=(25, 8))

        # Realizarea pie chart ului
        ax2.pie(percents_size, labels=new_extensions2, autopct="%1.1f%%", startangle=0)
        ax2.axis("equal")
        ax2.set_title("Proporția fiecărui tip ca size:")

        plot.show()

    except ZeroDivisionError as e:
        print("Partitia nu contine fisiere.")
    except Exception as e:
        print(e);

#Parcurgerea recursiva a partitiei-----------------------------------------------------
def analyze_rec(partition, percentage_number_limit, percentage_size_limit):
    number_of_files = 0
    number_of_dirs = 0
    extensions = {}

    try:
        partition_path = build_partition_path(partition)

        if not os.path.exists(partition_path):
            raise Exception("Partitia data nu exista")

        if os.access(partition_path, os.R_OK):
            try:
                for current_dir, sub_dirs, files in tqdm(os.walk(partition_path), desc="Progress"):

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
                        if "," in file_ext and " " in file_ext:
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
                            if sys.platform.startswith("win"):
                                file_ext = file_ext.lower()

                            if file_ext not in extensions:
                                extensions[file_ext] = [file_size]
                            else:
                                extensions[file_ext].append(file_size)

            #Daca vreun director e inaccesibil, lasam utilizatorul sa aleaga daca, continuam sau nu
            except PermissionError as p:
                print(f"Directorul {current_dir} nu este accesibil.\nDoriti sa continuam prin excluderea acestuia? y/n")
                response = input()
                if response == "y" or response == "Y":
                    pass
                else:
                    raise SystemExit
            except Exception as e:
                print(
                    f"Am intampinat o eroare la deschiderea de director/fisier.\nDoriti sa continuam? y/n")
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
            print(f"Eroare: {e}")
        raise SystemExit
    else:
        print(f"Numar dir: {number_of_dirs}")
        print(f"Numar files: {number_of_files}")
        print(f"Numar extensii: {len(extensions)}")

        make_plots_number_size(extensions, number_of_files, percentage_number_limit, percentage_size_limit)


#Parcurgerea doar a primului nivel-----------------------------------------------------
def analyze_first_level(partition, percentage_number_limit, percentage_size_limit):
    number_of_files = 0
    number_of_dirs = 0
    extensions = {}

    try:
        partition_path = build_partition_path(partition)

        if not os.path.exists(partition_path):
            raise Exception("Partitia data nu exista")

        if os.access(partition_path, os.R_OK):
            try:
                for element in tqdm(os.listdir(partition_path), desc="Progress"):
                    #construim path-ul elementului
                    elem_path = os.path.join(partition_path, element)

                    #verificam daca emlement este file sau director
                    if os.path.isdir(elem_path):
                        number_of_dirs += 1


                    elif os.path.isfile(elem_path):
                        number_of_files += 1
                        file_size = os.path.getsize(elem_path)

                        #Extragem extensia fisierului
                        file_ext = os.path.splitext(element)[1]

                        #verificam daca fisierul nu e standard, adica contine o insiruire de valori precum version=.., culture-.. etc.
                        if "," in file_ext and " " in file_ext:
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
                            if sys.platform.startswith("win"):
                                file_ext = file_ext.lower()

                            if file_ext not in extensions:
                                extensions[file_ext] = [file_size]
                            else:
                                extensions[file_ext].append(file_size)

            #Daca vreun director e inaccesibil, lasam utilizatorul sa aleaga daca, continuam sau nu
            except PermissionError as p:
                print(f"Un fisier sau un director din partitia {partition} nu este accesibil.\nDoriti sa continuam prin excluderea acestuia? y/n")
                response = input()
                if response == "y" or response == "Y":
                    pass
                else:
                    raise SystemExit
            except Exception as e:
                print(
                    f"Am intampinat o eroare la deschiderea de director/fisier.\nDoriti sa continuam? y/n")
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
            print(f"Eroare: {e}")
        raise SystemExit
    else:
        print(f"Numar dir: {number_of_dirs}")
        print(f"Numar files: {number_of_files}")
        print(f"Numar extensii: {len(extensions)}")

        for ext in extensions:
            print(f"{ext}: {extensions[ext]}")

        make_plots_number_size(extensions, number_of_files, percentage_number_limit, percentage_size_limit)

if __name__ == '__main__':
        if len(sys.argv) != 2:
            print("Numarul incorect de argumente!\nVa rog introduceti comanda sub forma: python.exe <nume_fisier.py> <nume_partitie>\n")

        else:
            partition = sys.argv[1]

            print("Cum doriti sa parcurgem partitia?\nRECURSIV (tastati:  R)\nPRIMUL NIVEL (tastati:  N)")
            while True:
                response = input()
                if response.lower() == "r":
                    analyze_rec(partition, 0.35, 1)
                    break
                elif response.lower() == "n":
                    analyze_first_level(partition, 0.1, 0.1)
                    break
                else:
                    print("Va rog introduceti  R  pentru parcurgere RECURSIV sau  N  pentru parcurgerea PRIMUL NIVEL")

