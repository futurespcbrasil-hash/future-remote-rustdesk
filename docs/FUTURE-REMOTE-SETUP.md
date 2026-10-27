# Future Remote — configuração e compilação

Este fork é a base de desenvolvimento do cliente Future Remote para uso interno da Future Soluções.

## Identidade visual

O projeto SPC Vision contém a logo PNG em `public/logo-future.png` e também versões SVG em `public/logo-future-black.svg` e `public/logo-future-white.svg`. Antes de incorporar assets ao cliente RustDesk, conferir contraste, transparência e dimensões; não presumir que a URL pública do CRM seja um caminho de arquivo local do repositório.

## Servidor self-hosted

- ID / rendezvous server: `future-remote.duckdns.org`
- Relay server: `future-remote.duckdns.org:21117`
- Chave pública do servidor: `NgQBktnunnDC45ZaFZX9w1fixGsGD8Wb9J0WB94niB8=`
- API Server: deixe vazio para o servidor OSS, salvo se futuramente for configurada uma API própria compatível.

A chave acima é a chave **pública**. Nunca publicar ou colocar em workflows a chave privada `id_ed25519` do servidor.

## Configuração do cliente — validação do código

O fork fixa o submódulo `libs/hbb_common` no commit `edefa08b798b7fbf70b274a4cdbf701c9e06f7a3`. Nesse commit, `src/config.rs` define `RENDEZVOUS_SERVERS` e `RS_PUB_KEY` como constantes de compilação. Portanto, **não usar como fato as variáveis de ambiente `RENDEZVOUS_SERVER` e `RS_PUB_KEY`**: elas não foram confirmadas como mecanismo de configuração nessa versão.

Próximo passo técnico: fazer a alteração mínima e revisável nas constantes do submódulo fixado (ou criar uma atualização de submódulo controlada), definir `APP_NAME`/identidade visual nos pontos suportados pelo projeto e só então preparar o workflow de build. Incluir submódulos ao clonar: `git submodule update --init --recursive`.

## Plano de entrega

1. Validar a versão fixada do submódulo e o mecanismo de configuração.
2. Integrar a marca Future Remote sem remover atribuições/licenças upstream.
3. Configurar e executar build para Windows x64 e macOS Intel/Apple Silicon.
4. Investigar Windows 32 bits separadamente; não prometer esse artefato até existir um alvo de compilação compatível.
5. Validar em duas máquinas que os clientes usam o servidor Future Remote e que a conexão funciona.

## Avisos

- Não remover indiscriminadamente chamadas da API oficial para tentar suprimir uma mensagem. Primeiro identificar a origem do aviso; configurar o servidor próprio e remover uma verificação de aviso são coisas diferentes.
- O uso interno não elimina automaticamente as obrigações da licença do projeto upstream.
- Não incluir chaves privadas, tokens ou secrets no código, nos logs ou em artefatos públicos.
- Não alterar a configuração da VPS como parte do build do cliente.
