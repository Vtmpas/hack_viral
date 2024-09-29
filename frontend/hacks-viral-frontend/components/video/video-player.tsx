import React, { useRef, useEffect } from 'react';

interface VideoPlayerProps {
  videoSrc: string;
  videoWidth: number;
  videoHeight: number;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoSrc, videoWidth, videoHeight }) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
    }
  }, [videoSrc]);

  return (
    <video
      ref={videoRef}
      className="w-full h-auto rounded-2xl z-50 relative"
      width={videoWidth}
      height={videoHeight}
      controls
    >
      <source src={videoSrc} type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  );
};

export default VideoPlayer;