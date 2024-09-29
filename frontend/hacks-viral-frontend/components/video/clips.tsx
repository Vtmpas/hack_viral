import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import VideoPlayer from "@/components/video/video-player";

import Image from "next/image";
import WorflowImg01 from "@/public/images/workflow-01.png";

export default function Clips() {
  const [clips, setClips] = useState<{ url: string, meta: any }[]>([]);
  const [videoId, setVideoId] = useState<string | null>(null);

  useEffect(() => {
    console.log('useEffect called'); // Лог для проверки вызова useEffect

    const fetchClips = async () => {
      console.log('fetchClips function called'); // Лог для проверки вызова функции

      const storedVideoId = sessionStorage.getItem('videoId');
      const storedClipsNum = sessionStorage.getItem('clipsNum');
      if (storedVideoId && storedClipsNum) {
        console.log(`videoId: ${storedVideoId}`);
        console.log(`clipsNum: ${storedClipsNum}`);
        
        setVideoId(storedVideoId); // Устанавливаем videoId

        const clipsNum = parseInt(storedClipsNum, 10);
        const fetchedClips: { url: string, meta: any }[] = [];
        for (let i = 1; i <= clipsNum; i++) {
          const videoResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/part?videoId=${storedVideoId}&clipsNum=${i}`);
          const videoBlob = await videoResponse.blob();
          const videoUrl = URL.createObjectURL(videoBlob);

          const metaResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/meta?videoId=${storedVideoId}&clipsNum=${i}`);
          const meta = await metaResponse.json();

          console.log(`Metadata for clip ${i}:`, meta); // Логируем метаданные

          fetchedClips.push({ url: videoUrl, meta });
        }
        setClips(fetchedClips);
        console.log(`Number of fetched clips: ${fetchedClips.length}`);
      } else {
        console.log('VideoId or ClipsNum not found in sessionStorage');
      }
    };

    fetchClips();
  }, []);

  const handleDownload = () => {
    clips.forEach((clip, index) => {
      const link = document.createElement('a');
      link.href = clip.url;
      link.download = `${clip.meta.title || `clip_${index + 1}`}.mp4`; // Use title from metadata or fallback to default
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  };

  return (
    <section>
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="pb-12 md:pb-20">
          {/* Section header */}
          <div className="mx-auto max-w-3xl pb-12 text-center md:pb-20">
            <div
                className="inline-flex items-center gap-3 pb-3 before:h-px before:w-8 before:bg-gradient-to-r before:from-transparent before:to-indigo-200/50 after:h-px after:w-8 after:bg-gradient-to-l after:from-transparent after:to-indigo-200/50">
              <span
                  className="inline-flex bg-gradient-to-r from-indigo-500 to-indigo-200 bg-clip-text text-transparent">
                Пожилые цукаты и мисис
              </span>
            </div>
            <h2 className="animate-[gradient_6s_linear_infinite] bg-[linear-gradient(to_right,theme(colors.gray.200),theme(colors.indigo.200),theme(colors.gray.50),theme(colors.indigo.300),theme(colors.gray.200))] bg-[length:200%_auto] bg-clip-text pb-4 font-nacelle text-3xl font-semibold text-transparent md:text-4xl">
              Генерация виральных клипов
            </h2>
            <p className="text-lg text-indigo-200/65">
              Простой и элегантный интерфейс для быстрого начала работы с вертикальными видео. Сгенерируй яркий и
              запоминающийся контент за пару кликов.

            </p>
            <br />
            <br />
            {/* Buttons */}
            <div className="flex justify-center space-x-4 top-5">
              <div data-aos="fade-up" data-aos-delay={600}>
                <Link href="/"
                className="btn relative w-full bg-gradient-to-b from-gray-800 to-gray-800/60 bg-[length:100%_100%] bg-[bottom] text-gray-300 before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] hover:bg-[length:100%_150%] sm:w-auto"
                >
                    Обратно
                </Link>
              </div>
              <div data-aos="fade-up" data-aos-delay={400}>
                <a
                    className="btn group mb-4 w-full bg-gradient-to-t from-indigo-600 to-indigo-500 bg-[length:100%_100%] bg-[bottom] text-white shadow-[inset_0px_1px_0px_0px_theme(colors.white/.16)] hover:bg-[length:100%_150%] sm:mb-0 sm:w-auto"
                    href={`${process.env.NEXT_PUBLIC_EDITOR_URL}/video/editor?videoId=${videoId}&clipsNum=${clips.length}`}
                    target="_blank" // Открываем в новой вкладке
                    rel="noopener noreferrer" // Безопасность
                >
                  <span className="relative inline-flex items-center">
                    Редактировать клипы
                    <span
                        className="ml-1 tracking-normal text-white/50 transition-transform group-hover:translate-x-0.5">
                      -&gt;
                    </span>
                  </span>
                </a>
              </div>
              <div data-aos="fade-up" data-aos-delay={600}>
                <button
                    className="btn relative w-full bg-gradient-to-b from-gray-800 to-gray-800/60 bg-[length:100%_100%] bg-[bottom] text-gray-300 before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_right,theme(colors.gray.800),theme(colors.gray.700),theme(colors.gray.800))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] hover:bg-[length:100%_150%] sm:w-auto"
                    onClick={handleDownload}
                >
                  Скачать
                </button>
              </div>
            </div>
          </div>
          {/* Video grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {clips.map((clip, index) => (
            <a
                key={index} // Added key prop here
                className="group/card relative h-full overflow-hidden rounded-2xl bg-gray-800 p-px before:pointer-events-none before:absolute before:-left-40 before:-top-40 before:z-10 before:h-80 before:w-80 before:translate-x-[var(--mouse-x)] before:translate-y-[var(--mouse-y)] before:rounded-full before:bg-indigo-500/80 before:opacity-0 before:blur-3xl before:transition-opacity before:duration-500 after:pointer-events-none after:absolute after:-left-48 after:-top-48 after:z-30 after:h-64 after:w-64 after:translate-x-[var(--mouse-x)] after:translate-y-[var(--mouse-y)] after:rounded-full after:bg-indigo-500 after:opacity-0 after:blur-3xl after:transition-opacity after:duration-500 after:hover:opacity-20 before:group-hover:opacity-100"
                href="#0"
              >
                <div className="relative z-20 h-full overflow-hidden rounded-[inherit] bg-gray-950 after:absolute after:inset-0 after:bg-gradient-to-br after:from-gray-900/50 after:via-gray-800/25 after:to-gray-900/50">
                  {/* Arrow */}
                  <div
                    className="absolute right-6 top-6 flex h-8 w-8 items-center justify-center rounded-full border border-gray-700/50 bg-gray-800/65 text-gray-200 opacity-0 transition-opacity group-hover/card:opacity-100"
                    aria-hidden="true"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width={9}
                      height={8}
                      fill="none"
                    >
                      <path
                        fill="#F4F4F5"
                        d="m4.92 8-.787-.763 2.733-2.68H0V3.443h6.866L4.133.767 4.92 0 9 4 4.92 8Z"
                      />
                    </svg>
                  </div>
                  {/* Image */}
                  <div key={index} className="rounded-2xl overflow-hidden p-4">
                    <VideoPlayer
                        videoSrc={clip.url}
                        videoWidth={1920}
                        videoHeight={1080}
                    />
                  </div>
                  {/* Content */}
                  <h3 className="animate-[gradient_6s_linear_infinite] bg-[linear-gradient(to_right,theme(colors.gray.200),theme(colors.indigo.200),theme(colors.gray.50),theme(colors.indigo.300),theme(colors.gray.200))] bg-[length:200%_auto] bg-clip-text pb-4 font-nacelle text-xl font-semibold text-transparent md:text-2xl text-center">
                    {clip.meta.title}
                  </h3>
                  <div className="p-4">
                    <div className="mb-6 flex flex-wrap gap-1">
                      {clip.meta.hashtags && clip.meta.hashtags.map((hashtag: string, hashtag_index: number) => (
                        <span key={hashtag_index} className="mb-1 btn-sm relative rounded-full bg-gray-800/40 px-2.5 py-0.5 text-xs font-normal before:pointer-events-none before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-transparent before:[background:linear-gradient(to_bottom,theme(colors.gray.700/.15),theme(colors.gray.700/.5))_border-box] before:[mask-composite:exclude_!important] before:[mask:linear-gradient(white_0_0)_padding-box,_linear-gradient(white_0_0)] hover:bg-gray-800/60">
                          <span className="bg-gradient-to-r from-indigo-500 to-indigo-200 bg-clip-text text-transparent">
                            {hashtag}
                          </span>
                        </span>
                      ))}
                    </div>
                    <p className="text-indigo-200/65 mb-4">
                      <strong>Описание:</strong> {clip.meta.description}
                    </p>
                    <p className="text-indigo-200/65 mb-4">
                      <strong>Целевая аудитория:</strong> {clip.meta.target_audience}
                    </p>
                    <p className="text-indigo-200/65">
                      <strong>Настроение видео:</strong> {clip.meta.sentiment}
                    </p>
                  </div>
                </div>
            </a>
            )
          )}
          </div>
        </div>
      </div>
    </section>
  );
}