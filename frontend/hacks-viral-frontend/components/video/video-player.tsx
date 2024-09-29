import React from 'react';

interface VideoPlayerProps {
  videoSrc: string;
  videoWidth: number;
  videoHeight: number;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoSrc, videoWidth, videoHeight }) => {
  return (
    <video
      className="w-full h-auto rounded-2xl"
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