# 🐾 Previsão de Permanência em Abrigos de Animais (Austin Animal Center)

Projeto desenvolvido para a disciplina de **PISI3**, focado em aplicar técnicas de Ciência de Dados e Machine Learning para otimizar a gestão e adoção de animais.

## 🎯 Objetivo do Projeto
Analisar os dados reais do Austin Animal Center para entender os fatores que prolongam a estadia de um animal no abrigo e criar um modelo preditivo capaz de classificar estadias em: **Curta, Média ou Longa**. 

Isso permite que a gestão direcione recursos de marketing e cuidados especiais para os animais com maior risco de longa permanência desde o dia zero.

## 🛠️ Tecnologias e Métodos Utilizados
*   **Linguagem:** Python
*   **Manipulação de Dados:** Pandas, NumPy
*   **Visualização:** Matplotlib, Seaborn
*   **Machine Learning (Scikit-Learn):** 
    *   *Clusterização:* K-Means (Perfilagem de animais)
    *   *Classificação:* Random Forest, Regressão Logística, KNN
    *   *Balanceamento:* SMOTE
*   **Explicabilidade (XAI):** SHAP (Para entender "como" o modelo toma decisões).

## 🚀 Como Executar
1. Clone o repositório:
   `git clone https://github.com/ViniMiranda06/PISI3---Adotai`
2. Instale as dependências:
   `pip install pandas numpy matplotlib seaborn scikit-learn imbalanced-learn shap kagglehub`
3. Execute o script principal ou abra o Jupyter Notebook no Google Colab. O dataset será baixado automaticamente via API do Kaggle.

## 👥 Equipe
*   **Vinícius de Oliveira Miranda** - Pisi3
*   **Júlio Gabriel** - Pisi3
*   **Hilário Leal** - Pisi3 & DSI
*   **João Augusto** - Pisi3
*   **Matheus Lima** - DSI
