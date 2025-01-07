import React, { useEffect } from "react";

function CameraFeed({ videoRef }) {
  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error("Error accessing camera:", error);
      }
    };

    startCamera();
  }, [videoRef]);

  return (
    <div style={{ flex: 1 }}>
      <h2 style={{ margin: 0, padding: "10px 0" }}>Live Camera Feed</h2>
      <video
        ref={videoRef}
        autoPlay
        style={{ height: "calc(100% - 40px)", width: "100%" }}
      ></video>
    </div>
  );
}

export default CameraFeed;
