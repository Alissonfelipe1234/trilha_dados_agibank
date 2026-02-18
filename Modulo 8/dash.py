import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from database_setup import engine, Livro, Categoria, Usuario, Venda, Emprestimo

# 1. Configuração da Página
st.set_page_config(page_title="Agiteca Tech", layout="wide", page_icon="heart")

# 2. Função para Carregar Dados (Com Cache para não travar o banco)
@st.cache_data(ttl=60) # Atualiza a cada 1 minuto
def carregar_livros():
    stmt = select(
        Livro.id, 
        Livro.nome, 
        Livro.autor, 
        Livro.preco, 
        Livro.quantidade, 
        Categoria.genero
    ).join(Categoria, Livro.id_categoria == Categoria.id)
    
    return pd.read_sql(stmt, engine)

# --- SIDEBAR (NAVEGAÇÃO) ---
st.sidebar.title("Menu")
menu = st.sidebar.radio("Ir para:", ["Dashboard", "Catálogo", "Cadastrar Livro", "Cadastrar Usuário", "Vendas", "Empréstimos"])

# --- ÁREA 1: DASHBOARD ---
if menu == "Dashboard":
    st.title("Dashboard da Livraria")
    df = carregar_livros()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Títulos", len(df))
    col2.metric("Valor em Estoque", f"R$ { (df['preco'] * df['quantidade']).sum():,.2f}")
    col3.metric("Mediana de Preços", f"R$ {df['preco'].median():.2f}")
    
    st.divider()
    
    st.subheader("Distribuição por Gênero")
    contagem_genero = df['genero'].value_counts()
    st.bar_chart(contagem_genero)

# --- ÁREA 2: CATÁLOGO ---
elif menu == "Catálogo":
    st.title("Livros Disponíveis")
    df = carregar_livros()
    
    busca = st.text_input("Pesquisar por nome do livro:")
    generos = ["Todos"] + list(df['genero'].unique())
    filtro_gen = st.selectbox("Filtrar por Gênero:", generos)
    
    df_filtrado = df.copy()
    if busca:
        df_filtrado = df_filtrado[df_filtrado['nome'].str.contains(busca, case=False)]
    if filtro_gen != "Todos":
        df_filtrado = df_filtrado[df_filtrado['genero'] == filtro_gen]
        
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

# --- ÁREA 3: CADASTRAR LIVRO (CRUD) ---
elif menu == "Cadastrar Livro":
    st.title("Adicionar Novo Exemplar")
    
    with st.form("form_cadastro"):
        nome = st.text_input("Nome do Livro")
        autor = st.text_input("Autor")
        preco = st.number_input("Preço (R$)", min_value=0.0, step=0.01)
        qtd = st.number_input("Quantidade", min_value=0, step=1)
        
        with Session(engine) as session:
            cats = session.query(Categoria).all()
            dict_cats = {c.genero: c.id for c in cats}
            escolha_cat = st.selectbox("Gênero", options=list(dict_cats.keys()))
        
        btn_salvar = st.form_submit_button("Salvar no Banco")
        
        if btn_salvar:
            with Session(engine) as session:
                novo = Livro(
                    nome=nome, autor=autor, preco=preco, 
                    quantidade=qtd, id_categoria=dict_cats[escolha_cat],
                    sinopse="Cadastrado via WebApp", isbn="AUTO-GEN"
                )
                session.add(novo)
                session.commit()
                st.success(f"Livro '{nome}' cadastrado com sucesso!")
                st.balloons()

