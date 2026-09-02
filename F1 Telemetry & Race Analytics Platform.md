# F1 Telemetry & Race Analytics Platform

**Tipo:** Projeto de Portfólio — Data Engineering + Data Science  
**Domínio:** Formula 1 / Motorsport Analytics  
**Papel:** Data Scientist / Data Engineer  
**Prioridade:** Alta  
**Estratégia:** Construir primeiro um MVP funcional e evoluir para uma plataforma analítica completa.

---

# 1. Visão do Produto

## 1.1 Problema

Dados de Formula 1 possuem informações de corrida, voltas, pilotos, equipes, pneus, clima e telemetria. Porém, esses dados normalmente estão distribuídos em diferentes estruturas e precisam ser processados antes de responder perguntas relevantes sobre performance.

O projeto tem como objetivo transformar esses dados em uma plataforma capaz de:

> **coletar, organizar, processar, analisar e visualizar dados de sessões de F1, permitindo avaliar performance de pilotos, carros, pneus e estratégias de corrida.**

A plataforma deverá combinar **Data Engineering, análise estatística, séries temporais, processamento de sinais e Machine Learning**.

---

# 2. Objetivos

## 2.1 Objetivo principal

Construir uma plataforma de analytics capaz de ingerir dados históricos de F1 e gerar análises reprodutíveis sobre performance de pilotos e equipes.

## 2.2 Objetivos secundários

Demonstrar domínio de:

- Python
- SQL
- ETL / ELT
- Data Lake
- Parquet
- AWS S3
- AWS Glue
- Athena
- Data Quality
- Feature Engineering
- Statistical Analysis
- Machine Learning
- Time Series
- Data Visualization
- Docker
- Testes automatizados
- CI/CD

---

# 3. Perguntas de Negócio

A plataforma deve permitir responder perguntas como:

### Performance

- Qual piloto foi mais rápido em determinado circuito?
- Em quais setores cada piloto ganha ou perde tempo?
- Qual é a diferença média entre companheiros de equipe?
- Como a performance muda ao longo de uma corrida?

### Pneus

- Como o tempo de volta evolui conforme o pneu envelhece?
- Qual composto apresenta melhor desempenho?
- Qual é a degradação estimada por composto?

### Telemetria

- Onde um piloto está perdendo tempo na pista?
- Qual é a diferença de velocidade entre dois pilotos em uma curva?
- Onde ocorre a maior diferença de frenagem?
- Qual piloto possui maior velocidade de entrada/saída de curva?

### Estratégia

- Qual estratégia de pneus apresentou melhor resultado?
- Quanto tempo foi perdido em pit stops?
- Qual estratégia teria sido potencialmente melhor dadas determinadas condições?

### Machine Learning

- É possível prever o tempo de uma volta?
- É possível prever degradação dos pneus?
- É possível identificar voltas anômalas?
- É possível estimar performance esperada de um piloto em determinada condição?

---

# 4. Fontes de Dados

## 4.1 FastF1

A principal fonte do projeto será o **FastF1**, uma biblioteca Python desenvolvida para acessar e analisar resultados, timing, telemetria e outros dados de Formula 1.

Ela permite trabalhar com:

- lap timing
- telemetria
- posição do carro
- dados de pilotos
- dados de sessões
- pneus
- clima
- informações de corrida

O FastF1 também utiliza cache para os dados acessados, o que será útil para desenvolver um pipeline reprodutível.

Documentação:

