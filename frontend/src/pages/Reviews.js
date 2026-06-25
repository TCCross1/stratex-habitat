import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageWrap, Stars } from "@/components/Primitives";
import { BadgeCheck } from "lucide-react";

export default function Reviews() {
  const { data } = useQuery({ queryKey: ["reviews"], queryFn: async () => (await api.get("/reviews")).data });
  return (
    <PageWrap title="Reviews & Ratings" subtitle="Native STRATEX-verified reviews carry the most scoring weight.">
      <div className="space-y-3 max-w-3xl">
        {data?.length === 0 && <div className="text-sm text-[#71717a]">No reviews yet.</div>}
        {data?.map((r) => (
          <div key={r.id} className="panel rounded-md p-4" data-testid={`review-${r.id}`}>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-white">{r.title}</span>
              <Stars rating={r.rating} />
            </div>
            <p className="text-[12px] text-[#a1a1aa] mt-1">{r.body}</p>
            <div className="text-[11px] text-teal mt-2 flex items-center gap-1">
              <BadgeCheck size={12} /> {r.author_name} · {r.source === "stratex_verified" ? "STRATEX Verified" : "External Source"}
            </div>
          </div>
        ))}
      </div>
    </PageWrap>
  );
}
