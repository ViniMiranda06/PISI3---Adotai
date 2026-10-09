# 🐾 Adotai - Dashboard de Permanência em abrigos de animais

Um Recurso visual Interativo do nosso projeto que reflete o tempo de permanência dos animais no Austin Animal Center.

## 🎯 Objetivo
Permitir que qualquer pessoa, sem conhecer o projeto, entenda o problema, o que foi feito e o que foi alcançado.

## 🌿 Branches
- `main-eda`: notebook de análise exploratória e modelos
- `main-dash`: base do dashboard
- `dash/pagina-*`: uma branch por página, que volta para `main-dash` por pull request

## 🗂️ Estrutura do dashboard
| Página | Pergunta que responde |
|---|---|
| Início | Do que se trata o projeto? |
| Os dados | Quanto tempo os animais ficam no abrigo? |
| Perfis | Existem tipos de animais com estadias diferentes? |
| Modelos | Dá para prever a permanência? |
| Explicabilidade e app | O que pesa na previsão e como ajudar na adoção? |

## 🧱 Padrão das páginas
Todas seguem o mesmo roteiro:
título como pergunta → gráfico → "o que isso significa" (2 a 3 linhas) → conclusão.
As cores e fontes ficam em `Dashboard/tema.py`. Nunca copiar hex direto no código.

## 📓 Origem dos resultados
Os resultados vêm do notebook `PISI3_EDA.ipynb` (K-Means, Random Forest,
Regressão Logística, KNN, SMOTE e SHAP). Dados: Austin Animal Center
(Kaggle), 79.672 registros.

## 🚀 Como executar
1. Clone e entre na branch do dashboard:
   `git clone https://github.com/ViniMiranda06/PISI3---Adotai`
   `git checkout main-dash`
2. Instale as dependências:
   `pip install -r Dashboard/requirements.txt`
3. Rode:
   `cd Dashboard && python app.py`
4. Abra http://127.0.0.1:8050 no navegador.

## 👥 Equipe
*   **Vinícius de Oliveira Miranda** - Pisi3
*   **Júlio Gabriel** - Pisi3
*   **Hilário Leal** - Pisi3 & DSI
*   **João Augusto** - Pisi3
*   **Matheus Lima** - DSI
