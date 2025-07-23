# Gemm-Aid

## AI-Powered Medical Assistant

Gemm-Aid is a lightweight, offline-capable health assistant designed for both emergency and daily use. Built for the **Gemma 3n Impact Challenge**, it demonstrates how efficient local inference can support critical scenarios with speed and reliability.

---

## Features

- Main Mode – Interactive, memory-based symptom checking  
- Emergency Mode – Fast, memoryless response system for urgent input  
- Powered by Gemma 3n – Local inference with a small, efficient LLM  
- Fuzzy Matching – Quick symptom retrieval from structured knowledge  
- Persistent Memory – Tracks and adapts to user interactions over time
- NiceGUI Frontend – Clean, responsive, ChatGPT-style interface  
- Fully Offline – All processing is done locally with no internet required

---

## Technical Overview

| Component            | Description                                                        |
|----------------------|--------------------------------------------------------------------|
| `main.py`            | Core logic for main mode (memory, knowledge, Gemma3n prompt flow) |
| `emergency_mode.py`  | Fast-response logic for emergency input, no memory used           |
| `gui.py`             | NiceGUI frontend with dual-mode chat interface                    |
| `Knowledge/`         | Health response database (JSON)                                   |
| `Memory/`            | Stores user memory; default file included for startup             |

### Models Used

- Gemma 3n (LLM backend)
- FuzzyWuzzy (text-based symptom matcher)


