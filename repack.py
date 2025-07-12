import os
import sys
import struct
import json
import shutil

# --- Configurações ---
ORIGINAL_SCRIPT_FOLDER = "output"
TRANSLATION_FILES_FOLDER = "output_json"
REPACK_OUTPUT_FOLDER = "repack_files"

TEXT_ENCODING = 'shift_jis'
DIALOGUE_MARKER = b'\x0a\x00'

def repack_file(original_script_path, translation_json_path, output_script_path):
    base_filename = os.path.basename(original_script_path)
    print(f"\n--- Repack do arquivo: {base_filename} ---")

    try:
        with open(original_script_path, 'rb') as f:
            original_data = f.read()
    except FileNotFoundError:
        print(f"  [ERRO] Arquivo de script original não encontrado: {original_script_path}")
        return

    try:
        with open(translation_json_path, 'r', encoding='utf-8') as f:
            translation_data = json.load(f)
    except FileNotFoundError:
        print(f"  [AVISO] Arquivo de tradução não encontrado para {base_filename}. Copiando original.")
        shutil.copy(original_script_path, output_script_path)
        return
    except json.JSONDecodeError:
        print(f"  [ERRO] Arquivo JSON mal formatado: {translation_json_path}")
        return

    new_data = bytearray()
    last_pos = 0

    for block_info in translation_data:
        # Usa texto traduzido se existir, senão original
        text_to_insert = block_info.get("translated_text", "").strip()
        if not text_to_insert:
            text_to_insert = block_info["original_text"]

        metadata = block_info.get("metadata", block_info)  # para compatibilidade

        size_address = metadata["size_address"]
        marker_address = size_address - len(DIALOGUE_MARKER)

        # Copia do último cursor até o início do bloco (antes do marcador)
        new_data.extend(original_data[last_pos:marker_address])

        # Codifica o novo texto
        try:
            new_text_bytes = text_to_insert.encode(TEXT_ENCODING)
        except UnicodeEncodeError:
            print(f"  [ERRO DE CODIFICAÇÃO] Bloco '{block_info['id']}' tem caracteres inválidos.")
            print(f"  Texto: {text_to_insert}")
            return

        # Novo tamanho = texto + byte nulo final
        new_block_size = len(new_text_bytes) + 1

        # Atualiza o byte do tamanho no arquivo (2 bytes, little endian)
        new_size_bytes = struct.pack('<H', new_block_size)

        # Monta o novo bloco: marcador + tamanho + texto + 0x00 final
        new_block_data = DIALOGUE_MARKER + new_size_bytes + new_text_bytes + b'\x00'
        new_data.extend(new_block_data)

        # Avança o cursor pulando o bloco original no arquivo
        # original_block_size aqui é o tamanho do bloco, que já inclui o byte nulo final
        original_block_size = metadata['original_block_size']

        # O texto original começa 2 bytes após size_address
        text_start_pos = size_address + 2

        last_pos = text_start_pos + original_block_size

    # Copia o resto do arquivo original depois do último bloco
    new_data.extend(original_data[last_pos:])

    # Salva o arquivo recompilado
    with open(output_script_path, 'wb') as f_out:
        f_out.write(new_data)

    print(f"  -> SUCESSO! Arquivo reconstruído salvo em: {output_script_path}")

def main():
    if not all(os.path.isdir(p) for p in [ORIGINAL_SCRIPT_FOLDER, TRANSLATION_FILES_FOLDER]):
        print("[ERRO] As pastas 'output' e/ou 'translation_files' não foram encontradas.")
        sys.exit(1)

    if os.path.exists(REPACK_OUTPUT_FOLDER):
        shutil.rmtree(REPACK_OUTPUT_FOLDER)
    os.makedirs(REPACK_OUTPUT_FOLDER)

    print(f"\nIniciando processo de reinserção (repack)...")
    print(f"Pasta Original: '{ORIGINAL_SCRIPT_FOLDER}'")
    print(f"Pasta Tradução: '{TRANSLATION_FILES_FOLDER}'")
    print(f"Pasta Saída:    '{REPACK_OUTPUT_FOLDER}'")

    for root, _, files in os.walk(TRANSLATION_FILES_FOLDER):
        files.sort()
        for filename in files:
            if not filename.endswith('.json'):
                continue

            relative_path = os.path.relpath(root, TRANSLATION_FILES_FOLDER)
            base_script_name = filename.replace('.json', '')

            translation_json_path = os.path.join(root, filename)
            original_script_path = os.path.join(ORIGINAL_SCRIPT_FOLDER, relative_path, base_script_name)
            output_script_path = os.path.join(REPACK_OUTPUT_FOLDER, relative_path, base_script_name)

            os.makedirs(os.path.dirname(output_script_path), exist_ok=True)

            repack_file(original_script_path, translation_json_path, output_script_path)

    print("\n✅ Processo de reinserção concluído!")

if __name__ == '__main__':
    main()
