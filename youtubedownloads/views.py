from django.http import HttpResponse, JsonResponse
from pytubefix import YouTube
from moviepy.editor import VideoFileClip
import os
import uuid
import requests

def download_youtube_audio(request):
    if request.method == "GET":
        url = request.GET.get('url')
        start_time = request.GET.get('from')
        end_time = request.GET.get('to')

        if not url:
            return JsonResponse({'error': 'Missing url'}, status=400)
        
        if not start_time:
            return JsonResponse({'error': 'Missing start_time'}, status=400)
        
        if not end_time:
            return JsonResponse({'error': 'Missing end_time'}, status=400)

        print("url: {0}".format(url))
        print("from: {0}".format(start_time))
        print("to: {0}".format(end_time))

        # 임시 파일을 저장할 경로
        temp_dir = '/tmp'  # 적절한 경로로 변경하세요

        # 임시 파일 이름 생성
        temp_video_file = os.path.join(temp_dir, str(uuid.uuid4()) + '.mp4')
        temp_audio_file = os.path.join(temp_dir, str(uuid.uuid4()) + '.wav')

        try:
            yt = YouTube(url, use_po_token=True)
            # 오디오 스트림만 필터링하여 다운로드
            video = yt.streams.filter(only_audio=True).first()

            if not video:
                return JsonResponse({'error': 'No audio stream available for this video'}, status=400)

            video.download(output_path=temp_dir, filename=os.path.basename(temp_video_file))
            print("download success")

            # 비디오 파일 열기
            clip = VideoFileClip(temp_video_file)

            # 비디오의 총 시간 가져오기
            total_duration = clip.duration

            # end_time이 비디오의 총 시간을 초과할 경우 총 시간으로 설정
            if end_time > total_duration:
                end_time = total_duration

            # 비디오의 일부분을 오디오로 추출하여 저장
            audio_clip = clip.subclip(start_time, end_time).audio
            audio_clip.write_audiofile(temp_audio_file)
            audio_clip.close()

            with open(temp_audio_file, 'rb') as audio_file:
                audio_bytes = audio_file.read()

            # 외부 서버로 오디오 파일을 전송
            url = "https://model-o5rcbmo3sq-du.a.run.app/predict"
            files = {"file": open(temp_audio_file, 'rb')}
            response = requests.post(url, files=files)

            # 서버 응답을 그대로 반환
            if response.status_code == 200:
                return HttpResponse(content=response.content, content_type='application/json')
            else:
                return JsonResponse({'error': 'Failed to process the audio file on the external server'}, status=500)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        finally:
            # 임시 파일 삭제
            try:
                if os.path.exists(temp_video_file):
                    os.remove(temp_video_file)
                if os.path.exists(temp_audio_file):
                    os.remove(temp_audio_file)
            except Exception as e:
                print(f"Error deleting temporary files: {str(e)}")
                
