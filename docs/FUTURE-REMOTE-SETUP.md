# Future Remote — configuração e compilação

Este fork é a base de desenvolvimento do cliente Future Remote para uso interno da Future Soluções.

## Identidade visual

O projeto SPC Vision contém a logo PNG em `public/logo-future.png` e também versões SVG em `public/logo-future-black.svg` e `public/logo-future-white.svg`. Antes de incorporar assets ao cliente RustDesk, conferir contraste, transparência e dimensões; não presumir que a URL pública do CRM seja um caminho de arquivo local do repositório.

## Servidor self-hosted

- ID / rendezvous server: `future-remote.duckdns.org`
- Relay server: `future-remote.duckdns.org:21117`
- Chave pública do servidor: `NgQBktnunnDC45ZaFZX9w1fixGsGD8Wb9J0WB94niB8=`
- API Server: deixe vazio no servidor OSS, salvo se uma API própria compatível for configurada.

A chave acima é **pública**. Nunca publicar ou colocar em workflows a chave privada `id_ed25519` do servidor.

## Configuração do cliente

O fork fixa `libs/hbb_common` no commit `edefa08b798b7fbf70b274a4cdbf701c9e06f7a3`. Nessa versão, `RENDEZVOUS_SERVERS` e `RS_PUB_KEY` são constantes de compilação. Não presumir que variáveis de ambiente alterem essas constantes.

O script `scripts/configure_future_remote.py` aplica a configuração do servidor de forma reproduzível e estrita: ele falha se a estrutura das declarações upstream mudar e confirma o resultado. O script altera apenas o checkout local do submódulo; não altera o commit do submódulo no Git nem a VPS. O workflow `Future Remote - client configuration validation` verifica o pin do submódulo e valida o diff.

## Etapas de entrega

1. Validar o patch das constantes do servidor.
2. Definir nome do aplicativo, identidade visual, ícones e metadados por plataforma sem remover avisos legítimos ou atribuições/licenças upstream.
3. Compilar primeiro Windows x64; inspecionar logs e artefatos antes de ampliar para macOS Intel/Apple Silicon.
4. Investigar Windows 32 bits separadamente; não prometer artefato até existir alvo compatível.
5. Testar em duas máquinas que os clientes apontam para o servidor Future Remote e que a conexão funciona.

## Limitações e segurança

- A validação de configuração não equivale a uma compilação nem a um teste de conexão.
- Não remover indiscriminadamente chamadas da API oficial para suprimir uma mensagem. Primeiro identificar a origem do aviso.
- Uso interno não elimina automaticamente obrigações da licença upstream.
- Não incluir chaves privadas, tokens ou secrets no código, logs ou artefatos públicos.
- Nenhuma configuração da VPS é alterada por estes scripts/workflows.
