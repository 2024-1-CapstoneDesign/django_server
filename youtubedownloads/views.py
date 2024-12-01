from django.http import HttpResponse, JsonResponse
from pytubefix import YouTube
from pytubefix.cli import on_progress
from moviepy.video.io.VideoFileClip import VideoFileClip
import tempfile
import uuid
import requests


def download_youtube_audio(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Only GET method is allowed'}, status=405)

    url = request.GET.get('url')
    start_time = request.GET.get('from')
    end_time = request.GET.get('to')

    if not url:
        return JsonResponse({'error': 'Missing url'}, status=400)
    if not start_time or not end_time:
        return JsonResponse({'error': 'Missing start_time or end_time'}, status=400)

    try:
        start_time = float(start_time)
        end_time = float(end_time)
    except ValueError:
        return JsonResponse({'error': 'Invalid start_time or end_time'}, status=400)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 임시 파일 생성
            temp_video_file = f"{temp_dir}/{uuid.uuid4()}.mp4"
            temp_audio_file = f"{temp_dir}/{uuid.uuid4()}.wav"

            # YouTube 영상 다운로드
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback=on_progress)
            audio_stream = yt.streams.get_audio_only()
            audio_stream.download(output_path=temp_dir, filename=temp_video_file.split('/')[-1])
            print("영상 다운로드 완료")

            # 비디오 파일 열기 및 오디오 추출
            clip = VideoFileClip(temp_video_file)
            end_time = min(end_time, clip.duration)  # 종료 시간이 영상 길이를 초과하지 않도록 제한

            # 비디오에서 지정 구간 오디오 추출 및 저장
            audio_clip = clip.subclip(start_time, end_time).audio
            audio_clip.write_audiofile(temp_audio_file)
            audio_clip.close()
            clip.close()
            print("오디오 추출 및 저장 완료")

            # 외부 서버로 오디오 파일 전송
            with open(temp_audio_file, 'rb') as audio_file:
                response = requests.post(
                    "https://model-o5rcbmo3sq-du.a.run.app/predict",
                    files={"file": audio_file}
                )

            # 외부 서버 응답 처리
            if response.status_code == 200:
                return HttpResponse(content=response.content, content_type='application/json')
            else:
                return JsonResponse({'error': 'Failed to process the audio file on the external server'}, status=500)

    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
