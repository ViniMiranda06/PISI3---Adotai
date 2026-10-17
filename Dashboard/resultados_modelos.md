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

## Análise detalhada do Random Forest

Foram avaliadas duas configurações do Random Forest: sem balanceamento e com aplicação de SMOTE ao conjunto de treinamento. A avaliação foi realizada sobre o mesmo conjunto de teste.

### Métricas por classe

| Métrica | Sem SMOTE | Com SMOTE |
|---|---:|---:|
| Acurácia | 0,773768 | 0,749168 |
| F1 — Curta | 0,873209 | 0,858385 |
| F1 — Média | 0,345109 | 0,360531 |
| F1 — Longa | 0,370644 | 0,366999 |
| F1 macro | 0,529654 | 0,528638 |

### Matrizes de confusão

As linhas representam as classes reais e as colunas, as classes previstas. A ordem das classes é Curta, Média e Longa.

**Sem SMOTE**

| Real \ Prevista | Curta | Média | Longa |
|---|---:|---:|---:|
| Curta | 11243 | 520 | 245 |
| Média | 1550 | 635 | 166 |
| Longa | 950 | 174 | 452 |

**Com SMOTE**

| Real \ Prevista | Curta | Média | Longa |
|---|---:|---:|---:|
| Curta | 10662 | 862 | 484 |
| Média | 1355 | 760 | 236 |
| Longa | 817 | 243 | 516 |

### Interpretação

Sem SMOTE, o modelo apresenta melhor desempenho geral em acurácia e F1 macro. Com SMOTE, o F1 da classe Média aumenta de 0,345109 para 0,360531, enquanto o F1 das classes Curta e Longa diminui. O F1 macro passa de 0,529654 para 0,528638, indicando que o balanceamento não proporcionou melhora geral relevante para o Random Forest neste experimento.

**Nota metodológica:** as métricas detalhadas acima correspondem à reprodução local do experimento. Os valores com SMOTE apresentam pequenas diferenças em relação aos resultados registrados anteriormente no notebook. Para manter a consistência, esta análise utiliza os resultados da reprodução local. Além disso, a padronização das variáveis numéricas ocorreu antes da divisão entre treino e teste, o que pode introduzir vazamento de informação e deve ser considerado uma limitação metodológica.