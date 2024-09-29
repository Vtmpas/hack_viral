import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom'; // Import useLocation
import { Button } from '@/components/ui/button';
import {
  ADD_AUDIO,
  ADD_IMAGE,
  ADD_TEXT,
  ADD_VIDEO,
  dispatcher,
} from '@designcombo/core';
import { nanoid } from 'nanoid';
import { IMAGES } from '@/data/images';
import { DEFAULT_FONT } from '@/data/fonts';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { UploadIcon } from 'lucide-react';
import axios from 'axios';
import { ScrollArea } from '@/components/ui/scroll-area'; // Добавляем импорт ScrollArea

// Function to generate a thumbnail from a video URL
const generateThumbnail = (videoUrl: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    video.src = videoUrl;
    video.crossOrigin = 'anonymous';
    video.addEventListener('loadeddata', () => {
      video.currentTime = 0;
    });
    video.addEventListener('seeked', () => {
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      if (context) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/png');
        resolve(dataUrl);
      } else {
        reject('Failed to get canvas context');
      }
    });
    video.addEventListener('error', (error) => {
      reject(error);
    });
  });
};

export const Uploads = () => {
  const location = useLocation(); // Use useLocation to get the current URL
  const queryParams = new URLSearchParams(location.search);
  const videoId = queryParams.get('videoId') || '';
  const clipsNum = parseInt(queryParams.get('clipsNum') || '0', 10);

  const [videoUrls, setVideoUrls] = useState<string[]>([]);
  const [thumbnails, setThumbnails] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<string>('projects');

  // Отладочные сообщения для проверки параметров
  console.log('Parsed URL params:', { videoId, clipsNum });

  const handleAddImage = () => {
    dispatcher?.dispatch(ADD_IMAGE, {
      payload: {
        id: nanoid(),
        details: {
          src: IMAGES[4].src,
        },
      },
      options: {
        trackId: 'main',
      },
    });
  };

  const handleAddText = () => {
    dispatcher?.dispatch(ADD_TEXT, {
      payload: {
        id: nanoid(),
        details: {
          text: 'Heading',
          fontSize: 200,
          width: 900,
          fontUrl: DEFAULT_FONT.url,
          fontFamily: DEFAULT_FONT.postScriptName,
          color: '#ffffff',
          WebkitTextStrokeColor: 'green',
          WebkitTextStrokeWidth: '20px',
          textShadow: '30px 30px 100px rgba(255, 255, 0, 1)',
          wordWrap: 'break-word',
          wordBreak: 'break-all',
        },
      },
      options: {},
    });
  };

  const handleAddAudio = () => {
    dispatcher?.dispatch(ADD_AUDIO, {
      payload: {
        id: nanoid(),
        details: {
          src: 'https://ik.imagekit.io/snapmotion/timer-voice.mp3',
        },
      },
      options: {},
    });
  };

  const handleAddVideo = (src: string) => {
    dispatcher?.dispatch(ADD_VIDEO, {
      payload: {
        id: nanoid(),
        details: {
          src,
        },
        metadata: {
          resourceId: src,
        },
      },
      options: {
        trackId: 'main',
      },
    });
  };

  const fetchVideo = async (videoId: string, clipNum: number) => {
    try {
      const response = await axios.get(`http://195.242.25.2:8009/api/part`, {
        params: {
          videoId,
          clipsNum: clipNum,
        },
        responseType: 'blob', // Указываем, что ожидаем Blob
      });
      console.log('Fetch video response:', response); // Log the response to inspect its structure
      return response.data;
    } catch (error) {
      console.error('Error fetching video:', error);
      return null;
    }
  };

  const handleFetchAndAddVideos = async (videoId: string, clipsNum: number) => {
    try {
      console.log(`Fetching videos for videoId: ${videoId} with clipsNum: ${clipsNum}`);
      const urls: string[] = [];
      const thumbnailPromises: Promise<string>[] = [];
      for (let i = 1; i <= clipsNum; i++) {
        const videoBlob = await fetchVideo(videoId, i);
        if (videoBlob) {
          const videoUrl = URL.createObjectURL(videoBlob);
          urls.push(videoUrl);
          thumbnailPromises.push(generateThumbnail(videoUrl));
        } else {
          console.error('Invalid video data for clip:', i);
        }
      }
      setVideoUrls(urls);
      const generatedThumbnails = await Promise.all(thumbnailPromises);
      setThumbnails(generatedThumbnails);
    } catch (error) {
      console.error('Error in handleFetchAndAddVideos:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'projects') {
      console.log('Active tab is projects');
      handleFetchAndAddVideos(videoId, clipsNum);
    }
  }, [activeTab, videoId, clipsNum]);

  return (
    <div className="flex-1">
      <div className="text-md text-text-primary font-medium h-12  flex items-center px-4">
        Your media
      </div>
      <ScrollArea className="h-[calc(100%-3rem)] px-4"> {/* Ограничиваем высоту и добавляем прокрутку */}
        <div>
          <Tabs defaultValue="projects" className="w-full" onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-1">
              <TabsTrigger value="projects">Project</TabsTrigger>
            </TabsList>
            <TabsContent value="projects">
              <div className="flex flex-col gap-4 mt-4">
                {thumbnails.map((thumbnail, index) => (
                  <div key={index} className="cursor-pointer" onClick={() => handleAddVideo(videoUrls[index])}>
                    <img src={thumbnail} alt={`Video preview ${index + 1}`} className="w-full h-auto" />
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </ScrollArea>
      <div className="fixed left-0 top-1/2 transform -translate-y-1/2">
        <Button
          onClick={() => {
            setActiveTab('uploads');
          }}
          className="flex gap-2"
          size="sm"
          variant="secondary"
        >
          <UploadIcon size={16} /> Upload
        </Button>
      </div>
    </div>
  );
};