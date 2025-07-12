# Extrai uma fonte NFTR de um arm9.bin descomprimido

INPUT_FILE = "arm9.bin"
OUTPUT_FILE = "font.nftr"

OFFSET = 0x87E80
SIZE = 0x73C18

def main():
    with open(INPUT_FILE, "rb") as f:
        f.seek(OFFSET)
        data = f.read(SIZE)

    with open(OUTPUT_FILE, "wb") as f:
        f.write(data)

    print(f"Fonte extraída com sucesso para '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()
