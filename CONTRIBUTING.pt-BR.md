# Contribuindo para TAG

🇺🇸 [Read in English](CONTRIBUTING.md)

Obrigado por considerar contribuir com TAG. Este documento fornece diretrizes para contribuições.

## Como Contribuir

1. **Fork o Repositório**
   ```bash
   git clone https://github.com/manoanzi/tag.git
   cd tag
   ```

2. **Crie uma Branch**
   ```bash
   git checkout -b feature/minha-contribuicao
   ```

3. **Faça suas Alterações**
   - Siga os princípios TAG rigorosamente
   - Adicione testes para novos exemplos
   - Use type hints em todas as funções

4. **Commit suas Mudanças**
   ```bash
   git commit -m "Add: descrição da contribuição"
   ```

5. **Push para sua Branch**
   ```bash
   git push origin feature/minha-contribuicao
   ```

6. **Abra um Pull Request**
   - Descreva claramente o que foi alterado
   - Referencie issues relacionadas
   - Aguarde revisão

## Áreas de Contribuição

- Exemplos práticos em Python
- Patterns de teste avançados
- Melhorias na documentação
- Templates e ferramentas de geração de estrutura
- Tutoriais e guias

## Diretrizes de Código

- Use Python 3.11+
- Siga PEP 8
- Use type hints em todas as funções e retornos
- Código funcional e imutável
- snake_case para todos os arquivos e módulos

## Princípios TAG

Todas as contribuições devem seguir os 9 princípios fundamentais:

1. **Protocols definem contratos**: abstrações de infraestrutura via `typing.Protocol`
2. **Domains são schemas, nunca funções**: entidades imutáveis com Pydantic
3. **Logics são puras e concentram as decisões**: sem IO, aleatoriedade, relógio ou `Result`; toda regra e ramificação fica aqui e devolve um schema de domínio
4. **Adapters transformam estruturas**: conversões entre camadas sem efeitos colaterais, inclusive de schemas para `Result`
5. **Gateways fazem IO**: acesso externo via Protocols recebidos como parâmetro
6. **Flows são pipelines de orquestração**: da entrada bruta ao schema de resposta, incluindo o log de negócio
7. **Handlers só repassam**: entrada do transporte para um Flow, schema de resposta de volta
8. **Drivers implementam Protocols**: encapsulam bibliotecas externas fora de `src/`
9. **Efeitos colaterais nas bordas**: IO, aleatoriedade e tempo ficam atrás de Protocols, acessados por Gateways e implementados por Drivers

## Processo de Revisão

1. Mantenedor revisa o PR
2. Discussão e ajustes se necessário
3. Aprovação e merge
4. Atualização do CHANGELOG

## Código de Conduta

Este projeto segue o [Código de Conduta](CODE_OF_CONDUCT.pt-BR.md). Ao participar, você concorda em respeitar estes termos.

## Dúvidas?

Abra uma [issue](https://github.com/manoanzi/tag/issues) para discussão.

---

**Obrigado por contribuir com TAG.**
