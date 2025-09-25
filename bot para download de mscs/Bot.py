import yt_dlp
from youtubesearchpython import VideosSearch
import os # Importa a biblioteca os para manipulação de arquivos/pastas

# O restante do código, incluindo a verificação do requests no início, permanece o mesmo.
# Se a sua seção de 'Diagnóstico de Ambiente' não está mais dando erro, pode removê-la.

def buscar_e_obter_url_youtube(nome_video, download_mp3=False): # Adiciona um novo parâmetro
    """
    Busca um vídeo no YouTube pelo nome e, opcionalmente, converte e baixa em MP3.

    Args:
        nome_video (str): O nome do vídeo que você deseja processar.
        download_mp3 (bool): Se True, tentará baixar e converter o vídeo para MP3.

    Returns:
        str: A URL direta do vídeo (se download_mp3 for False),
             ou o caminho do arquivo MP3 baixado (se download_mp3 for True e bem-sucedido),
             ou None em caso de falha.
    """
    print(f"\n[DEBUG] Tentando processar vídeo: '{nome_video}'")
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
            'format': 'bestaudio/best', # Baixa apenas a melhor faixa de áudio
            'noplaylist': True,
            'quiet': True,
            'proxy': None, # Mantemos o proxy desativado para evitar o problema anterior

            # --- OPÇÕES PARA CONVERSÃO E DOWNLOAD EM MP3 ---
            'extractaudio': True,       # Extrai o áudio do vídeo
            'audioformat': "mp3",       # Define o formato de áudio para mp3
            'outtmpl': os.path.join('downloads_mp3', '%(title)s.%(ext)s'), # Pasta e nome do arquivo de saída
            'writedescription': False,  # Opcional: não salva a descrição
            'postprocessors': [{        # Pós-processador para converter o áudio
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # Qualidade do MP3 (192kbps)
            }],
            # --- FIM DAS OPÇÕES DE MP3 ---

            'simulate': not download_mp3, # Simula se download_mp3 é False
            'skip_download': not download_mp3, # Pula download se download_mp3 é False
        }

        # Cria a pasta de downloads se ela não existir
        if download_mp3 and not os.path.exists('downloads_mp3'):
            os.makedirs('downloads_mp3')
            print("  [INFO] Pasta 'downloads_mp3' criada.")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            if download_mp3:
                print(f"  [INFO] Iniciando download e conversão para MP3 de '{nome_video}'...")
                # O yt-dlp retornará informações sobre o arquivo baixado
                info_dict = ydl.extract_info(video_url, download=True)
                # O caminho do arquivo baixado pode ser obtido de _filename
                downloaded_file_path = ydl.prepare_filename(info_dict)
                print(f"  [SUCESSO] MP3 baixado para: {downloaded_file_path}")
                return downloaded_file_path # Retorna o caminho do arquivo MP3
            else:
                print(f"  [INFO] Apenas obtendo URL de stream (sem download) para '{nome_video}'...")
                info_dict = ydl.extract_info(video_url, download=False)
                if 'url' in info_dict:
                    print(f"  [DEBUG] yt-dlp encontrou URL direta: {info_dict['url'][:50]}...")
                    return info_dict['url']
                elif 'formats' in info_dict:
                    for f in info_dict['formats']:
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
    
    print("--- Bot de Extração/Download de Músicas do YouTube ---")
    print("Digite os nomes dos vídeos/músicas um por um. Digite 'fim' quando terminar.")
    print("[DEBUG] Iniciando loop de entrada de nomes.")

    while True:
        nome = input("Digite o nome de uma música/vídeo: ")
        print(f"[DEBUG] Você digitou: '{nome}'")
        if nome.lower().strip() == 'fim':
            print("[DEBUG] 'fim' detectado. Saindo do loop de entrada.")
            break
        if nome.strip():
            nomes_dos_videos.append(nome.strip())
            print(f"[DEBUG] Adicionado '{nome.strip()}' à lista. Lista atual: {nomes_dos_videos}")
        else:
            print("[INFO] Nome do vídeo não pode ser vazio. Tente novamente.")

    print(f"\n[DEBUG] Loop de entrada finalizado. Nomes a processar: {nomes_dos_videos}")

    if not nomes_dos_videos:
        print("\nNenhuma música/vídeo inserido para processamento. Encerrando.")
    else:
        # Pergunta ao usuário se ele quer apenas a URL ou quer baixar o MP3
        modo_operacao = input("\nDeseja apenas a URL (U) ou baixar o MP3 (M)? (U/M): ").lower().strip()
        
        realizar_download_mp3 = (modo_operacao == 'm')

        print(f"\n--- Processando as buscas e {'downloads' if realizar_download_mp3 else 'extração de URLs'} ---")
        
        # O yt-dlp precisa do FFmpeg para a conversão de áudio.
        # Ele tentará encontrar o FFmpeg no PATH do sistema.
        # Se você não o tem, baixe-o de https://ffmpeg.org/download.html
        # e adicione a pasta 'bin' do FFmpeg ao seu PATH do sistema.
        if realizar_download_mp3:
            print("\nATENÇÃO: Para download em MP3, você precisa ter o FFmpeg instalado e no PATH do sistema.")
            print("  Se o download falhar, baixe em https://ffmpeg.org/download.html e adicione a pasta 'bin' ao PATH.")
            
        for nome_video_individual in nomes_dos_videos:
            resultado = buscar_e_obter_url_youtube(nome_video_individual, download_mp3=realizar_download_mp3)
            
            if realizar_download_mp3:
                if resultado:
                    print(f"  **MP3 de '{nome_video_individual}' foi baixado para:** {resultado}")
                else:
                    print(f"  Falha ao baixar MP3 para '{nome_video_individual}'.")
            else: # Apenas extração de URL
                if resultado:
                    print(f"  **URL Direta de Stream para '{nome_video_individual}':** {resultado}")
                    print("  (Atenção: Estas URLs de stream são temporárias e podem expirar rapidamente.)")
                else:
                    print(f"  Não foi possível obter a URL direta para '{nome_video_individual}'.")
        print("\n--- Processamento Concluído! ---")