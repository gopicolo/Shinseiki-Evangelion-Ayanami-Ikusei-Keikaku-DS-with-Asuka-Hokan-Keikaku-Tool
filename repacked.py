import os
import struct
import sys

SOURCE_DIR = "repack_files"       # Traduções (se existirem)
UNPACKED_DIR = "output"           # Originais
FINAL_SCD_DIR = "repacked_scd"    # Saída final .scd
TEXT_ENCODING = 'shift_jis'

def create_scd_archive(folder_name, output_scd_path):
    print(f"--- Criando SCD para: {folder_name} ---")

    # Caminhos
    repack_folder = os.path.join(SOURCE_DIR, folder_name)
    original_folder = os.path.join(UNPACKED_DIR, folder_name)
    order_txt = os.path.join(original_folder, "_file_order.txt")

    if not os.path.exists(order_txt):
        print(f"  [ERRO] _file_order.txt não encontrado em {original_folder}")
        return

    with open(order_txt, 'r', encoding='utf-8') as f:
        ordered_filenames = [line.strip() for line in f if line.strip()]

    files_to_pack = []

    for filename in ordered_filenames:
        if filename == "_file_order.txt":
            continue

        # Tenta pegar da pasta traduzida primeiro
        repacked_path = os.path.join(repack_folder, filename)
        original_path = os.path.join(original_folder, filename)

        if os.path.isfile(repacked_path):
            filepath = repacked_path
        elif os.path.isfile(original_path):
            filepath = original_path
        else:
            print(f"  [AVISO] Arquivo '{filename}' não encontrado em nenhuma pasta. Pulando.")
            continue

        files_to_pack.append({'name': filename, 'path': filepath})

    if not files_to_pack:
        print("  [AVISO] Nenhum arquivo válido encontrado. Pulando.")
        return

    file_count = len(files_to_pack)
    print(f"  → Empacotando {file_count} arquivos...")

    header_size = 16
    file_table_size = file_count * 16
    data_start_offset = header_size + file_table_size

    file_table_bytes = bytearray()
    data_blob_bytes = bytearray()
    current_relative_offset = 0

    for file_info in files_to_pack:
        filename = file_info['name']
        filepath = file_info['path']
        with open(filepath, 'rb') as f:
            file_data = f.read()

        try:
            name_bytes = filename.encode(TEXT_ENCODING)
        except UnicodeEncodeError:
            name_bytes = filename.encode('ascii', errors='ignore')

        if len(name_bytes) > 12:
            print(f"  [AVISO] Nome do arquivo '{filename}' >12 bytes. Será truncado.")
            name_bytes = name_bytes[:12]

        padded_name = name_bytes.ljust(12, b'\0')
        table_entry = struct.pack('<12sI', padded_name, current_relative_offset)
        file_table_bytes.extend(table_entry)
        data_blob_bytes.extend(file_data)
        current_relative_offset += len(file_data)

    magic = b'SCR\0'
    header = struct.pack('<4sIII', magic, file_count, data_start_offset, 0)
    final_scd_data = header + file_table_bytes + data_blob_bytes

    with open(output_scd_path, 'wb') as f_out:
        f_out.write(final_scd_data)

    print(f"  ✅ SCD '{os.path.basename(output_scd_path)}' criado com sucesso ({len(final_scd_data)} bytes).")

def main():
    print("--- INICIANDO CRIAÇÃO DOS ARQUIVOS .SCD ---")

    if not os.path.isdir(UNPACKED_DIR):
        print(f"[ERRO FATAL] Pasta original '{UNPACKED_DIR}' não encontrada.")
        sys.exit(1)

    os.makedirs(FINAL_SCD_DIR, exist_ok=True)
    print(f"Os arquivos .scd finais serão salvos em: '{FINAL_SCD_DIR}'\n")

    for folder_name in sorted(os.listdir(UNPACKED_DIR)):
        original_folder = os.path.join(UNPACKED_DIR, folder_name)
        if os.path.isdir(original_folder):
            output_scd_file = os.path.join(FINAL_SCD_DIR, f"{folder_name}.scd")
            create_scd_archive(folder_name, output_scd_file)

    print("\n✅ Todos os arquivos .SCD foram criados com sucesso!")

if __name__ == '__main__':
    main()
