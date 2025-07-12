This tool was created by gopicolo for extracting and reinserting text in the game Shinseiki Evangelion Ayanami Ikusei Keikaku DS with Asuka Hokan Keikaku

# Shinseiki Evangelion Ayanami Ikusei Keikaku DS with Asuka Hokan Keikaku – Extraction and Repacking Tools
A set of Python scripts to extract, translate, repack, and rebuild `.scd` files from Nintendo DS games. The tools are primarily designed for translation and fan localization projects.

## 📁 Included Tools

### 1. `unpack.py`
Extracts `.scd` container files into individual script files.

- Input: `.scd` files in the `input/` folder
- Output: Extracted files in `output/`
- Also generates `_file_order.txt` to preserve file order

### 2. `dump.py`
Scans binary script files for dialog blocks, extracts readable text, and saves it into structured `.json` files.

- Input: Binary script files in `output/`
- Output: JSON files in `output_json/` containing extracted text blocks

### 3. `repack.py`
Reinserts translated text into the original binary scripts, using the JSON structure produced by `dump.py`.

- Input:
  - Original scripts: `output/`
  - Translations: `output_json/`
- Output: Rebuilt binary files in `repack_files/`

### 4. `repacked.py`
Rebuilds final `.scd` files using the repacked scripts, matching the original file order.

- Input:
  - Repacked files: `repack_files/`
  - File order reference: `output/*/_file_order.txt`
- Output: Final `.scd` files in `repacked_scd/`

---

## 🅰️ NFTR Font Tools

These are optional tools if you want to extract or replace the in-game font.

### 5. `unpack.py` (NFTR version)
Extracts a `.nftr` font from a decompressed `arm9.bin`.

### 6. `repack.py` (NFTR version)
Reinserts a `.nftr` font into a decompressed `arm9.bin`.

---

## 🛠 Requirements

- Python 3.7+
- No external dependencies

---

## 🧪 Usage

### 1. Extract `.scd`:
```bash
python unpack.py
```

### 2. Dump text:
```bash
python dump.py
```

### 3. Translate the JSON files in `output_json/`.

### 4. Repack text:
```bash
python repack.py
```

### 5. Rebuild `.scd` files:
```bash
python repacked.py
```

---

## 📌 Notes

- Uses Shift-JIS encoding. Be careful with characters not supported by the game.
- Each block of text is validated to ensure it's actual readable dialog before dumping.
- Repacker preserves original structure and only replaces the text blocks.

---
