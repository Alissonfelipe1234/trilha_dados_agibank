from huggingface_hub import snapshot_download
import os

# Define o nome da pasta onde vamos salvar
nome_pasta = "modelo_sentimento_offline"

print(f"📥 Baixando arquivos para a pasta: {nome_pasta} ...")

# O parâmetro 'local_dir' é o segredo. Ele baixa tudo para essa pasta.
path = snapshot_download(
    repo_id="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    local_dir=nome_pasta,
    local_dir_use_symlinks=False  # Importante: False para baixar os arquivos reais, não atalhos
)

print("✅ Download concluído! Copie a pasta 'modelo_sentimento_offline' para os alunos.")