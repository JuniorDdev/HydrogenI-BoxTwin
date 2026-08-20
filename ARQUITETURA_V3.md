# Arquitetura BoxTwin v3

## Fluxo operacional

1. O sensor real ou simulado produz uma matriz 8×8.
2. O serviço de volume calcula ocupação, altura, confiança e zonas válidas.
3. O motor de regras identifica capacidade alta, baixa confiança e obstrução.
4. A leitura e as anomalias são gravadas no SQLite.
5. O painel recebe a nova leitura por SSE (`GET /api/stream`).
6. Adaptadores opcionais enviam e-mail ou Twilio com intervalo antirrepetição.
7. O administrador registra ciência e consulta a tratativa no RAG local.

## API preparada para Flutter

| Método | Rota | Uso |
|---|---|---|
| GET | `/api/health` | estado e dimensões do BoxNode |
| GET | `/api/readings/latest` | leitura mais recente |
| GET | `/api/readings/history` | série histórica |
| GET | `/api/stream` | eventos em tempo real |
| GET | `/api/admin/anomalies` | fila protegida de incidentes |
| POST | `/api/admin/anomalies/{id}/acknowledge` | registro de ciência |
| POST | `/api/admin/assistant` | consulta ao RAG |

Para o aplicativo Flutter, a etapa seguinte deverá substituir a sessão web nas rotas móveis por JWT de curta duração, HTTPS obrigatório e armazenamento seguro do token. Não exponha diretamente o Raspberry Pi na internet; utilize um backend central ou VPN/túnel autenticado.

## IA e RAG

A base inicial fica em `boxtwin/knowledge/procedures.json`. O serviço recupera documentos por relevância lexical e devolve as fontes utilizadas. Essa abordagem funciona offline e é adequada ao MVP. Na evolução, o mesmo contrato pode usar embeddings, um banco vetorial e um modelo de linguagem; mantenha sempre as fontes, os limites de decisão e a aprovação humana para ações operacionais.

Quando `GROQ_ENABLED=true`, o Groq recebe a pergunta, o histórico recente da conversa, os dados técnicos da anomalia e somente os procedimentos recuperados. Se houver timeout, indisponibilidade ou chave inválida, a resposta volta automaticamente ao modo `local-rag`.

## Respostas pelo Twilio

- `1 42`: registra ciência da anomalia 42;
- `2 42`: marca a anomalia 42 como em atendimento;
- `3 42`: marca a anomalia 42 como resolvida.

Os webhooks validam `X-Twilio-Signature` quando `TWILIO_VALIDATE_SIGNATURE=true`.

## Segurança antes de publicar

- Alterar `ADMIN_PASSWORD` e `SECRET_KEY`.
- Guardar `.env` fora do GitHub.
- Usar HTTPS e cookies seguros em produção.
- Criar usuários individuais e trilha de auditoria na próxima fase.
- Não permitir que a IA acione máquinas ou descarte alertas automaticamente.
- Usar credenciais de teste do Twilio antes de habilitar mensagens reais.

## Validação

```powershell
pip install -r requirements.txt
pytest -q
python app.py
```

Teste em Android na mesma rede acessando `http://IP_DO_COMPUTADOR:5000`. Em produção, utilize HTTPS.
