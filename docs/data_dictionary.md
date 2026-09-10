# Dicionario de dados

## Escopo e origem

Este contrato define os dados usados no MVP de F1 Telemetry & Race Analytics.
A temporada selecionada para o MVP e **2022**. Os tipos foram validados no
notebook `notebooks/01_data_exploration.ipynb` com a sessao **Bahrain Grand Prix
2022 - Race**, usando FastF1 3.8.3 e pandas.

`nullable` descreve se o campo apresentou valores nulos na amostra validada;
campos opcionais podem ser nulos em outras corridas mesmo quando nao foram
nulos nessa amostra.

## seasons

| source | column | datatype | description | nullable |
|---|---|---|---|---|
| FastF1 / MVP | season | int64 | Ano da temporada analisada. | nao |

## events

| source | column | datatype | description | nullable |
|---|---|---|---|---|
| FastF1 `get_event_schedule` | RoundNumber | int64 | Numero da etapa no calendario. | nao |
| FastF1 `get_event_schedule` | Country | object | Pais do evento. | nao |
| FastF1 `get_event_schedule` | Location | object | Localidade ou circuito do evento. | nao |
| FastF1 `get_event_schedule` | OfficialEventName | object | Nome oficial do evento. | nao |
| FastF1 `get_event_schedule` | EventDate | datetime64[ns] | Data principal do evento. | nao |
| FastF1 `get_event_schedule` | EventName | object | Nome curto do evento. | nao |
| FastF1 `get_event_schedule` | EventFormat | object | Formato do fim de semana. | nao |
| FastF1 `get_event_schedule` | Session1 | object | Nome da primeira sessao do evento. | nao |
| FastF1 `get_event_schedule` | Session1Date | object | Data da primeira sessao, conforme o calendario. | nao |
| FastF1 `get_event_schedule` | Session1DateUtc | datetime64[ns] | Data UTC da primeira sessao. | nao |
| FastF1 `get_event_schedule` | Session2 | object | Nome da segunda sessao do evento. | nao |
| FastF1 `get_event_schedule` | Session2Date | object | Data da segunda sessao, conforme o calendario. | nao |
| FastF1 `get_event_schedule` | Session2DateUtc | datetime64[ns] | Data UTC da segunda sessao. | nao |
| FastF1 `get_event_schedule` | Session3 | object | Nome da terceira sessao do evento. | nao |
| FastF1 `get_event_schedule` | Session3Date | object | Data da terceira sessao, conforme o calendario. | nao |
| FastF1 `get_event_schedule` | Session3DateUtc | datetime64[ns] | Data UTC da terceira sessao. | nao |
| FastF1 `get_event_schedule` | Session4 | object | Nome da quarta sessao do evento. | nao |
| FastF1 `get_event_schedule` | Session4Date | object | Data da quarta sessao, conforme o calendario. | nao |
| FastF1 `get_event_schedule` | Session4DateUtc | datetime64[ns] | Data UTC da quarta sessao. | nao |
| FastF1 `get_event_schedule` | Session5 | object | Nome da quinta sessao do evento. | nao |
| FastF1 `get_event_schedule` | Session5Date | object | Data da quinta sessao, conforme o calendario. | nao |
| FastF1 `get_event_schedule` | Session5DateUtc | datetime64[ns] | Data UTC da quinta sessao. | nao |
| FastF1 `get_event_schedule` | F1ApiSupport | bool | Indica se o evento possui suporte pela F1 API. | nao |

## sessions

A entidade `sessions` e uma camada canonica do projeto, formada a partir do
objeto `Session` do FastF1 e do calendario do evento.

| source | column | datatype | description | nullable |
|---|---|---|---|---|
| FastF1 `Session` / MVP | season | int64 | Ano da temporada. | nao |
| FastF1 `Session` / MVP | round | int64 | Numero da etapa no calendario. | nao |
| FastF1 `Session` / MVP | session_type | object | Tipo da sessao, por exemplo `R`, `Q`, `FP1`. | nao |
| FastF1 `Session` / MVP | session_name | object | Nome legivel da sessao. | nao |
| FastF1 `Session` / MVP | date | datetime64[ns] | Data e hora de inicio da sessao. | nao |

## drivers

Os campos abaixo correspondem a `session.results` do FastF1. A tabela representa
o resultado dos pilotos na sessao, incluindo identificacao, equipe e resultado.

