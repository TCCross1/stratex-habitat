import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { popBack } from "@/lib/navHistory";

export default function BackButton() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const home = user?.role === "contractor" ? "/marketplace" : "/twin";

  const goBack = () => {
    const prev = popBack();
    navigate(prev || home);
  };

  return (
    <button
      onClick={goBack}
      data-testid="global-back-btn"
      aria-label="Go back"
      className="fixed left-3 z-[60] flex items-center gap-1.5 rounded-full border border-[#27272a]
        bg-[#0a0a0bee] backdrop-blur px-3.5 py-2 text-[13px] text-[#a1a1aa] shadow-lg
        hover:text-teal hover:border-teal transition-colors active:scale-95
        bottom-[calc(4.5rem+env(safe-area-inset-bottom))] md:bottom-4"
    >
      <ArrowLeft size={16} /> Back
    </button>
  );
}

