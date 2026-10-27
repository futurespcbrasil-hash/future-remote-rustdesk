# Future Remote — configuração e compilação

Este fork é a base de desenvolvimento do cliente Future Remote para uso interno da Future Soluções.

## Servidor self-hosted

- ID / rendezvous server: `future-remote.duckdns.org`
- Relay server: `future-remote.duckdns.org:21117` (o servidor anuncia o relay padrão automaticamente quando aplicável)
- Chave pública do servidor: `NgQBktnunnDC45ZaFZX9w1fixGsGD8Wb9J0WB94niB8=`
- API Server: deixe vazio para o servidor OSS, salvo se futuramente for configurada uma API própria compatível.

A chave acima é a chave **pública**. Nunca publicar ou colocar em workflows a chave privada `id_ed25519` do servidor.

## Estratégia de build

O cliente RustDesk aceita os parâmetros de servidor personalizados durante a compilação através das variáveis `RENDEZVOUS_SERVER` e `RS_PUB_KEY`. As duas devem ser definidas juntas:

```bash
export RENDEZVOUS_SERVER="future-remote.duckdns.org"
export RS_PUB_KEY="NgQBktnunnDC45ZaFZX9w1fixGsGD8Wb9J0WB94niB8="
```

A compilação precisa incluir os submódulos Git (`git submodule update --init --recursive`). Neste fork, `libs/hbb_common` é um submódulo; por isso, não presuma que `libs/hbb_common/src/config.rs` seja um arquivo versionado diretamente neste repositório. Confirme a versão e o estado do submódulo antes de editar o código.

## Plano de entrega

1. Validar o submódulo e o mecanismo de configuração na versão fixada pelo fork.
2. Configurar o build para Windows x64 e macOS Intel/Apple Silicon.
3. Executar os workflows e corrigir erros de build antes de distribuir.
4. Investigar Windows 32 bits separadamente; não prometer esse artefato até existir um alvo de compilação compatível.
5. Validar em duas máquinas que os clientes usam o servidor Future Remote e que a conexão funciona.

## Avisos

- Não se deve remover indiscriminadamente chamadas da API oficial para tentar suprimir uma mensagem. Primeiro identifique de onde vem o aviso; configurar o servidor próprio e remover uma verificação de aviso são coisas diferentes.
- Preserve os avisos de licença e atribuição exigidos pelo projeto upstream. O uso interno não elimina automaticamente as obrigações da licença.
- Não inclua chaves privadas, tokens ou secrets no código, nos logs ou em artefatos públicos.
- Não altere a configuração da VPS como parte do build do cliente.
