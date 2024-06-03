from django.http import HttpResponse
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import shutil
import uuid

def download_youtube_audio(request):
    if request.method == "GET":
        url = request.GET.get('url')
        start_time = float(request.GET.get('start_time'))
        end_time = float(request.GET.get('end_time'))

        # 임시 파일을 저장할 경로
        temp_dir = '/tmp'  # 적절한 경로로 변경하세요

        # 임시 파일 이름 생성
        temp_video_file = os.path.join(temp_dir, str(uuid.uuid4()) + '.mp4')
        temp_audio_file = os.path.join(temp_dir, str(uuid.uuid4()) + '.wav')

        try:
            yt = YouTube(url)
            video = yt.streams.filter().first()
            video.download(output_path=temp_dir, filename=os.path.basename(temp_video_file))

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

            response = HttpResponse(content=audio_bytes, content_type='audio/wav')
            response['Content-Disposition'] = 'attachment; filename="audio.wav"'
            return response
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_video_file):
                os.remove(temp_video_file)
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
