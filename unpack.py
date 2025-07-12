import os
import struct

INPUT_DIR = 'input'
OUTPUT_DIR = 'output'

def unpack_scd(scd_path, output_base_dir):
    """
    Extrai arquivos de um container .scd.
    """
    print(f"--- Processando: {os.path.basename(scd_path)} ---")

    try:
        with open(scd_path, 'rb') as f:
            scd_data = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{scd_path}' não encontrado.")
        return

    magic = scd_data[0:4]
    if magic != b'SCR\0':
        print(f"Erro: Assinatura inválida no arquivo {os.path.basename(scd_path)}. Esperado 'SCR\\0'.")
        return

    file_count = struct.unpack('<I', scd_data[4:8])[0]
    data_start_offset = struct.unpack('<I', scd_data[8:12])[0]

    print(f"Arquivos encontrados: {file_count}")
    print(f"Início dos dados: 0x{data_start_offset:X}")

    scd_output_folder_name = os.path.basename(scd_path).replace('.scd', '')
    scd_output_dir = os.path.join(output_base_dir, scd_output_folder_name)
    os.makedirs(scd_output_dir, exist_ok=True)

    file_entries = []
    table_offset = 0x10
    for i in range(file_count):
        entry_offset = table_offset + (i * 16)
        entry_data = scd_data[entry_offset : entry_offset + 16]
        name_bytes, offset = struct.unpack('<12sI', entry_data)
        try:
            filename = name_bytes.split(b'\0')[0].decode('shift_jis')
        except UnicodeDecodeError:
            filename = name_bytes.split(b'\0')[0].decode('ascii', errors='ignore')
        file_entries.append({'name': filename, 'offset': offset})

    # Salva a ordem dos arquivos
    order_path = os.path.join(scd_output_dir, "_file_order.txt")
    with open(order_path, 'w', encoding='utf-8') as order_file:
        for entry in file_entries:
            order_file.write(entry['name'] + '\n')

    for i in range(file_count):
        current_entry = file_entries[i]
        start_pos = data_start_offset + current_entry['offset']
        if i < file_count - 1:
            next_entry = file_entries[i+1]
            size = next_entry['offset'] - current_entry['offset']
        else:
            size = len(scd_data) - start_pos

        file_data = scd_data[start_pos : start_pos + size]
        output_filepath = os.path.join(scd_output_dir, current_entry['name'])
        try:
            with open(output_filepath, 'wb') as f_out:
                f_out.write(file_data)
            print(f"  -> Extraído '{current_entry['name']}' ({size} bytes) para '{scd_output_dir}'")
        except IOError as e:
            print(f"Erro ao salvar '{current_entry['name']}': {e}")

    print(f"--- Processamento de {os.path.basename(scd_path)} concluído. ---\n")


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not os.path.isdir(INPUT_DIR):
        print(f"Erro: O diretório '{INPUT_DIR}' não foi encontrado.")
    else:
        scd_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.scd')]
        if not scd_files:
            print(f"Nenhum arquivo .scd encontrado na pasta '{INPUT_DIR}'.")
        else:
            for scd_file in scd_files:
                scd_path = os.path.join(INPUT_DIR, scd_file)
                unpack_scd(scd_path, OUTPUT_DIR)
            print("Todos os arquivos foram processados. 🐍")