# --- ÁREA 4: CADASTRAR USUÁRIO ---
elif menu == "Cadastrar Usuário":
    st.title("Cadastro de Novos Clientes")
    
    with st.form("form_usuario"):
        nome = st.text_input("Nome Completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        btn_usuario = st.form_submit_button("Cadastrar Cliente")
        
        if btn_usuario:
            if not nome or not email or not senha:
                st.error("Por favor, preencha todos os campos.")
            else:
                try:
                    with Session(engine) as session:
                        novo_usuario = Usuario(
                            nome=nome,
                            email=email,
                            senha=senha  # Em um app real, aqui deveria haver hash da senha
                        )
                        session.add(novo_usuario)
                        session.commit()
                        st.success(f"Usuário '{nome}' cadastrado com sucesso!")
                        st.balloons()
                except Exception as e:
                    st.error(f"Erro ao cadastrar: E-mail já existe ou erro no banco.")

# --- ÁREA 5: VENDAS ---
elif menu == "Vendas":
    st.title("Registrar Venda")
    
    with Session(engine) as session:
        livros = session.query(Livro).filter(Livro.quantidade > 0).all()
        usuarios = session.query(Usuario).all()
        
        dict_livros = {f"{l.nome} (Qtd: {l.quantidade})": l for l in livros}
        dict_usuarios = {f"{u.nome} ({u.email})": u for u in usuarios}
        
    if not livros:
        st.warning("Não há livros em estoque para venda.")
    elif not usuarios:
        st.warning("Não há usuários cadastrados.")
    else:
        with st.form("form_venda"):
            escolha_livro_str = st.selectbox("Selecione o Livro", options=list(dict_livros.keys()))
            escolha_usuario_str = st.selectbox("Selecione o Cliente", options=list(dict_usuarios.keys()))
            qtd_venda = st.number_input("Quantidade", min_value=1, step=1)
            
            btn_venda = st.form_submit_button("Finalizar Venda")
            
            if btn_venda:
                livro_obj = dict_livros[escolha_livro_str]
                usuario_obj = dict_usuarios[escolha_usuario_str]
                
                if qtd_venda > livro_obj.quantidade:
                    st.error(f"Estoque insuficiente! Disponível: {livro_obj.quantidade}")
                else:
                    try:
                        with Session(engine) as session:
                            # Re-busca o livro na sessão atual para garantir integridade
                            l = session.get(Livro, livro_obj.id)
                            nova_venda = Venda(id_livro=l.id, id_usuario=usuario_obj.id, quantidade=qtd_venda)
                            l.quantidade -= qtd_venda
                            
                            session.add(nova_venda)
                            session.commit()
                            st.success(f"Venda de '{l.nome}' registrada com sucesso!")
                            st.balloons()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao processar venda: {e}")

# --- ÁREA 6: EMPRÉSTIMOS ---
elif menu == "Empréstimos":
    st.title("Registrar Empréstimo")
    
    with Session(engine) as session:
        livros = session.query(Livro).filter(Livro.quantidade > 0).all()
        usuarios = session.query(Usuario).all()
        
        dict_livros = {f"{l.nome} (Disponível: {l.quantidade})": l for l in livros}
        dict_usuarios = {f"{u.nome} ({u.email})": u for u in usuarios}

    if not livros:
        st.warning("Não há livros disponíveis para empréstimo.")
    elif not usuarios:
        st.warning("Não há usuários cadastrados.")
    else:
        with st.form("form_emprestimo"):
            escolha_livro_str = st.selectbox("Livro", options=list(dict_livros.keys()))
            escolha_usuario_str = st.selectbox("Cliente", options=list(dict_usuarios.keys()))
            dt_devolucao = st.date_input("Data de Devolução Prevista")
            
            btn_emprestimo = st.form_submit_button("Confirmar Empréstimo")
            
            if btn_emprestimo:
                livro_obj = dict_livros[escolha_livro_str]
                usuario_obj = dict_usuarios[escolha_usuario_str]
                
                try:
                    with Session(engine) as session:
                        l = session.get(Livro, livro_obj.id)
                        novo_emp = Emprestimo(
                            id_livro=l.id, 
                            id_usuario=usuario_obj.id, 
                            dt_devolucao_prevista=dt_devolucao,
                            devolvido=False
                        )
                        l.quantidade -= 1 # Retira 1 do estoque
                        
                        session.add(novo_emp)
                        session.commit()
                        st.success(f"Empréstimo de '{l.nome}' para {usuario_obj.nome} realizado!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao processar empréstimo: {e}")