| source | column | datatype | description | nullable |
|---|---|---|---|---|
| FastF1 `session.results` | DriverNumber | object | Numero do piloto. | nao |
| FastF1 `session.results` | BroadcastName | object | Nome formatado para transmissao. | nao |
| FastF1 `session.results` | Abbreviation | object | Abreviacao de tres letras. | nao |
| FastF1 `session.results` | DriverId | object | Identificador do piloto no FastF1. | nao |
| FastF1 `session.results` | TeamName | object | Nome da equipe. | nao |
| FastF1 `session.results` | TeamColor | object | Cor da equipe. | nao |
| FastF1 `session.results` | TeamId | object | Identificador da equipe. | nao |
| FastF1 `session.results` | FirstName | object | Primeiro nome. | nao |
| FastF1 `session.results` | LastName | object | Sobrenome. | nao |
| FastF1 `session.results` | FullName | object | Nome completo. | nao |
| FastF1 `session.results` | HeadshotUrl | object | URL da imagem do piloto. | nao |
| FastF1 `session.results` | CountryCode | object | Codigo do pais do piloto. | nao |
| FastF1 `session.results` | Position | float64 | Posicao final numerica. | nao |
| FastF1 `session.results` | ClassifiedPosition | object | Posicao final classificada, incluindo estados especiais. | nao |
| FastF1 `session.results` | GridPosition | float64 | Posicao de largada. | nao |
| FastF1 `session.results` | Q1 | timedelta64[ns] | Tempo da primeira parte da classificacao. | sim |
| FastF1 `session.results` | Q2 | timedelta64[ns] | Tempo da segunda parte da classificacao. | sim |
| FastF1 `session.results` | Q3 | timedelta64[ns] | Tempo da terceira parte da classificacao. | sim |
| FastF1 `session.results` | Time | timedelta64[ns] | Tempo total ou diferenca do resultado. | sim |
| FastF1 `session.results` | Status | object | Status final do piloto. | nao |
| FastF1 `session.results` | Points | float64 | Pontos obtidos na sessao. | nao |
| FastF1 `session.results` | Laps | float64 | Numero de voltas completadas. | nao |

## laps

Os campos abaixo correspondem a `session.laps`. Uma linha representa uma volta
de um piloto durante uma sessao.

| source | column | datatype | description | nullable |
|---|---|---|---|---|
| FastF1 `session.laps` | Time | timedelta64[ns] | Tempo da volta relativo ao inicio da sessao. | nao |
| FastF1 `session.laps` | Driver | object | Abreviacao ou identificador do piloto. | nao |
| FastF1 `session.laps` | DriverNumber | object | Numero do piloto. | nao |
| FastF1 `session.laps` | LapTime | timedelta64[ns] | Duracao da volta. | sim |
| FastF1 `session.laps` | LapNumber | float64 | Numero sequencial da volta. | nao |
| FastF1 `session.laps` | Stint | float64 | Numero do stint. | nao |
| FastF1 `session.laps` | PitOutTime | timedelta64[ns] | Tempo de saida dos boxes relativo a sessao. | sim |
| FastF1 `session.laps` | PitInTime | timedelta64[ns] | Tempo de entrada nos boxes relativo a sessao. | sim |
| FastF1 `session.laps` | Sector1Time | timedelta64[ns] | Duracao do setor 1. | sim |
| FastF1 `session.laps` | Sector2Time | timedelta64[ns] | Duracao do setor 2. | sim |
| FastF1 `session.laps` | Sector3Time | timedelta64[ns] | Duracao do setor 3. | sim |
| FastF1 `session.laps` | Sector1SessionTime | timedelta64[ns] | Momento de conclusao do setor 1 na sessao. | sim |
| FastF1 `session.laps` | Sector2SessionTime | timedelta64[ns] | Momento de conclusao do setor 2 na sessao. | sim |
| FastF1 `session.laps` | Sector3SessionTime | timedelta64[ns] | Momento de conclusao do setor 3 na sessao. | sim |
| FastF1 `session.laps` | SpeedI1 | float64 | Velocidade no primeiro speed trap intermediario. | sim |
| FastF1 `session.laps` | SpeedI2 | float64 | Velocidade no segundo speed trap intermediario. | sim |
| FastF1 `session.laps` | SpeedFL | float64 | Velocidade na linha de chegada. | sim |
| FastF1 `session.laps` | SpeedST | float64 | Velocidade no speed trap. | sim |
| FastF1 `session.laps` | IsPersonalBest | object | Indicador de melhor volta pessoal. | sim |
| FastF1 `session.laps` | Compound | object | Composto do pneu. | nao |
| FastF1 `session.laps` | TyreLife | float64 | Idade do pneu em voltas. | nao |
| FastF1 `session.laps` | FreshTyre | bool | Indica se o pneu era novo no stint. | nao |
| FastF1 `session.laps` | Team | object | Equipe do piloto. | nao |
| FastF1 `session.laps` | LapStartTime | timedelta64[ns] | Tempo de inicio da volta na sessao. | nao |
| FastF1 `session.laps` | LapStartDate | datetime64[ns] | Data e hora de inicio da volta. | nao |
| FastF1 `session.laps` | TrackStatus | object | Status da pista durante a volta. | nao |
| FastF1 `session.laps` | Position | float64 | Posicao do piloto na volta. | sim |
| FastF1 `session.laps` | Deleted | object | Indicador de volta deletada. | sim |
| FastF1 `session.laps` | DeletedReason | object | Motivo da delecao da volta. | sim |
| FastF1 `session.laps` | FastF1Generated | bool | Indica se o registro foi gerado pelo FastF1. | nao |
| FastF1 `session.laps` | IsAccurate | bool | Indicador de precisao da volta. | nao |

