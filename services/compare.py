"""
# Modo de uso:

## Informar argumentos após a execução
python services/compare.py

## Informar argumentos na linha de comando
python services/compare.py arquivo='./local_arquivos.tsv' delimitador='tab' coluna=0 arquivo='./sp_arquivos.tsv' delimitador=';' coluna=0
"""

import sys
from typing import Optional


class Compare:

    def __init__(
        self,
        arquivo_01: Optional[str] = None,
        delimitador_01: Optional[str] = None,
        coluna_01: Optional[int] = None,
        arquivo_02: Optional[str] = None,
        delimitador_02: Optional[str] = None,
        coluna_02: Optional[int] = None,
    ):
        # Arquivo 1
        self.arquivo_01: str = arquivo_01
        self.delimitador_01: str = delimitador_01
        self.coluna_01: int = coluna_01
        self.linhas_1: dict = {}
        # Arquivo 2
        self.arquivo_02: str = arquivo_02
        self.delimitador_02: str = delimitador_02
        self.coluna_02: int = coluna_02
        self.linhas_2: dict = {}
        # Verificador
        self.dados_carregados = all(
            valor is not None
            for valor in [
                arquivo_01,
                delimitador_01,
                coluna_01,
                arquivo_02,
                delimitador_02,
                coluna_02,
            ]
        )

    def abrir_arquivo(
        self,
        caminho_arquivo: str,
        delimitador: str,
        coluna: int,
    ) -> dict:
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            linhas = file.readlines()
            if delimitador.lower() == "tab":
                delimitador = "\t"

            linhas = [linha.strip().split(delimitador) for linha in linhas]
            res: dict = {}
            for linha in linhas:
                res[str(linha[coluna])] = linha
            return res

    def carregar_arquivos(self):
        # Arquivo 1
        print("=" * 40)
        print("        --- Primeiro Arquivo ---        ")
        print("=" * 40)
        self.arquivo_01 = input("Digite o caminho do primeiro arquivo: ")
        self.delimitador_01 = input("Digite o delimitador (ex: ',' ';' '|' ou 'tab'): ")
        self.coluna_01 = int(input("Digite o número da coluna (começando do 0): "))

        # Arquivo 2
        print("=" * 40)
        print("        --- Segundo Arquivo ---        ")
        print("=" * 40)
        self.arquivo_02 = input("Digite o caminho do segundo arquivo: ")
        self.delimitador_02 = input("Digite o delimitador (ex: ',' ';' '|' ou 'tab'): ")
        self.coluna_02 = int(input("Digite o número da coluna (começando do 0): "))

    def comparar_colunas(self):
        if not self.linhas_1 or not self.linhas_2:
            print("Um dos arquivos não foi carregado corretamente.")
            return

        valores_1 = set(self.linhas_1.keys())
        valores_2 = set(self.linhas_2.keys())

        apenas_no_arquivo_1 = valores_1 - valores_2
        apenas_no_arquivo_2 = valores_2 - valores_1

        resultado_arquivo_1 = []
        for chave in apenas_no_arquivo_1:
            resultado_arquivo_1.append(";".join(self.linhas_1[chave]))

        resultado_arquivo_2 = []
        for chave in apenas_no_arquivo_2:
            resultado_arquivo_2.append(";".join(self.linhas_2[chave]))

        self.salvar_resultado(
            "./somente_no_arquivo_1.txt",
            resultado_arquivo_1,
        )
        self.salvar_resultado(
            "./somente_no_arquivo_2.txt",
            resultado_arquivo_2,
        )

        print("=" * 40)
        print("        --- Arquivos salvos ---        ")
        print("=" * 40)

    def comparar(self):
        if not self.dados_carregados:
            self.carregar_arquivos()
        self.linhas_1 = self.abrir_arquivo(
            self.arquivo_01,
            self.delimitador_01,
            self.coluna_01,
        )
        self.linhas_2 = self.abrir_arquivo(
            self.arquivo_02,
            self.delimitador_02,
            self.coluna_02,
        )
        self.comparar_colunas()

    def salvar_resultado(self, caminho_saida: str, resultados: list):
        with open(caminho_saida, "w", encoding="utf-8") as file:
            for res in resultados:
                file.write(f"{res}\n")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        compare = Compare()
    else:
        compare = Compare(
            arquivo_01=sys.argv[1].replace("arquivo=", ""),
            delimitador_01=sys.argv[2].replace("delimitador=", ""),
            coluna_01=int(sys.argv[3].replace("coluna=", "")),
            arquivo_02=sys.argv[4].replace("arquivo=", ""),
            delimitador_02=sys.argv[5].replace("delimitador=", ""),
            coluna_02=int(sys.argv[6].replace("coluna=", "")),
        )

    compare.comparar()
