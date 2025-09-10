
# 🧾 AttachValidator

**AttachValidator** é um sistema automatizado de validação de comprovantes de pagamento, desenvolvido em Python, com suporte a OCR (Reconhecimento Óptico de Caracteres), utilizado para validação de comprovantes de pagamento em solicitações de workflow.  

O objetivo do projeto é automatizar a verificação de anexos (PDFs ou imagens) em solicitações de sistemas internos, garantindo que o documento anexado seja realmente um comprovante válido antes de prosseguir no fluxo, verificando se o anexo atende a critérios como:

- Valor do pagamento (ex: R$30,00)
- Destinatário correto (ex: empresa Lev)
- Validade da data (últimos 5 dias úteis)

---

## 📌 Objetivo

Automatizar o processo de verificação de comprovantes enviados por usuários para reduzir erros humanos e aumentar a eficiência do fluxo de trabalho interno.

---

## 🚀 Tecnologias Utilizadas

- **Python 3.10+**
- `Selenium` — automação de navegação no sistema WorkBank Virtual  
- `Pytesseract` — OCR via Tesseract para leitura de textos em imagens e PDFs  
- `PDF2Image` — conversão de páginas de PDFs para imagem  
- `OpenPyXL` — geração de planilhas Excel com os dados validados  
- `re` — expressões regulares para extrair datas, nomes, valores etc.

---

## O que faz o Script:
   - Login no sistema
   - Acessa o menu de workflow buscando a página de solicitações
   - Filtra solicitações com os bancos: `CLICKLEV` e `CLICKPOWER`
   - Verifica se há anexo de comprovante (PDF ou imagem)
   - Executa OCR no anexo
   - Valida: valor, destinatário, CNPJ, data (últimos 5 dias), nome do pagador
   - Gera uma planilha Excel com os comprovantes válidos

---

## 📤 Saída

A saída é uma planilha `.xlsx` com os comprovantes válidos, contendo:

| data   | valor  | detalhes                               | codigo |
|--------|--------|----------------------------------------|--------|
| 10/09  | R$30,00| 10/09 23:59 JOÃO DA SILVA              | 12345  |
| ...    | ...    | ...                                    | ...    |

---

## 🔍 Regras de Validação

- **Valor:** Deve ser R$30,00 (com tolerância para OCRs como "3O,OO", "30OO", etc.)
- **Destinatário:** Contém o nome "Lev", CNPJ e banco corretos
- **Data:** Dentro dos últimos 5 dias corridos
- **Nome:** Nome completo com pelo menos 2 palavras (e.g. "Maria Souza")

---

## ⚠️ Observações

- Não salva anexos no disco — os arquivos são analisados diretamente em memória.
- Suporta múltiplos layouts de comprovantes (Pagbank, PicPay, Santander etc.)
- O OCR é sensível à qualidade do anexo — imagens borradas podem gerar falsos negativos.

---

## 📌 Futuras melhorias

- Interface gráfica (GUI) para facilitar o uso, sem precisar rodar scripts
- Testes automatizados para validação dos critérios

---

## 👨‍💻 Autor

Desenvolvido por **Vinicius Ávila**  
[GitHub](https://github.com/viniciusavila1)
[Linkedin](https://linkedin.com/in/vinicius-avila)