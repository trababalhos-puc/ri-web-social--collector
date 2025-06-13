import streamlit as st
import json
import os
import tempfile
import pandas as pd
import subprocess
import platform
import time
import logging

from service.index import Index
from service.transform import HTMLFileMapper

st.set_page_config(
    page_title="Navegador de Documentos IPEA",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

class IPEANavigator:
    def __init__(self):
        self.analyzer = None
        self.documents = {}
        self.json_data = {}

    def get_index_description(self, index_name):
        """Retorna descrição de cada tipo de índice"""
        descriptions = {
            "básico": {
                "titulo": "Básico",
                "descricao": "Processamento padrão com remoção de stopwords e stemming",
                "uso": "Bom para buscas gerais"
            },
            "sem_stopwords": {
                "titulo": "Sem Stopwords",
                "descricao": "Remove palavras comuns mas mantém palavras originais",
                "uso": "Ideal para termos específicos"
            },
            "com_stemming": {
                "titulo": "Com Stemming",
                "descricao": "Reduz palavras ao radical (casa, casas → cas)",
                "uso": "Encontra variações da mesma palavra"
            },
            "bigramas": {
                "titulo": "Bigramas",
                "descricao": "Indexa pares de palavras consecutivas",
                "uso": "Perfeito para nomes próprios e frases específicas"
            },
            "shingles": {
                "titulo": "Shingles (1-3 gramas)",
                "descricao": "Combina palavras individuais, bigramas e trigramas",
                "uso": "Busca flexível com contexto"
            }
        }
        return descriptions.get(index_name, {
            "titulo": index_name.title(),
            "descricao": "Índice personalizado",
            "uso": "Configuração específica"
        })

    def load_data(self, json_file_path):
        """Carrega os dados do arquivo JSON"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            return True
        except Exception as e:
            st.error(f"Erro ao carregar arquivo JSON: {e}")
            return False

    def initialize_index(self, json_file_path=None):
        """Inicializa o sistema de indexação"""
        try:
            if json_file_path is None:
                json_file_path = "html_files_map.json"

            if not os.path.exists(json_file_path):
                st.info("Arquivo de mapeamento não encontrado. Gerando...")
                import multiprocessing
                num_cpus = max(1, multiprocessing.cpu_count() // 2)
                st.info(f"Usando {num_cpus} processos paralelos")

                mapper = HTMLFileMapper(num_workers=num_cpus)
                result = mapper.run(extract_content=True)
                st.success(f"Mapeamento concluído: {mapper.output_file}")

            index_system = Index(json_file_path)
            self.analyzer = index_system.start()
            self.documents = index_system.documents

            if self.analyzer:
                self.analyzer.compare_indices()
                return True
            else:
                st.error("Não foi possível criar o analisador de índices.")
                return False

        except Exception as e:
            st.error(f"Erro ao inicializar índice: {e}")
            logging.error(f"Erro durante inicialização: {e}", exc_info=True)
            return False

    def get_full_path(self, doc_path):
        """Constrói o caminho completo do arquivo HTML"""
        try:
            data = self.json_data['ipea']
            path_parts = doc_path.split('/')

            current_data = data
            for part in path_parts:
                current_data = current_data.get(part, {})

            if isinstance(current_data, dict) and 'path' in current_data:
                return f"ipea/{current_data['path']}"
            return None
        except Exception as e:
            st.error(f"Erro ao construir caminho: {e}")
            return None

    def open_html_file(self, file_path):
        """Abre arquivo HTML no navegador padrão"""
        try:
            if os.path.exists(file_path):
                abs_path = os.path.abspath(file_path)

                if platform.system() == "Windows":
                    os.startfile(abs_path)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", abs_path])
                else:
                    subprocess.run(["xdg-open", abs_path])

                return True
            else:
                st.error(f"Arquivo não encontrado: {file_path}")
                return False
        except Exception as e:
            st.error(f"Erro ao abrir arquivo: {e}")
            return False

def main():
    st.title("Navegador de Documentos IPEA")
    st.markdown("---")

    if 'navigator' not in st.session_state:
        st.session_state.navigator = IPEANavigator()

    navigator = st.session_state.navigator

    with st.sidebar:
        st.header("Configurações")
        json_file_path = "html_files_map.json"

        if os.path.exists(json_file_path):
            st.success(f"Arquivo encontrado: {json_file_path}")

            if st.button("Inicializar Sistema"):
                with st.spinner("Carregando dados e criando índices..."):
                    if navigator.load_data(json_file_path):
                        if navigator.initialize_index(json_file_path):
                            st.success("Sistema inicializado com sucesso!")
                            st.session_state.system_ready = True
                        else:
                            st.error("Erro ao inicializar índices")
                    else:
                        st.error("Erro ao carregar dados")
        else:
            st.warning(f"Arquivo não encontrado: {json_file_path}")
            st.info("O arquivo será gerado automaticamente.")

            if st.button("Gerar Mapeamento e Inicializar"):
                with st.spinner("Gerando mapeamento... Pode demorar alguns minutos."):
                    if navigator.initialize_index():
                        st.success("Sistema inicializado com sucesso!")
                        st.session_state.system_ready = True
                    else:
                        st.error("Erro ao inicializar sistema")

            st.markdown("**Ou carregue manualmente:**")
            uploaded_file = st.file_uploader("Carregar arquivo JSON", type=['json'])

            if uploaded_file is not None:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                    json_content = json.loads(uploaded_file.read())
                    json.dump(json_content, tmp_file, ensure_ascii=False, indent=2)
                    tmp_file_path = tmp_file.name

                if st.button("Inicializar Sistema (Upload)"):
                    with st.spinner("Carregando dados..."):
                        if navigator.load_data(tmp_file_path):
                            if navigator.initialize_index(tmp_file_path):
                                st.success("Sistema inicializado!")
                                st.session_state.system_ready = True
                            else:
                                st.error("Erro ao inicializar")
                        else:
                            st.error("Erro ao carregar dados")

        if hasattr(st.session_state, 'system_ready') and st.session_state.system_ready:
            st.success("Sistema Ativo")
            if navigator.analyzer:
                st.metric("Documentos", len(navigator.documents))
                st.metric("Índices", len(navigator.analyzer.indices))

                with st.expander("Tipos de Índice"):
                    for idx_name in navigator.analyzer.indices.keys():
                        desc = navigator.get_index_description(idx_name)
                        st.markdown(f"**{desc['titulo']}**")
                        st.caption(desc['descricao'])
                        st.caption(f"Uso: {desc['uso']}")
                        st.divider()

    if hasattr(st.session_state, 'system_ready') and st.session_state.system_ready:
        st.header("Busca de Documentos")

        if navigator.analyzer and navigator.analyzer.indices:
            available_indices = list(navigator.analyzer.indices.keys())

            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                query = st.text_input(
                    "Digite sua consulta:",
                    placeholder="Ex: Eltis, David e David Richardson"
                )

            with col2:
                index_options = []
                index_mapping = {}

                for idx in available_indices:
                    desc = navigator.get_index_description(idx)
                    option_text = desc['titulo']
                    index_options.append(option_text)
                    index_mapping[option_text] = idx

                selected_option = st.selectbox("Tipo de índice:", index_options)
                selected_index = index_mapping[selected_option]

                desc = navigator.get_index_description(selected_index)
                st.caption(desc['descricao'])
                st.caption(f"Uso: {desc['uso']}")

            with col3:
                top_n = st.selectbox("Resultados:", [5, 10, 20, 50], index=0)

            if selected_index in navigator.analyzer.stats:
                stats = navigator.analyzer.stats[selected_index]

                with st.expander(f"Informações do índice '{selected_index}'"):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Vocabulário", f"{stats['vocabulary_size']:,}")
                    with col2:
                        st.metric("Termos/Doc", f"{stats['mean_terms_per_doc']:.1f}")
                    with col3:
                        st.metric("Tamanho", f"{navigator.analyzer.memory_usage[selected_index]/1024/1024:.1f} MB")
                    with col4:
                        st.metric("Tempo", f"{navigator.analyzer.times[selected_index]:.1f}s")

        if query:
            with st.spinner("Buscando..."):
                if selected_index:
                    selected_analyzer = navigator.analyzer.indices[selected_index]
                    processed_query = navigator.analyzer.processor.process_text(query)

                    start_time = time.time()
                    results = selected_analyzer.rank_search(processed_query["tokens"])[:top_n]
                    search_time = (time.time() - start_time) * 1000

                    if results:
                        st.subheader(f"Resultados - {selected_index}")
                        st.caption(f"Tempo: {search_time:.2f} ms | {len(results)} documentos")

                        results_data = []
                        for i, (doc_path, score) in enumerate(results):
                            full_path = navigator.get_full_path(doc_path)
                            results_data.append({
                                "Posição": i + 1,
                                "Documento": doc_path,
                                "Score": f"{score:.4f}",
                                "Caminho": full_path or "Não encontrado",
                                "Existe": "Sim" if full_path and os.path.exists(full_path) else "Não"
                            })

                        df = pd.DataFrame(results_data)
                        st.dataframe(df, use_container_width=True)

                        st.markdown("### Abrir Documentos")
                        cols = st.columns(min(len(results), 5))

                        for i, (doc_path, score) in enumerate(results[:5]):
                            full_path = navigator.get_full_path(doc_path)

                            with cols[i]:
                                if st.button(f"Doc {i+1}", key=f"{selected_index}_{i}"):
                                    if full_path and os.path.exists(full_path):
                                        if navigator.open_html_file(full_path):
                                            st.success(f"Abrindo: {os.path.basename(full_path)}")
                                        else:
                                            st.error("Erro ao abrir")
                                    else:
                                        st.error("Arquivo não encontrado")

                        if st.checkbox("Comparar com outros índices"):
                            st.markdown("---")
                            st.subheader("Comparação")

                            comparison_data = []
                            for idx_name, idx in navigator.analyzer.indices.items():
                                if idx_name != selected_index:
                                    start_time = time.time()
                                    comp_results = idx.rank_search(processed_query["tokens"])[:5]
                                    comp_time = (time.time() - start_time) * 1000

                                    comparison_data.append({
                                        "Índice": idx_name,
                                        "Documentos": len(comp_results),
                                        "Tempo (ms)": f"{comp_time:.2f}",
                                        "Melhor Score": f"{comp_results[0][1]:.4f}" if comp_results else "0.0000",
                                        "Top Doc": comp_results[0][0] if comp_results else "Nenhum"
                                    })

                            if comparison_data:
                                comp_df = pd.DataFrame(comparison_data)
                                st.dataframe(comp_df, use_container_width=True)

                    else:
                        st.warning(f"Nenhum documento encontrado para '{query}'")
                        st.info("Tente um índice diferente ou outros termos")

        if st.checkbox("Mostrar Estatísticas"):
            st.header("Estatísticas dos Índices")

            stats_data = []
            for name, stats in navigator.analyzer.stats.items():
                stats_data.append({
                    "Índice": name,
                    "Documentos": stats['num_documents'],
                    "Vocabulário": stats['vocabulary_size'],
                    "Termos/Doc": f"{stats['mean_terms_per_doc']:.2f}",
                    "Tamanho (MB)": f"{navigator.analyzer.memory_usage[name]/1024/1024:.2f}",
                    "Tempo (s)": f"{navigator.analyzer.times[name]:.2f}"
                })

            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True)

        if st.checkbox("Explorar Documentos"):
            st.header("Explorador de Documentos")

            col1, col2 = st.columns(2)

            with col1:
                dates = set()
                for doc_path in navigator.documents.keys():
                    if '/' in doc_path:
                        date_part = doc_path.split('/')[0]
                        dates.add(date_part)

                selected_date = st.selectbox("Filtrar por data:", ["Todas"] + sorted(list(dates)))

            with col2:
                text_filter = st.text_input("Filtrar por nome:", placeholder="Digite parte do nome")

            filtered_docs = navigator.documents.copy()

            if selected_date != "Todas":
                filtered_docs = {k: v for k, v in filtered_docs.items() if k.startswith(selected_date)}

            if text_filter:
                filtered_docs = {k: v for k, v in filtered_docs.items() if text_filter.lower() in k.lower()}

            st.info(f"Mostrando {len(filtered_docs)} de {len(navigator.documents)} documentos")

            for i, (doc_path, content) in enumerate(list(filtered_docs.items())[:20]):
                with st.expander(f"{doc_path}"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        preview = content[:200] + "..." if len(content) > 200 else content
                        st.text(preview)

                    with col2:
                        full_path = navigator.get_full_path(doc_path)
                        if full_path and os.path.exists(full_path):
                            if st.button("Abrir", key=f"open_{i}"):
                                navigator.open_html_file(full_path)
                                st.success("Arquivo aberto!")
                        else:
                            st.error("Não encontrado")

            if len(filtered_docs) > 20:
                st.info(f"Mostrando apenas os primeiros 20. Total: {len(filtered_docs)}")

    else:
        st.info("Configure o sistema na barra lateral para começar.")

        st.markdown("""
        ### Como usar:
        
        1. **Carregue o arquivo JSON** na barra lateral
        2. **Clique em "Inicializar Sistema"** para criar os índices
        3. **Escolha o tipo de índice** mais adequado
        4. **Digite sua consulta** na caixa de busca
        5. **Clique nos botões** para abrir os documentos
        
        ### Funcionalidades:
        
        - **Busca inteligente** com múltiplos tipos de índice
        - **Seleção de índice** para diferentes estratégias
        - **Estatísticas detalhadas** dos índices criados  
        - **Explorador de documentos** com filtros
        - **Abertura automática** dos arquivos HTML
        - **Ranking por relevância** usando TF-IDF
        - **Comparação entre índices** para análise
        
        ### Tipos de Índice:
        
        - **Básico**: Processamento padrão
        - **Sem Stopwords**: Remove palavras comuns
        - **Com Stemming**: Reduz palavras ao radical
        - **Bigramas**: Pares de palavras consecutivas
        - **Shingles**: Combina 1, 2 e 3 palavras
        
        **Dica**: Use "Sem Stopwords" para buscas gerais e "Bigramas" para frases específicas
        """)

if __name__ == "__main__":
    main()