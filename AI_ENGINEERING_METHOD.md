# Relatório de Método de Arquitetura, Orquestração e Governança — SentinelForge

## 1. Objetivo

O SentinelForge está sendo construído como um laboratório simulado de DevSecOps e Defense-in-Depth, no qual a arquitetura de segurança é implementada, executada e validada em um ambiente Docker real.

O método adotado não é simplesmente "pedir para uma IA escrever código". Ele separa:

* definição arquitetural;
* implementação;
* auditoria;
* execução no ambiente real;
* validação por evidências;
* correção controlada;
* preservação de uma baseline congelada.

A regra central é que o **runtime local real é a fonte de verdade**.

---

## 2. Método arquitetural utilizado

A arquitetura segue uma abordagem de **Defense-in-Depth orientada a controles e missões**.

A unidade conceitual principal é a missão.

Cada missão define, entre outros elementos:

* ameaça;
* alvo;
* objetivo de aprendizagem;
* controles disponíveis;
* pré-requisitos;
* contrato de execução;
* restrições arquiteturais;
* percentual mínimo de mitigação;
* impacto aceitável de latência;
* disponibilidade mínima.

O fluxo arquitetural é essencialmente:

```text
Missão
   ↓
Scenario Registry
   ↓
Orchestrator
   ↓
Baseline
   ↓
Aplicação dos controles
   ↓
Target API
   ↓
Probe Campaign
   ↓
Observed Result
   ↓
Avaliação de restrições
   ↓
Security Decision Record (SDR)
```

O SDR funciona como evidência da decisão arquitetural.

---

## 3. Papel do Orchestrator

O `orchestrator/main.py` funciona como o núcleo de orquestração.

Ele:

1. recebe a missão;
2. consulta o cenário registrado;
3. identifica os controles;
4. executa uma baseline;
5. envia os controles ao `target_api`;
6. executa novamente os probes;
7. compara baseline e resultado observado;
8. calcula mitigação, latência e disponibilidade;
9. executa integrações DevSecOps quando aplicável;
10. produz o Security Decision Record;
11. registra o resultado pedagógico.

O Orchestrator, portanto, não é simplesmente uma API intermediária. Ele é o **motor de decisão e evidência da arquitetura simulada**.

---

## 4. Scenario Registry

O `scenario_registry.py` funciona como uma camada declarativa.

Em vez de espalhar regras de cada missão pelo código, as missões são descritas como contratos.

Por exemplo, a MISSION-002 define:

* ameaça: `data_exposure`;
* endpoint: `/api/v1/user/profile`;
* probes baseados em `probe_id`;
* condição esperada de mascaramento;
* mitigação mínima de 95%;
* orçamento máximo de 30 ms;
* disponibilidade mínima de 99%.

Isso permite que o Orchestrator permaneça relativamente genérico.

---

## 5. Control Registry

O `control_registry.py` representa os controles de segurança disponíveis.

Cada controle possui:

* `control_id`;
* nome;
* camada;
* trade-offs;
* explicações de falha;
* finalidade pedagógica.

Isso cria uma separação importante:

```text
Cenário/Missão
      ≠
Controle de Segurança
      ≠
Mecanismo de Execução
```

Essa separação permite testar diferentes arquiteturas contra a mesma ameaça.

---

# 6. Método de construção entre Você, ChatGPT e Gemini

O método adotado é deliberadamente dividido em papéis.

## 6.1 Você — Arquiteto, auditor e autoridade final

Seu papel é o mais importante.

Você:

* define o objetivo;
* define o que deve ser preservado;
* executa os comandos no ambiente real;
* fornece os resultados reais;
* decide se uma alteração deve ser aceita;
* audita o comportamento;
* impede alterações especulativas;
* mantém a baseline;
* aprova ou rejeita correções.

Você é, na prática, o **System Owner / Architecture Authority**.

A regra estabelecida foi:

> Local machine + Docker runtime real = Source of Truth.

Portanto, nenhum resultado produzido apenas por uma IA substitui a execução real.

---

## 6.2 Gemini — Implementador operacional

O Gemini está sendo utilizado principalmente como **agente de implementação**.

Seu papel é:

