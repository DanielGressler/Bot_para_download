import yt_dlp
from youtubesearchpython import VideosSearch

def buscar_e_obter_url_youtube(nome_video):
    """
    Busca um vídeo no YouTube pelo nome e tenta obter sua URL direta de stream.

    Args:
        nome_video (str): O nome do vídeo que você deseja pesquisar.

    Returns:
        str: A URL direta do vídeo (ou a URL de stream, dependendo da disponibilidade),
             ou None se não for possível encontrar ou obter a informação.
    """
    print(f"\n[DEBUG] Tentando buscar vídeo: '{nome_video}'")
    try:
        videos_search = VideosSearch(nome_video, limit=1)
        result = videos_search.result()

        if not result['result']:
            print(f"  [INFO] Nenhum vídeo encontrado para '{nome_video}'.")
            return None

        video_id = result['result'][0]['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"  [INFO] URL do YouTube encontrada para '{nome_video}': {video_url}")

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'noplaylist': True,
            'quiet': True,
            'simulate': True,
            'force_print_json': True,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            extra_info = ydl.extract_info(video_url, download=False)
            
            if 'url' in extra_info:
                print(f"  [DEBUG] yt-dlp encontrou URL direta: {extra_info['url'][:50]}...") # Mostra só o começo da URL
                return extra_info['url']
            elif 'formats' in extra_info:
                for f in extra_info['formats']:
                    if 'url' in f and 'ext' in f and (f['ext'] == 'mp4' or f['ext'] == 'webm'):
                        print(f"  [DEBUG] yt-dlp encontrou URL em formatos: {f['url'][:50]}...")
                        return f['url']
            
            print(f"  [INFO] yt-dlp não conseguiu encontrar uma URL de stream direta para '{nome_video}'.")
            return None

    except Exception as e:
        print(f"  [ERRO] Ocorreu um erro ao processar '{nome_video}': {e}")
        return None

if __name__ == "__main__":
    nomes_dos_videos = []
    
    print("--- Bot de Extração de URLs do YouTube ---")
    print("Digite os nomes dos vídeos um por um. Digite 'fim' (sem aspas) quando terminar.")
    print("[DEBUG] Iniciando loop de entrada de nomes.")

    while True:
        nome = input("Digite o nome de um vídeo: ")
        print(f"[DEBUG] Você digitou: '{nome}'") # Adicionado para ver o input
        if nome.lower().strip() == 'fim': # Adicionado .strip() para remover espaços extras
            print("[DEBUG] 'fim' detectado. Saindo do loop de entrada.")
            break
        if nome.strip():
            nomes_dos_videos.append(nome.strip())
            print(f"[DEBUG] Adicionado '{nome.strip()}' à lista. Lista atual: {nomes_dos_videos}")
        else:
            print("[INFO] Nome do vídeo não pode ser vazio. Tente novamente.")

    print(f"\n[DEBUG] Loop de entrada finalizado. Nomes a processar: {nomes_dos_videos}")

    if not nomes_dos_videos:
        print("\nNenhum vídeo foi inserido para busca. Encerrando.")
    else:
        print("\n--- Processando as buscas... ---")
        for nome_video_individual in nomes_dos_videos:
            print(f"\n[DEBUG] Chamando buscar_e_obter_url_youtube para '{nome_video_individual}'")
            url_direta = buscar_e_obter_url_youtube(nome_video_individual)
            if url_direta:
                print(f"\n  **URL Direta de Stream para '{nome_video_individual}':** {url_direta}")
                print("  (Atenção: Estas URLs de stream são temporárias e podem expirar rapidamente.)")
            else:
                print(f"\n  Não foi possível obter a URL direta para '{nome_video_individual}'.")
        print("\n--- Processamento Concluído! ---")