[FastF1 Documentation](https://docs.fastf1.dev/?utm_source=chatgpt.com)

---

## 4.2 Jolpica F1 API

Como segunda fonte, utilizar a API compatível com o ecossistema Ergast/Jolpica para dados estruturados de campeonatos, corridas, pilotos, equipes e resultados.

Ela pode ser utilizada para complementar os dados de telemetria.

Arquiteturalmente:

```text
FastF1
    +
Jolpica API
    ↓
Data Ingestion Layer
```

A utilização de duas fontes também permitirá demonstrar um problema muito comum em Data Engineering:

> integração e normalização de fontes heterogêneas.

---

# 5. Escopo do MVP

O MVP **não deverá tentar resolver tudo**.

A primeira versão deverá trabalhar com:

### Temporadas

Começar com **uma temporada completa**, preferencialmente uma temporada recente com dados disponíveis.

Depois expandir para múltiplas temporadas.

### Sessões

Inicialmente:

- Race
- Qualifying

Practice e Sprint entram posteriormente.

Isso também reduz o risco operacional de depender inicialmente de toda a cobertura de dados disponível.

---

# 6. Arquitetura Inicial

A arquitetura proposta:

```text
                    ┌─────────────────┐
                    │    FastF1       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Jolpica API   │
                    └────────┬────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Data Ingestion    │
                  │       Python        │
                  └──────────┬──────────┘
                             │
                             ▼
                       ┌───────────┐
                       │    S3     │
                       │   RAW     │
                       └─────┬─────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Cleaning / Transform │
                  └──────────┬──────────┘
                             │
                             ▼
                       ┌───────────┐
                       │  PARQUET  │
                       │  CURATED  │
                       └─────┬─────┘
                             │
                  ┌──────────▼──────────┐
                  │      Glue Catalog   │
                  └──────────┬──────────┘
                             │
                             ▼
                       ┌───────────┐
                       │  Athena   │
                       └─────┬─────┘
                             │
               ┌─────────────┴─────────────┐
               ▼                           ▼
       ┌─────────────────┐        ┌─────────────────┐
       │ Data Analytics  │        │ Feature Pipeline│
       └────────┬────────┘        └────────┬────────┘
                │                          │
                │                          ▼
                │                  ┌───────────────┐
                │                  │ ML / Modeling │
                │                  └───────┬───────┘
                │                          │
                └────────────┬─────────────┘
                             ▼
                      ┌─────────────┐
                      │  Streamlit  │
                      │  Dashboard  │
                      └─────────────┘
```

---

# 7. Data Lake

Organizar o S3 em três camadas:

```text
s3://f1-platform/

    raw/
        source=fastf1/
        source=jolpica/

    curated/
        sessions/
        laps/
        telemetry/
        weather/
        drivers/
        constructors/
        pitstops/

    analytics/
        driver_performance/
        tyre_performance/
        sector_analysis/
        anomaly_detection/
        predictions/
```

## RAW

Dados originais, sem transformação.

Princípio:

> Never modify raw data.

---

## CURATED

Dados tratados e normalizados.

Exemplo:

```text
year
round
circuit_id
session
driver_id
lap_number
lap_time
sector_1
sector_2
sector_3
compound
tyre_life
position
```

---

## ANALYTICS

Dados derivados para consumo.

Exemplo:

```text
driver_id
circuit
avg_lap_time
best_lap
sector_delta
tyre_degradation
consistency_score
anomaly_score
```

---

# 8. Modelo de Dados

Uma primeira versão do modelo pode ser:

```text
DIM_DRIVER
----------
driver_id
driver_name
driver_code
nationality


DIM_TEAM
--------
team_id
team_name


DIM_CIRCUIT
-----------
circuit_id
circuit_name
country
location
length


DIM_SESSION
-----------
session_id
year
round
session_type
date
circuit_id


FACT_LAP
--------
session_id
driver_id
lap_number
lap_time
sector_1
sector_2
sector_3
compound
tyre_life
position
pit_in
pit_out


FACT_TELEMETRY
--------------
session_id
driver_id
lap_number
timestamp
distance
speed
throttle
brake
gear
rpm
x
y
z


FACT_WEATHER
------------
session_id
timestamp
air_temperature
track_temperature
humidity
pressure
wind_speed
rainfall
```

Não é necessário implementar tudo na primeira sprint.

---

# 9. Feature Engineering

Uma das partes mais importantes do projeto será transformar telemetria e timing bruto em variáveis analíticas.

## Performance

```text
best_lap
median_lap
mean_lap
lap_std
sector_1_mean
sector_2_mean
sector_3_mean
```

## Velocidade

```text
max_speed
avg_speed
corner_entry_speed
corner_exit_speed
```

## Frenagem

```text
braking_distance
max_braking
braking_time
```

## Pneus

```text
tyre_age
compound
laps_on_stint
lap_time_delta
estimated_degradation
```

## Consistência

```text
lap_time_std
rolling_mean
rolling_std
```

---

# 10. Primeiros Produtos Analíticos

## 10.1 Driver Comparison

Comparação direta:

```text
Driver A
vs
Driver B
```

Mostrar:

```text
Best Lap
Average Lap
Sector 1
Sector 2
Sector 3
Top Speed
Consistency
Tyre Degradation
```

---

# 11. Telemetry Delta Analysis

Uma das principais funcionalidades.

Selecionar:

```text
Driver A
Driver B
Lap N
```

E calcular:

```text
ΔSpeed
ΔThrottle
ΔBrake
ΔDistance
ΔLapTime
```

Visualização:

```text
Speed

Driver A ───────────────╮
                        │
Driver B ───────╮───────╯
                │
                └────────────
```

Também gerar:

> **Where does Driver A gain time over Driver B?**

---

# 12. Track Mapping

Transformar coordenadas de telemetria em um mapa do circuito.

Exemplo:

```text
              Turn 4
             /-----\
            /       \
      _____/         \____
     /                    \
    |                      |
    |                      |
     \_____            ____/
           \----------/
```

Aplicar métricas sobre o circuito:

```text
speed
braking
throttle
delta
```

Isso cria uma visualização muito forte para o portfólio.

---

# 13. Tire Degradation Model

Uma primeira abordagem estatística:

```text
Lap Time = baseline + degradation × tyre_age
```

Depois evoluir para um modelo multivariado:

```text
lap_time ~
    tyre_age
    + compound
    + track_temperature
    + driver
    + fuel_effect
    + track_status
```

Posteriormente:

```text
XGBoost
```

ou outro modelo apropriado.

O objetivo não é simplesmente maximizar métricas de ML, mas construir uma explicação útil para:

> **How quickly does each tyre compound lose performance?**

---

# 14. Lap Time Prediction

Criar um modelo que estime:

```text
Expected Lap Time
```

Features:

```text
driver
team
compound
tyre_age
previous_lap_time
sector_times
track_temperature
air_temperature
track_status
```

Output:

```text
Predicted Lap Time
Confidence / Error
```

Inicialmente:

```text
Baseline
↓
Linear Regression
↓
Random Forest
↓
XGBoost
```

Comparar os modelos.

---

# 15. Anomaly Detection

Criar uma camada de detecção automática de comportamento anormal.

Exemplo:

```text
Normal lap
    ↓
Expected telemetry
    ↓
Observed telemetry
    ↓
Residual
    ↓
Anomaly Score
```

Pode começar utilizando:

```text
Isolation Forest
```

ou métodos estatísticos.

Detectar:

- voltas fora do padrão
- perda anormal de performance
- comportamento anormal de velocidade
- setores inconsistentes

---

# 16. Race Strategy Analytics

Depois do MVP analítico, criar:

> **Race Strategy Simulator**

Dados:

```text
tyre degradation
pit stop duration
lap time
tyre compound
weather
track status
```

Simular estratégias:

```text
Strategy A
Medium → Hard

Strategy B
Soft → Medium → Hard

Strategy C
Medium → Medium
```

Usar Monte Carlo:

```text
10,000 simulations
        ↓
Expected Race Time
Probability of strategy being better
```

---

# 17. Dashboard

O dashboard será dividido em módulos.

## Overview

```text
Season
Race
Session
Driver
Team
```

## Race Analytics

Mostrar:

- posição
- gap
- lap time
- stint
- pit stops

## Driver Comparison

Comparar dois pilotos.

## Telemetry

Mostrar:

- speed
- throttle
- brake
- gear
- RPM

## Track Analysis

Mapa do circuito + métricas.

## Tyres

Mostrar:

- tyre life
- degradation
- lap time evolution

## ML

Mostrar:

- prediction
- error
- anomaly score

---

# 18. Backlog do Produto

As tarefas abaixo devem ser executadas **na ordem apresentada**.

---

# EPIC 1 — Project Foundation

## TASK 1.1 — Criar repositório

Criar GitHub:

```text
F1_telemetry_analytics
```

Estrutura inicial:

```text
src/
tests/
notebooks/
configs/
scripts/
docker/
docs/
.github/
README.md
pyproject.toml
Dockerfile
```

### Critério de aceite

O projeto deve possuir:

- README
- estrutura de diretórios
- ambiente Python
- Git
- `.gitignore`
- dependências versionadas

---

## TASK 1.2 — Configurar ambiente

Criar ambiente com:

```text
Python
pandas
numpy
scipy
scikit-learn
fastf1
pyarrow
duckdb
plotly
streamlit
pytest
```

Depois adicionar dependências AWS.

### Critério de aceite

Executar:

```bash
pytest
```

sem erros.

---

# EPIC 2 — Data Discovery

## TASK 2.1 — Explorar FastF1

Criar notebook:

```text
01_data_exploration.ipynb
```

Investigar:

- seasons
- events
- sessions
- drivers
- laps
- telemetry
- weather

---

## TASK 2.2 — Selecionar temporada inicial

Escolher uma temporada para o MVP.

Critério:

> disponibilidade, estabilidade dos dados e variedade suficiente para demonstrar as análises.

---

## TASK 2.3 — Definir contrato dos dados

Documentar:

```text
source
column
datatype
description
nullable
```

Criar:

```text
docs/data_dictionary.md
```

---

# EPIC 3 — Data Ingestion

## TASK 3.1 — Criar FastF1 extractor

Criar:

```text
src/ingestion/fastf1_loader.py
```

Responsabilidades:

```text
get_season()
get_event()
get_session()
get_laps()
get_telemetry()
get_weather()
```

---

## TASK 3.2 — Implementar cache

Evitar baixar novamente dados já processados.

---

## TASK 3.3 — Criar pipeline de ingestão

Exemplo:

```bash
python -m src.ingestion.run \
    --year 2025 \
    --session race
```

---

## TASK 3.4 — Persistir RAW

Salvar dados em:

```text
data/raw/
```

Durante desenvolvimento.

Depois migrar para:

```text
S3/raw/
```

---

# EPIC 4 — Data Transformation

## TASK 4.1 — Normalização

Padronizar:

- nomes
- tipos
- timestamps
- unidades
- identificadores

---

## TASK 4.2 — Criar tabelas curated

Criar:

```text
drivers
teams
circuits
sessions
laps
telemetry
weather
```

Formato:

```text
Parquet
```

---

## TASK 4.3 — Data Quality

Implementar verificações:

```text
duplicate records
null percentage
invalid lap time
invalid driver
missing telemetry
invalid timestamp
```

Pode começar com:

```text
Great Expectations
```

ou checks próprios em Python.

---

# EPIC 5 — AWS Data Platform

## TASK 5.1 — Criar bucket S3

Estrutura:

```text
raw/
curated/
analytics/
```

---

## TASK 5.2 — Configurar Glue Catalog

Criar tabelas:

```text
f1_laps
f1_telemetry
f1_weather
f1_drivers
```

---

## TASK 5.3 — Consultas Athena

Criar queries analíticas:

```text
best lap
average lap
driver comparison
tyre performance
pit stops
sector performance
```

---

# EPIC 6 — Analytics Engine

## TASK 6.1 — Driver Performance

Calcular:

```text
best lap
average lap
median lap
std
sector deltas
```

---

## TASK 6.2 — Sector Analysis

Para cada circuito:

```text
fastest sector
driver delta
team delta
```

---

## TASK 6.3 — Tyre Analysis

Criar:

```text
lap_time vs tyre_age
```

e estimar:

```text
degradation slope
```

---

## TASK 6.4 — Telemetry Analysis

Comparar:

```text
speed
throttle
brake
gear
```

---

# EPIC 7 — Visualization

## TASK 7.1 — Criar dashboard Streamlit

Primeira página:

```text
Race Overview
```

---

## TASK 7.2 — Driver Comparison

Adicionar comparação interativa:

```text
Driver A
Driver B
```

---

## TASK 7.3 — Telemetry page

Adicionar:

```text
speed trace
throttle
brake
gear
```

---

## TASK 7.4 — Track visualization

Criar mapa do circuito utilizando coordenadas.

---

# EPIC 8 — Machine Learning

## TASK 8.1 — Definir baseline

Criar baseline simples:

```text
previous lap
rolling average
linear regression
```

---

## TASK 8.2 — Lap Prediction

Treinar:

```text
Random Forest
XGBoost
```

Comparar:

```text
MAE
RMSE
R²
```

---

## TASK 8.3 — Feature importance

Utilizar:

```text
SHAP
```

para explicar o modelo.

---

# EPIC 9 — Anomaly Detection

## TASK 9.1

Criar features de telemetria.

## TASK 9.2

Criar baseline de comportamento normal.

## TASK 9.3

Implementar:

```text
Isolation Forest
```

## TASK 9.4

Criar:

```text
anomaly_score
```

## TASK 9.5

Visualizar anomalias no circuito.

---

# EPIC 10 — Race Strategy

Essa etapa vem **depois do MVP**.

## TASK 10.1

Modelar degradação dos pneus.

## TASK 10.2

Modelar pit stop.

## TASK 10.3

Criar simulador.

## TASK 10.4

Executar Monte Carlo.

## TASK 10.5

Comparar estratégias.

---

# 19. Roadmap

## Fase 1 — Foundation

```text
Repository
Environment
Documentation
Data discovery
```

**Resultado:** projeto tecnicamente estruturado.

---

## Fase 2 — Data Engineering

```text
FastF1
    ↓
ETL
    ↓
Parquet
    ↓
S3
    ↓
Glue
    ↓
Athena
```

**Resultado:** Data Lake funcional.

---

## Fase 3 — Analytics

```text
Lap Analysis
Sector Analysis
Tyre Analysis
Driver Comparison
Telemetry
```

**Resultado:** camada analítica.

---

## Fase 4 — Dashboard

```text
Streamlit
```

**Resultado:** produto visual utilizável.

---

## Fase 5 — Machine Learning

```text
Lap Prediction
Tyre Degradation
Anomaly Detection
```

**Resultado:** camada preditiva.

---

## Fase 6 — Advanced Analytics

```text
Race Strategy
Monte Carlo
Optimization
```

**Resultado:** plataforma analítica avançada.

---

# 20. Definition of Done

Uma tarefa somente será considerada concluída quando:

```text
[ ] código implementado
[ ] teste criado
[ ] documentação atualizada
[ ] tratamento de erros implementado
[ ] dados validados
[ ] resultado reproduzível
[ ] commit realizado
```

Para features de ML:

```text
[ ] baseline
[ ] train/validation/test
[ ] métricas
[ ] comparação com baseline
[ ] análise de erro
[ ] explicabilidade
```

---

# 21. Requisitos Não Funcionais

## Reprodutibilidade

Outra pessoa deve conseguir:

```bash
git clone ...
docker compose up
```

e executar o projeto.

---

## Idempotência

Executar o pipeline duas vezes não deve duplicar os dados.

---

## Observabilidade

Registrar:

```text
pipeline start
pipeline end
records processed
records rejected
execution time
errors
```

---

## Performance

O pipeline deve evitar carregar telemetria completa desnecessariamente em memória.

Utilizar:

```text
Parquet
partitioning
column pruning
DuckDB/Athena
```

quando apropriado.

---

# 22. Estrutura Final do GitHub

Ao final:

```text
f1-telemetry-race-analytics/
│
├── src/
│   ├── ingestion/
│   ├── transformation/
│   ├── analytics/
│   ├── features/
│   ├── models/
│   └── utils/
│
├── tests/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_driver_analysis.ipynb
│   ├── 03_telemetry_analysis.ipynb
│   ├── 04_tyre_degradation.ipynb
│   └── 05_modeling.ipynb
│
├── dashboard/
│
├── configs/
│
├── scripts/
│
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── methodology.md
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── pyproject.toml
├── README.md
└── LICENSE
```

---

# 23. Entregável Final

Ao finalizar o projeto, o GitHub deverá apresentar:

### Data Engineering

```text
API / FastF1
      ↓
ETL
      ↓
Data Lake
      ↓
Parquet
      ↓
Glue
      ↓
Athena
```

### Data Science

```text
Exploratory Analysis
      ↓
Feature Engineering
      ↓
Statistical Modeling
      ↓
Machine Learning
```

### Produto

```text
Streamlit Dashboard
```

### Machine Learning

```text
Lap Time Prediction
Tyre Degradation
Anomaly Detection
```

### Advanced Analytics

```text
Race Strategy Simulation
Monte Carlo
```

---

# 24. Resultado Esperado para o Portfólio

O projeto final deve permitir que um recrutador veja claramente que você sabe trabalhar com um problema **end-to-end**:

```text
               DATA ENGINEERING
                      │
                      ▼
Source → Ingestion → Data Lake → Transformation
                                     │
                                     ▼
                                Data Warehouse
                                     │
                                     ▼
                                Analytics
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
                Data Science                    Visualization
                     │                               │
                     ▼                               ▼
                    ML                           Dashboard
```

O ponto principal do projeto não será simplesmente:

> "Analisei dados de Fórmula 1."

Será:

> **"Construí uma plataforma de dados capaz de coletar, armazenar, transformar, analisar e modelar dados de telemetria e corrida de Formula 1."**

Esse posicionamento é muito mais forte para um portfólio de **Data Scientist / Data Engineer**.

---

# 25. MVP — Critério de Sucesso

O MVP será considerado bem-sucedido quando for possível executar:

```text
Selecionar:
    Season
    Race
    Session
    Driver A
    Driver B
```

e obter automaticamente:

```text
✓ Lap comparison
✓ Sector comparison
✓ Tyre analysis
✓ Telemetry comparison
✓ Track visualization
✓ Performance metrics
```

Tudo alimentado pelo pipeline de dados, sem depender de processamento manual em notebooks.

---

# 26. Backlog Futuro

Depois da primeira versão:

```text
[ ] Multi-season analysis
[ ] Sprint analysis
[ ] Weather integration
[ ] Race strategy simulator
[ ] Monte Carlo simulation
[ ] ML deployment
[ ] Model registry
[ ] Model monitoring
[ ] Data drift detection
[ ] Automated retraining
[ ] CI/CD
[ ] Airflow/Dagster
[ ] AWS Lambda / ECS
[ ] API para serving dos modelos
```

Essas funcionalidades podem transformar o projeto de um portfólio em uma **mini plataforma de ML/Data Engineering em produção**.

---

# 27. Prioridade do Produto

Como Product Owner, a prioridade será:

### P0 — Obrigatório

```text
FastF1 ingestion
Data Lake
Parquet
Data model
ETL
Athena
Driver analytics
Telemetry analytics
Dashboard
```

### P1 — Importante

```text
Tyre degradation
Lap prediction
Anomaly detection
AWS deployment
Automated tests
CI/CD
```

### P2 — Evolução

```text
Strategy simulator
Monte Carlo
Model serving
Monitoring
Drift
Retraining
```

### P3 — Nice to Have

```text
Real-time telemetry
Live race analysis
Advanced optimization
Multi-source weather
```

---

# 28. Ordem de Execução Recomendada

A sequência oficial de desenvolvimento será:

```text
1. Criar GitHub
        ↓
2. Configurar Python
        ↓
3. Explorar FastF1
        ↓
4. Escolher temporada
        ↓
5. Definir data model
        ↓
6. Construir ingestion
        ↓
7. Salvar RAW
        ↓
8. Transformar → Parquet
        ↓
9. Criar Data Lake
        ↓
10. Glue + Athena
        ↓
11. Criar métricas analíticas
        ↓
12. Driver comparison
        ↓
13. Telemetry analysis
        ↓
14. Track visualization
        ↓
15. Streamlit
        ↓
16. Tyre degradation
        ↓
17. Lap prediction
        ↓
18. Anomaly detection
        ↓
19. Race strategy simulator
        ↓
20. Docker
        ↓
21. CI/CD
        ↓
22. Documentação final
        ↓
23. Deploy
```

# 29. Definition of Success

No final, o projeto deverá demonstrar cinco capacidades principais:

**1. Data Engineering**

Conseguir coletar, armazenar e transformar dados em escala.

**2. Data Science**

Conseguir extrair padrões relevantes e construir modelos estatísticos/ML.

**3. Software Engineering**

Código modular, testado, versionado e reproduzível.

**4. Cloud Engineering**

Utilização real de serviços AWS.

**5. Product Thinking**

As análises devem responder perguntas concretas, e não simplesmente gerar gráficos.

---

## Visão final

O projeto deverá parecer menos com:

```text
"Jupyter Notebook de F1"
```

e mais com:

```text
             F1 RACE ANALYTICS PLATFORM

      ┌──────────────────────────────────┐
      │           DATA SOURCES           │
      │       FastF1 + Jolpica API      │
      └────────────────┬─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  DATA PLATFORM  │
              │   S3 / Glue     │
              │     Athena      │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │    ANALYTICS    │
              │                 │
              │ Drivers         │
              │ Tyres           │
              │ Telemetry       │
              │ Sectors         │
              │ Strategy        │
              └────────┬────────┘
                       │
             ┌─────────┴──────────┐
             ▼                    ▼
       ┌───────────┐       ┌──────────────┐
       │    ML     │       │  Dashboard   │
       │ Prediction│       │  Streamlit   │
       │ Anomaly   │       │              │
       └───────────┘       └──────────────┘
```

**Produto final:** uma plataforma de análise de performance de F1 de ponta a ponta, com dados reais, pipeline de engenharia, camada analítica, Machine Learning e interface de consumo.