* receber uma especificação;
* modificar os arquivos necessários;
* implementar funcionalidades;
* corrigir problemas apontados;
* sugerir testes;
* produzir alterações no código.

Ele funciona como uma espécie de **engenheiro de implementação assistido por IA**.

Entretanto, Gemini não possui autoridade final sobre a arquitetura.

Uma implementação considerada "pronta" pelo Gemini ainda precisa passar pelo processo:

```text
Implementação
      ↓
Auditoria humana
      ↓
Execução real
      ↓
Evidência
      ↓
Aceitação ou correção
```

Isso foi particularmente importante no caso da MISSION-003, em que uma avaliação anterior indicava prontidão, mas a execução real revelou que o endpoint necessário ainda não existia.

A execução local corrigiu a discrepância.

---

## 6.3 ChatGPT — Arquiteto de processo, auditor técnico e copiloto de validação

Meu papel no método é diferente do Gemini.

Estou sendo utilizado principalmente para:

* interpretar resultados;
* identificar inconsistências;
* preservar a continuidade arquitetural;
* transformar evidências em próximos passos;
* revisar decisões;
* evitar alterações desnecessárias;
* definir comandos de verificação;
* analisar o comportamento do sistema;
* ajudar a manter a governança;
* distinguir falha real de comportamento esperado;
* impedir que uma hipótese seja tratada como fato.

Em outras palavras, o papel é mais próximo de:

**Architecture / Security Review Copilot**

do que de simples gerador de código.

Também existe uma regra importante: quando o teste real ainda não foi executado, a conclusão deve permanecer como hipótese.

---

# 7. Relação entre os três papéis

O modelo pode ser representado assim:

```text
                    VOCÊ
        Architecture Authority
          Auditor / Owner
                 │
       ┌─────────┴─────────┐
       │                   │
       ▼                   ▼
   GEMINI              CHATGPT
Implementação        Análise / Auditoria
Correções            Governança
Código               Validação
Testes sugeridos     Próximos passos
       │                   │
       └─────────┬─────────┘
                 ▼
          AMBIENTE REAL
          Docker / Runtime
                 │
                 ▼
          EVIDÊNCIA REAL
                 │
                 ▼
             VOCÊ DECIDE
```

Nenhuma das duas IAs substitui o ambiente real.

---

# 8. Regra de Frozen Baseline

Uma das características mais importantes do método é a existência de uma **baseline FROZEN**.

Quando uma funcionalidade é considerada validada, ela passa a ser comportamento protegido.

Uma mudança futura precisa declarar explicitamente:

1. o que está sendo alterado;
2. por que a alteração é necessária;
3. qual comportamento existente será preservado;
4. como a alteração será validada localmente.

Isso evita o padrão perigoso de:

```text
problema pequeno
   ↓
refatoração ampla
   ↓
múltiplos arquivos alterados
   ↓
novos problemas
   ↓
mais correções
   ↓
perda da baseline
```

O método prefere:

```text
problema identificado
   ↓
menor alteração necessária
   ↓
teste específico
   ↓
validação
   ↓
preservação da baseline
```

---

# 9. Validação baseada em evidências

O projeto não considera suficiente:

* "o código parece correto";
* "o teste da IA passou";
* "o endpoint deveria funcionar";
* "a arquitetura parece pronta".

A evidência precisa vir do runtime.

Exemplo recente:

O SCA foi implementado utilizando `pip-audit`.

A execução direta confirmou:

```text
dependencies_count = 46
vulnerable_dependencies_count = 0
vulnerabilities_count = 0
decision = SECURE
returncode = 0
```

Depois o mesmo mecanismo foi executado através do fluxo da missão.

Isso comprovou que o SCA não está apenas instalado: ele está integrado ao Orchestrator e aparece no SDR como `dependency_analysis_report`.

---

# 10. Interpretação do teste da MISSION-002

O teste com:

```text
dependency_analysis_safety
```

produziu:

```text
SCA decision = SECURE
```

mas a missão terminou como:

```text
ARCHITECTURAL TRADE-OFF VIOLATION
```

Isso não significa que o SCA falhou.

A lógica atual do Orchestrator calcula `secure` utilizando:

