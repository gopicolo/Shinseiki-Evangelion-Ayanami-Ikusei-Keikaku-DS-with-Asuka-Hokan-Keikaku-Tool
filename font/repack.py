# Reinsere uma fonte NFTR no arm9.bin descomprimido

INPUT_FILE = "font.nftr"
TARGET_FILE = "arm9.bin"
OFFSET = 0x87E80
MAX_SIZE = 0x73C18  # Tamanho original da fonte no bin

def main():
    with open(INPUT_FILE, "rb") as f:
        new_data = f.read()

    if len(new_data) > MAX_SIZE:
        print(f"[ERRO] A nova fonte é maior ({len(new_data)} bytes) que o tamanho permitido ({MAX_SIZE} bytes).")
        return

    # Abrir o arm9.bin e sobrescrever os dados da fonte
    with open(TARGET_FILE, "r+b") as f:
        f.seek(OFFSET)
        f.write(new_data)

        # Preencher com 0x00 se a nova fonte for menor
        padding = MAX_SIZE - len(new_data)
        if padding > 0:
            f.write(b'\x00' * padding)

    print(f"Fonte reinserida com sucesso em '{TARGET_FILE}'.")

if __name__ == "__main__":
    main()
