import { useEffect, useState } from "react";

// Detects device class + interaction mode and reacts to resize / orientation.
function compute() {
  if (typeof window === "undefined") return { type: "desktop", isPhone: false, isTablet: false, isDesktop: true, touch: false, orientation: "landscape" };
  const w = window.innerWidth;
  const touch = window.matchMedia("(pointer: coarse)").matches || "ontouchstart" in window;
  const orientation = w >= window.innerHeight ? "landscape" : "portrait";
  let type = "desktop";
  if (w < 768) type = "phone";
  else if (w < 1024) type = "tablet";
  return { type, isPhone: type === "phone", isTablet: type === "tablet", isDesktop: type === "desktop", touch, orientation, width: w };
}

export function useDevice() {
  const [device, setDevice] = useState(compute);
  useEffect(() => {
    let raf;
    const onResize = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => setDevice(compute())); };
    window.addEventListener("resize", onResize);
    window.addEventListener("orientationchange", onResize);
    return () => { window.removeEventListener("resize", onResize); window.removeEventListener("orientationchange", onResize); cancelAnimationFrame(raf); };
  }, []);
  return device;
}
