# Sysreport

**Sysreport** é uma ferramenta de auditoria de sistema desenvolvida em Python, projetada para realizar diagnósticos rápidos de saúde e segurança em ambientes Linux e Windows. O projeto tem como foco a automação da coleta de dados críticos, fornecendo relatórios estruturados (JSON) para análise pós-processamento.

## Funcionalidades

* Auditoria de Logs:

  * Linux: Coleta dados de erros e aletas através do journalctl (Últimas 24 horas)
  * Segurança: Monitoramento de tentativas de força bruta via /var/log/auth.log, com extração e contagem dos IPs agressores (Top 20).
* Diagnóstico de Saúde: Módulos dedicados para verificação da saúde do sistema (CPU, Memória, Disco).
* Diagnóstico de Rede: Verificação de conectividade e status de interfaces.
* Alta Performance: Utilização de processamento paralelo (ThreadPoolExecutor) para execução simultânea de diagnósticos.
* Portabilidade: Suporte a sistemas Windows e Linux com tratamento de caminhos (Pathlib) e exceções de SO.

## Arquitetura Técnica

O projeto é modular e organizado para facilitar a expansão:
```
  sysreport/
├── main.py            # Ponto de entrada com CLI robusta (argparse)
├── modulos/           # Lógica de análise (saude, rede, logs)
└── utils/             # Helpers (logger, escrita em JSON)
```
## Principais Tecnologias:

Python 3.10+
Bibliotecas padrão: argparse, concurrent.futures, pathlib, subprocess, re, collections.Counter.

## Uso

O sysreport gera um relatório em JSON contendo os dados coletados:
```
# Execução básica
python main.py

# Especificando diretório de saída
python main.py --dir "/caminho/personalizado/relatorios"
```
## Roadmap de Desenvolvimento

* [ ] Implementar integração para envio de relatórios via webhook (ex: Discord/Slack).
* [ ] Adicionar suporte a exportação em formato de tabela para leitura rápida no terminal.
* [ ] Criar testes unitários para os módulos de análise.

## Contribuições

Contribuições são bem-vindas! Se você deseja melhorar a ferramenta:

1. Faça um fork do projeto.
2. Crie uma branch para sua funcionalidade (git checkout -b feature/[nova-analise]).
3. Faça o commit das suas alterações.
4. Abra um Pull Request detalhando as alterações. 
