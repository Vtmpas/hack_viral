import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { IMAGES } from '@/data/images';
import { ADD_IMAGE, dispatcher } from '@designcombo/core';
import { nanoid } from 'nanoid';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { UploadIcon } from 'lucide-react';
import { useRef } from 'react';

export const Images = () => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleAddImage = (src: string) => {
    dispatcher?.dispatch(ADD_IMAGE, {
      payload: {
        id: nanoid(),
        details: {
          src: src,
        },
      },
      options: {
        trackId: 'main',
      },
    });
  };

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        handleAddImage(result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <div className="text-md flex-none text-text-primary font-medium h-12  flex items-center px-4">
        Изображения
      </div>
      <div className="px-4">
        <div>
          <Tabs defaultValue="projects" className="w-full">
              <Button
                onClick={handleUploadClick}
                className="flex gap-2 w-full"
                size="sm"
                variant="secondary"
              >
                <UploadIcon size={16} /> Загрузить
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
      </div>
      <ScrollArea>
        <div className="px-4 masonry-sm">
          {IMAGES.map((image, index) => {
            return (
              <div
                onClick={() => handleAddImage(image.src)}
                key={index}
                className="flex items-center justify-center w-full h-full bg-zinc-950 pb-2 overflow-hidden cursor-pointer"
              >
                <img
                  src={image.src}
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

function modifyImageUrl(url: string): string {
  const uploadIndex = url.indexOf('/upload');
  if (uploadIndex === -1) {
    throw new Error('Invalid URL: /upload not found');
  }

  const modifiedUrl =
    url.slice(0, uploadIndex + 7) +
    '/w_0.05,c_scale' +
    url.slice(uploadIndex + 7);
  return modifiedUrl;
}
