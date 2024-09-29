import { ScrollArea } from '@/components/ui/scroll-area';
import { VIDEOS } from '@/data/video';
import { ADD_VIDEO, dispatcher } from '@designcombo/core';
import { nanoid } from 'nanoid';

import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { UploadIcon } from 'lucide-react';

import { useRef } from 'react'; // Импортируем useRef для создания рефа

export const Videos = () => {
  const fileInputRef = useRef<HTMLInputElement>(null); // Создаем реф для input

  const handleUploadClick = () => {
    fileInputRef.current?.click(); // Кликаем на скрытый input при нажатии кнопки
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const src = URL.createObjectURL(file);
      handleAddVideo(src);
    }
  };

  const handleAddVideo = (src: string) => {
    dispatcher?.dispatch(ADD_VIDEO, {
      payload: {
        id: nanoid(),
        details: {
          src: src,
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

  return (
    <div className="flex-1 flex flex-col">
      <div className="text-md flex-none text-text-primary font-medium h-12  flex items-center px-4">
        Videos
      </div>
      <div>
          <Tabs defaultValue="projects" className="w-full">
              <Button
                onClick={handleUploadClick}
                className="flex gap-2 w-full"
                size="sm"
                variant="secondary"
              >
                <UploadIcon size={16} /> Upload
                <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
              </Button>
            <TabsContent value="projects"></TabsContent>
          </Tabs>
        </div>
      <ScrollArea>
        <div className="px-4 masonry-sm">
          {VIDEOS.map((image, index) => {
            return (
              <div
                onClick={() => handleAddVideo(image.src)}
                key={index}
                className="flex items-center justify-center w-full  bg-zinc-950 pb-2 overflow-hidden cursor-pointer"
              >
                <img
                  src={image.preview}
                  className="w-full h-full object-cover rounded-md"
                  alt="image"
                />
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
};
