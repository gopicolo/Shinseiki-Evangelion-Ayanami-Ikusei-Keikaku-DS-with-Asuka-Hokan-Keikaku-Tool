import os
import sys
import struct
import json
import shutil

# --- Configurações ---
INPUT_FOLDER_NAME = "output"
JSON_OUTPUT_FOLDER_NAME = "output_json"
TEXT_ENCODING = 'shift_jis'
MINIMUM_TEXT_LENGTH = 1  # Mantido, mas não usado diretamente
IGNORAR_ARQUIVOS = {"medium"}

# Marcador que precede um bloco de diálogo.
DIALOGUE_MARKER = b'\x0a\x00'

def texto_legivel(texto_decodificado):
    """Verifica se uma string decodificada parece ser texto real."""
    if not texto_decodificado or not texto_decodificado.strip():
        return False
    try:
        texto_decodificado.encode(TEXT_ENCODING)
        return True
    except UnicodeEncodeError:
        return False

def process_file(input_path, json_output_path):
    base_filename = os.path.basename(input_path)
    print(f"\n--- Processando arquivo: {input_path} ---")

    if os.path.splitext(base_filename)[0] in IGNORAR_ARQUIVOS:
        print("  [INFO] Arquivo ignorado pela configuração.")
        return

    try:
        with open(input_path, 'rb') as f_in:
            data = f_in.read()

        found_blocks = []
        block_index = 0
        current_pos = 0

        while current_pos < len(data):
            marker_pos = data.find(DIALOGUE_MARKER, current_pos)
            if marker_pos == -1:
                break

            size_field_pos = marker_pos + len(DIALOGUE_MARKER)
            block_start_pos = size_field_pos + 2

            if block_start_pos > len(data):
                current_pos = marker_pos + 1
                continue

            # Lê o tamanho do bloco (2 bytes, little-endian)
            block_size = struct.unpack('<H', data[size_field_pos:block_start_pos])[0]

            if block_size > 0 and (block_start_pos + block_size) <= len(data):
                block_data = data[block_start_pos : block_start_pos + block_size]
                null_terminator_pos = block_data.find(b'\x00')

                if null_terminator_pos != -1:
                    text_bytes = block_data[:null_terminator_pos]

                    # FILTRO: ignora blocos com bytes de controle (<0x20) exceto tab (0x09) e newline (0x0A)
                    if any(b < 0x20 and b not in (0x09, 0x0A) for b in text_bytes):
                        current_pos = marker_pos + 1
                        continue

                    try:
                        text = text_bytes.decode(TEXT_ENCODING)

                        # Ignora textos com só 1 caractere
                        if len(text) > 1 and texto_legivel(text):
                            block_info = {
                                "id": f"BLOCK_{block_index:03d}",
                                "size_address": size_field_pos,
                                "original_block_size": data[size_field_pos],  # valor literal do byte de tamanho
                                "original_text": text,
                            }
                            found_blocks.append(block_info)
                            block_index += 1
                    except UnicodeDecodeError:
                        pass

            current_pos = marker_pos + 1

        if not found_blocks:
            print("  Nenhum bloco de texto válido foi extraído.")
            return

        with open(json_output_path, 'w', encoding='utf-8') as f_out_json:
            json.dump(found_blocks, f_out_json, indent=4, ensure_ascii=False)

        print(f"  -> SUCESSO! {len(found_blocks)} bloco(s) salvo(s) em: {os.path.basename(json_output_path)}")

    except Exception as e:
        print(f"[ERRO] Falha crítica ao processar {input_path}: {e}")
        import traceback
        traceback.print_exc()

def main():
    if not os.path.isdir(INPUT_FOLDER_NAME):
        print(f"\n[ERRO] A pasta de entrada '{INPUT_FOLDER_NAME}' não foi encontrada.")
        sys.exit(1)

    if os.path.exists(JSON_OUTPUT_FOLDER_NAME):
        shutil.rmtree(JSON_OUTPUT_FOLDER_NAME)
    os.makedirs(JSON_OUTPUT_FOLDER_NAME)

    print("\nIniciando extração de textos para JSON...")
    print(f"Pasta de Entrada: '{INPUT_FOLDER_NAME}'")
    print(f"Pasta de Saída JSON: '{JSON_OUTPUT_FOLDER_NAME}'")

    for root, dirs, files in os.walk(INPUT_FOLDER_NAME):
        dirs.sort()
        files.sort()

        for filename in files:
            input_file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(input_file_path, INPUT_FOLDER_NAME)
            json_output_path = os.path.join(JSON_OUTPUT_FOLDER_NAME, f"{relative_path}.json")

            os.makedirs(os.path.dirname(json_output_path), exist_ok=True)

            process_file(input_file_path, json_output_path)

    print("\n✅ Extração concluída com sucesso!")

if __name__ == '__main__':
    main()