```text
observed["mitigation_percent"] >= min_mitigation
```

Ou seja, a decisão de mitigação da missão continua baseada no resultado dos probes da própria missão.

Essa distinção é importante:

```text
SCA
→ responde sobre vulnerabilidades das dependências

data_masking
→ responde sobre exposição de PII na resposta

MISSION-002
→ mede a mitigação da exposição de PII
```

Portanto, o resultado observado revelou uma característica arquitetural real do sistema, e não necessariamente um bug.

---

# 11. Princípio de não confundir controles

O método adotado também evita considerar todos os controles como equivalentes.

Um controle pode:

* mitigar diretamente a ameaça;
* fornecer defesa complementar;
* fornecer evidência;
* detectar uma condição;
* reduzir risco de supply chain;
* proteger outra camada.

Assim, um controle `SECURE` não precisa necessariamente produzir `mitigation_percent = 100%` para uma missão que mede outra ameaça.

Essa distinção é essencial para uma arquitetura de Defense-in-Depth.

---

# 12. Segurança do processo

Para preservar segurança e estabilidade, estamos adotando:

### Regra 1 — Não alterar sem evidência

Primeiro observar.

Depois interpretar.

Somente então alterar.

### Regra 2 — Um passo por vez

Quando existe incerteza, o próximo comando deve ser pequeno e específico.

### Regra 3 — Não refatorar por conveniência

Uma funcionalidade funcionando não deve ser reorganizada simplesmente porque existe uma forma "mais elegante".

### Regra 4 — Docker é parte da validação

O código precisa funcionar no ambiente em que será executado.

### Regra 5 — Testes reais prevalecem

A saída real do terminal prevalece sobre conclusões de qualquer IA.

### Regra 6 — Mudanças devem ser reversíveis

Alterações devem ser pequenas o suficiente para identificar claramente o que mudou.

---

# 13. Método de trabalho consolidado

O processo operacional recomendado para o SentinelForge é:

```text
1. Definir objetivo
       ↓
2. Registrar contrato arquitetural
       ↓
3. Gemini implementa
       ↓
4. Você audita
       ↓
5. ChatGPT ajuda a analisar
       ↓
6. Build Docker
       ↓
7. Subir runtime
       ↓
8. Executar teste real
       ↓
9. Analisar evidência
       ↓
10. Se correto → congelar comportamento
       ↓
11. Se incorreto → identificar menor correção
       ↓
12. Gemini implementa correção
       ↓
13. Repetir validação
```

Esse ciclo é muito mais seguro do que delegar a uma IA a implementação e também a decisão de que sua própria implementação está correta.

---

# 14. Estado atual do método

Neste ponto, o SentinelForge possui uma abordagem coerente de:

* arquitetura orientada a missões;
* controles de segurança declarativos;
* Orchestrator central;
* Target API sandbox;
* probes automatizados;
* Security Decision Records;
* avaliação de mitigação;
* avaliação de latência;
* avaliação de disponibilidade;
* SAST;
* SCA com `pip-audit`;
* feedback pedagógico;
* validação através do Docker real;
* baseline congelada;
* governança de mudanças.

O SCA foi recentemente confirmado em execução real, inclusive dentro do fluxo do Orchestrator.

---

# 15. Conclusão

O método do SentinelForge pode ser resumido como:

> **IA implementa. Outra IA auxilia na análise. O humano governa. O runtime real decide.**

Gemini é utilizado para acelerar a construção.

ChatGPT é utilizado para estruturar o raciocínio, auditoria, continuidade e próximos passos.

Você permanece como autoridade arquitetural, auditor e responsável pela aceitação.

E o Docker/runtime local fornece a evidência objetiva que encerra cada ciclo.

Essa divisão reduz dois riscos comuns em projetos desenvolvidos com IA:

1. a IA declarar que uma implementação está correta sem prova real;
2. uma correção local provocar regressões em comportamento que já estava validado.

O princípio fundamental permanece:

**nenhuma alteração deve ser aceita porque uma IA diz que está correta; ela deve ser aceita porque o comportamento foi demonstrado no ambiente real e preserva a baseline estabelecida.**
