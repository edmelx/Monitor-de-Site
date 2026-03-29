# Monitor-de-Site
Um pequeno projeto de monitoramento de site. Nele é possível saber se certo site que está na lista se encontra online ou indisponível.
Uso este projeto para demonstrar minha capacidade de construir pipelines de dados do zero, desde a coleta automatizada até a visualização em tempo real. 

Das dashboards:

O histórico de verificações indica a data e o horário que a consulta foi feita. O site indica o site que está consultado. O status_code indica o código da requisição HTTP. tempo_ms mostra o tempo que levou para fazer a consulta. E o resultado indica o status atual do site consultado.

O disponibilidade por site é o percentual de vezes que cada site retornou Online. Ex.: se GitHub foi consultado 3 vezes e as 3 vezes retornou Online, então ele é 100%. Se BB foi consultado 3 vezes e nas 3 vezes foi dado como 'Problema', o percentual dele vai ser zerado.
BB, Claude.ai e Amazon aparecem como zerados não porque estão fora, mas pode ser algum bot de segurança esteja bloqueando nosso script.

O sites online indica a quantidade de sites que estão online, baseado na consulta do total de verificações. 

Das ferramentas: 

Utilizei Python pra montar a estrutura por trás da automação;
SQL pra criar as tabelas;
SQLite pra armazenar os dados localmente;
Grafana pra exibição das dashboards;
Biblioteca requests para fazer as requisições HTTP
Biblioteca pandas pra análise e manipulação dos dados
VS Code como ambiente de desenvolvimento

O monitor detecta automaticamente se um site retornou um código HTTP diferente de 200 e classifica como Problema ou Offline

Sites como BB, Claude.ai e Amazon retornam 403 (Acesso negado) — o site está no ar, mas bloqueia requisições automáticas.

Também utilizei Claude AI, Google Gemini e Perplexity pra resolução de dúvidas e apoio técnico.
