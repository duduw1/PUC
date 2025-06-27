# 🦽 Cadeira de Rodas Inteligente — PUC

**Autores:** Robson Duarte Vicente e Vinicius Oliveira Ribas  
**Professor:** Mario Guimaraes Buratto

Integração de sistemas de controle e visão computacional para automatização de cadeiras de rodas com comandos faciais.

## 🚀 Descrição

Este projeto permite controlar uma cadeira de rodas simulada através de movimentos da cabeça, usando algoritmos de detecção facial (dlib/mediapipe) e integração com simuladores CoppeliaSim.

## 📝 Resumo Técnico

O sistema detecta a inclinação e direção da cabeça do usuário através da webcam, traduzindo esses movimentos em comandos para a cadeira de rodas simulada no ambiente CoppeliaSim.

### Bibliotecas Principais
- **OpenCV (`cv2`)**: Captura e processa imagens da webcam em tempo real
- **MediaPipe**: Detecção facial e pose corporal (versão principal)
- **dlib**: Detecção de landmarks faciais (versão alternativa)
- **NumPy**: Cálculos matemáticos e manipulação de arrays
- **Tkinter**: Interface gráfica do usuário
- **Pillow (PIL)**: Manipulação e exibição de imagens
- **CoppeliaSim API**: Integração com o simulador

## 🎮 Modos de Operação

### 1. Modo Principal (MediaPipe) - **RECOMENDADO**
```bash
python 6-mediapipe_melhorar.py
```
**Características:**
- Interface gráfica completa
- Controles de sensibilidade
- Detecção de piscadas
- Sistema de trava
- Feedback visual

### 2. Modo dlib (Alternativo)
```bash
python 5-dlib_melhorado.py
```
**Características:**
- Maior precisão
- 68 pontos faciais
- Requer arquivo de modelo

### 3. Modo Manual (Mouse)
```bash
python 1-move_automatic.py
```
**Características:**
- Controle por mouse
- Interface simples
- Ideal para testes

## 🎯 Controles

| Movimento | Ação |
|-----------|------|
| Inclinar cabeça para frente | ➡️ Avançar |
| Inclinar cabeça para trás | ⬅️ Recuar |
| Girar cabeça para esquerda | ⬅️ Virar à esquerda |
| Girar cabeça para direita | ➡️ Virar à direita |
| Piscar duas vezes | 🔒 Ativar/desativar |

## 📂 Estrutura dos Arquivos

### 🎮 Programas Principais
- `6-mediapipe_melhorar.py` — **Versão principal** (MediaPipe, interface completa)
- `5-dlib_melhorado.py` — Versão dlib (mais precisa, mais lenta)
- `1-move_automatic.py` — Controle por mouse (para testes)
- `2-move_manual.py` — Controle manual
- `3-dlib funcionando lento.py` — Versão dlib (lenta)
- `4-move_cam_mediapipe*.py` — Versões com MediaPipe

### 📁 Arquivos de Simulação
- `FUNCIONAL COM TESTE 15.ttt` — Cena do CoppeliaSim
- `sim.py`, `simConst.py` — API do CoppeliaSim
- `remoteApi.dll` — Biblioteca de comunicação

### 🔧 Scripts e Ferramentas
- `install.bat` — Instalador Windows
- `install.sh` — Instalador Linux/macOS
- `Makefile` — Compilação LaTeX e comandos úteis
- `requirements.txt` — Dependências Python

### 🎯 Arquivos de Modelo
- `shape_predictor_68_face_landmarks.dat` — Modelo dlib (95MB, não incluído no Git)

## ⚙️ Requisitos

### Sistema
- Python 3.8+
- Webcam funcional
- CoppeliaSim 4.5+ (para simulação)
- 8GB RAM (recomendado 16GB)

### Dependências Python
```bash
pip install -r requirements.txt
```

## 🔧 Instalação

### 1. Clone este repositório:
```bash
git clone https://github.com/duduw1/puc.git
cd embarcados-puc-cadeira-de-rodas
```

### 2. Instalação Automática
```bash
# Windows
install.bat

# Linux/macOS
chmod +x install.sh
./install.sh
```

### 3. Instalação Manual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Baixar Modelo dlib (se necessário)
- Baixe `shape_predictor_68_face_landmarks.dat` (95MB)
- Coloque na pasta raiz do projeto

## 🕹️ Como Usar

### 1. Configurar CoppeliaSim
1. Abra o CoppeliaSim
2. Carregue `FUNCIONAL COM TESTE 15.ttt`
3. Inicie a simulação
4. Verifique a porta 19997

### 2. Executar o Sistema
```bash
# Ativar ambiente virtual (se necessário)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Executar programa principal
python 6-mediapipe_melhorar.py
```

### 3. Configuração da Webcam
- Posicione-se a 50-80cm da câmera
- Mantenha iluminação adequada
- Evite óculos refletivos

### 4. Calibração
- Execute o programa
- Mantenha a cabeça neutra por 3 segundos
- Aguarde a calibração automática

## ❗ Solução de Problemas

### Problemas Comuns
- **Webcam não detectada**: Verifique drivers e permissões
- **CoppeliaSim não conecta**: Verifique porta 19997 e firewall
- **Performance baixa**: Reduza resolução ou use modo dlib
- **Erro de dependências**: Execute `pip install -r requirements.txt`

### Logs e Debug
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Documentação Adicional

### Tutorial Detalhado (LaTeX)
- **Arquivo**: `tutorial_cadeira_rodas.tex`
- **Como compilar**: `make pdf` (requer LaTeX instalado)
- **Visualizar**: `make view` (Windows) ou `make view-linux` (Linux)

### Compilação da Documentação
```bash
# Verificar se LaTeX está instalado
make check-latex

# Compilar PDF
make pdf

# Visualizar (Windows)
make view

# Limpar arquivos temporários
make clean
```

## ❗ Observações Importantes
- O arquivo `shape_predictor_68_face_landmarks.dat` é grande (95MB) e não está no repositório. Baixe manualmente se usar o modo dlib.
- Para simulação, utilize o CoppeliaSim e configure conforme as instruções acima.

## 👨‍💻 Autores
- **Robson Duarte Vicente**
- **Vinicius Oliveira Ribas**
- **Professor:** Mario Guimaraes Buratto

---
**Projeto acadêmico — PUC 2025**
