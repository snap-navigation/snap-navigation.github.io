// Only one demonstration plays at a time.
const videos = document.querySelectorAll('video');
videos.forEach((video) => {
  // Hide the usual right-click save menu; this cannot prevent media retrieval.
  video.addEventListener('contextmenu', (event) => event.preventDefault());
  video.addEventListener('play', () => {
    videos.forEach((other) => {
      if (other !== video) other.pause();
    });
  });
});