## telemetry

A entidade `telemetry` e derivada de `fastest_lap.get_telemetry()` para uma
volta selecionada. Uma linha representa uma amostra temporal da telemetria.

| source | column | datatype | description | nullable |
|---|---|---|---|---|
| FastF1 `Lap.get_telemetry` | Date | datetime64[ns] | Data e hora da amostra. | nao |
| FastF1 `Lap.get_telemetry` | SessionTime | timedelta64[ns] | Tempo da amostra desde o inicio da sessao. | nao |
| FastF1 `Lap.get_telemetry` | DriverAhead | object | Identificador do piloto a frente. | nao |
| FastF1 `Lap.get_telemetry` | DistanceToDriverAhead | float64 | Distancia ao piloto a frente. | sim |
| FastF1 `Lap.get_telemetry` | Time | timedelta64[ns] | Tempo relativo ao inicio da volta. | nao |
| FastF1 `Lap.get_telemetry` | RPM | float64 | Rotacao do motor. | nao |
| FastF1 `Lap.get_telemetry` | Speed | float64 | Velocidade do carro. | nao |
| FastF1 `Lap.get_telemetry` | nGear | int64 | Marcha engatada. | nao |
| FastF1 `Lap.get_telemetry` | Throttle | float64 | Percentual de acelerador. | nao |
| FastF1 `Lap.get_telemetry` | Brake | bool | Indicador de acionamento do freio. | nao |
| FastF1 `Lap.get_telemetry` | DRS | int64 | Estado do sistema DRS. | nao |
| FastF1 `Lap.get_telemetry` | Source | object | Fonte da amostra de telemetria. | nao |
| FastF1 `Lap.get_telemetry` | Distance | float64 | Distancia percorrida na volta. | nao |
| FastF1 `Lap.get_telemetry` | RelativeDistance | float64 | Distancia normalizada na volta. | nao |
| FastF1 `Lap.get_telemetry` | Status | object | Estado da amostra ou do carro. | nao |
| FastF1 `Lap.get_telemetry` | X | float64 | Coordenada espacial X do carro. | nao |
| FastF1 `Lap.get_telemetry` | Y | float64 | Coordenada espacial Y do carro. | nao |
| FastF1 `Lap.get_telemetry` | Z | float64 | Coordenada espacial Z do carro. | nao |

## weather

Os campos abaixo correspondem a `session.laps.get_weather_data()`. As leituras
sao alinhadas temporalmente as amostras de volta disponiveis na sessao.

| source | column | datatype | description | nullable |
|---|---|---|---|---|
| FastF1 `Laps.get_weather_data` | Time | timedelta64[ns] | Tempo relativo ao inicio da sessao. | nao |
| FastF1 `Laps.get_weather_data` | AirTemp | float64 | Temperatura do ar. | nao |
| FastF1 `Laps.get_weather_data` | Humidity | float64 | Umidade relativa do ar. | nao |
| FastF1 `Laps.get_weather_data` | Pressure | float64 | Pressao atmosferica. | nao |
| FastF1 `Laps.get_weather_data` | Rainfall | bool | Indicador de chuva. | nao |
| FastF1 `Laps.get_weather_data` | TrackTemp | float64 | Temperatura da pista. | nao |
| FastF1 `Laps.get_weather_data` | WindDirection | int64 | Direcao do vento em graus. | nao |
| FastF1 `Laps.get_weather_data` | WindSpeed | float64 | Velocidade do vento. | nao |

## Regras do contrato

- `source` identifica o objeto ou metodo FastF1 que origina o campo.
- `datatype` registra o `dtype` pandas observado, nao uma garantia de tipo SQL.
- Valores `timedelta64[ns]` devem ser convertidos para uma unidade definida pela
  camada analitica antes de serem persistidos em bancos relacionais.
- Campos `object` podem conter strings, identificadores ou valores especiais
  fornecidos pelo FastF1; a normalizacao desses campos fica para a camada de
  ingestao.
- A validacao deve ser repetida quando outra temporada ou tipo de sessao for
  incorporado ao MVP, pois disponibilidade e nulabilidade podem variar.
