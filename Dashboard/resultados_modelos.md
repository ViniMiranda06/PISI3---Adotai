# Resultados dos modelos de classificação

**Projeto:** Adotai — Análise da permanência de animais em abrigos
**Classes:** Curta (até 14 dias) e Prolongada (mais de 14 dias)
**Fonte:** notebook `PISI3_EDA.ipynb` (seções 6 a 7.6), executado do início ao fim.
A tabela completa, com métricas de treino, está em `data/resultados_modelos.csv`.

## Comparação dos modelos (conjunto de teste, 15.935 animais)

| Modelo | Balanceamento | Acurácia | F1 macro | F1 Prolongada | Recall Prolongada | F1 macro treino |
|---|---|---:|---:|---:|---:|---:|
| Random Forest | Sem SMOTE | 0,793 | 0,683 | 0,497 | 0,414 | 0,962 |
| Regressão Logística | Sem SMOTE | 0,753 | 0,431 | 0,003 | 0,002 | 0,430 |
| KNN | Sem SMOTE | 0,749 | 0,621 | 0,400 | 0,339 | 0,735 |
| Random Forest | Com SMOTE | 0,780 | 0,684 | 0,510 | 0,465 | 0,963 |
| Regressão Logística | Com SMOTE | 0,624 | 0,580 | 0,446 | 0,615 | 0,579 |
| KNN | Com SMOTE | 0,665 | 0,610 | 0,464 | 0,587 | 0,778 |
| Random Forest | Pesos por classe | 0,758 | 0,681 | 0,525 | 0,543 | 0,956 |
| Regressão Logística | Pesos por classe | 0,621 | 0,583 | 0,458 | 0,650 | 0,579 |
| **Random Forest regularizada** | **Pesos por classe** | **0,713** | **0,661** | **0,529** | **0,655** | **0,732** |

Outros experimentos (seções 10 a 14 do notebook):

| Experimento | Acurácia | F1 macro | F1 Prolongada | Recall Prolongada |
|---|---:|---:|---:|---:|
| EXP-01 — RF Regressor, corte em 14 dias | 0,65 | 0,62 | 0,51 | 0,74 |
| EXP-02 — XGBoost, dados originais | 0,79 | 0,64 | 0,41 | 0,30 |
| EXP-03 — XGBoost, pesos por classe | 0,70 | 0,65 | 0,52 | 0,66 |
| EXP-04 — XGBoost, pesos + raça e pelagem | 0,71 | 0,66 | 0,54 | 0,68 |

## Modelo final

Random Forest regularizada com pesos por classe (100 árvores, `max_depth=20`,
`min_samples_leaf=5`). O limiar de decisão de **0,51** foi escolhido por validação
cruzada (5 folds) só no treino, maximizando o F1 da classe Prolongada.

| Métrica (teste) | Valor |
|---|---:|
| Acurácia | 0,722 |
| F1 macro | 0,666 |
| ROC-AUC | 0,775 |
| F1 — Curta | 0,803 |
| F1 — Prolongada | 0,529 |
| Recall — Prolongada | 0,633 |
| Precisão — Prolongada | 0,454 |

**Matriz de confusão** (linhas = real, colunas = previsto):

| Real \ Prevista | Curta | Prolongada |
|---|---:|---:|
| Curta | 9.015 | 2.993 |
| Prolongada | 1.440 | 2.487 |

## Observações

- **Precisão:** de cada 10 animais que o modelo final marca como Prolongada, 4 a 5 realmente passam de 14 dias. Ele serve para priorizar atenção, não como certeza.
- **Acurácia engana:** responder sempre "Curta" já acerta 75,4%. Por isso o foco é o F1 macro e o recall da classe Prolongada.
- **Overfitting:** a Random Forest sem limite tem F1 macro de 0,96 no treino e 0,68 no teste. A versão regularizada reduz essa diferença para 0,07.
- **3 classes x 2 classes:** juntando as previsões Média + Longa do modelo de 3 classes, o ROC-AUC (0,769) fica praticamente igual ao do modelo de 2 classes (0,767). A mudança não aumenta o poder de previsão; ela torna a pergunta mais clara e útil para o abrigo.
- **Metodologia:** a padronização é ajustada só no treino (sem vazamento de dados) e a divisão treino/teste é estratificada (80/20, `random_state=42`).
