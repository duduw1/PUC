# 🦽 Cadeira de Rodas Inteligente — PUC

Projeto de cadeira de rodas controlada por movimentos da cabeça, utilizando visão computacional e Python. Desenvolvido para a disciplina de Embarcados na PUC.

## 🚀 Descrição
Este projeto permite controlar uma cadeira de rodas simulada através de movimentos da cabeça, usando algoritmos de detecção facial (dlib/mediapipe) e integração com simuladores.

## 📂 Estrutura dos Arquivos
- `1-move_automatic.py` — Controle automático (restaurado)
- `2-move_manual.py` — Controle manual (restaurado)
- `move_automatic.py` — Nova versão do controle automático
- `move_manual.py` — Nova versão do controle manual
- `3-dlib funcionando lento.py` — Versão dlib (lenta)
- `4-move_cam_mediapipe*.py` — Versões com MediaPipe
- `5-dlib_melhorado.py` — Dlib otimizado
- `6-mediapipe_melhorar.py` — MediaPipe otimizado
- `sim.py`, `simConst.py` — Integração com simulador
- `shape_predictor_68_face_landmarks.dat` — (Necessário, mas não enviado ao GitHub)

## ⚙️ Requisitos
- Python 3.8+
- OpenCV
- dlib
- mediapipe
- numpy
- (Outros conforme necessidade dos scripts)

## 🔧 Instalação
1. Clone este repositório:
   ```bash
   git clone https://github.com/duduw1/puc.git
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
   *(Crie um requirements.txt conforme os pacotes usados)*
3. Baixe o arquivo `shape_predictor_68_face_landmarks.dat` e coloque na mesma pasta dos scripts.

## 🕹️ Como Usar
Execute o script desejado, por exemplo:
```bash
python 4-move_cam_mediapipe4.py
```
Siga as instruções na tela para controlar a cadeira de rodas com movimentos da cabeça.

## ❗ Observações
- O arquivo `shape_predictor_68_face_landmarks.dat` é grande e não está no repositório. Baixe manualmente.
- Para simulação, utilize o software compatível (ex: CoppeliaSim) e configure conforme o script.

## 👨‍💻 Autores
- Seu Nome (duduw1)
- Colaboradores

---
Projeto acadêmico — PUC 2025
