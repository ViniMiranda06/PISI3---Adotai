# Resultados iniciais dos modelos de classificação

**Projeto:** Adotai — Análise da permanência de animais em abrigos  
**Responsabilidade:** P4 — Página 3: Modelos  
**Fonte:** Notebook `PISI3_EDA.ipynb`, seções 6 e 7.

## Comparação dos modelos

| Modelo | Balanceamento | Test Accuracy | Test Macro F1 |
|---|---|---:|---:|
| Random Forest | Sem SMOTE | 0.773768 | 0.529654 |
| Random Forest | Com SMOTE | 0.748792 | 0.527575 |
| Logistic Regression | Sem SMOTE | 0.753248 | 0.286420 |
| Logistic Regression | Com SMOTE | 0.529338 | 0.388797 |
| KNN | Sem SMOTE | 0.746533 | 0.444413 |
| KNN | Com SMOTE | 0.577471 | 0.441384 |

## Observações iniciais

- A Random Forest apresentou o maior F1 macro nos dois cenários avaliados.
- A Logistic Regression apresentou melhora no F1 macro após a aplicação do SMOTE, apesar da redução na acurácia.
- O KNN apresentou pequenas reduções no F1 macro e redução na acurácia após o balanceamento.

Estes resultados constituem a base para a comparação visual dos modelos e para as análises posteriores da página 3 do dashboard.