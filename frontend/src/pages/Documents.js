import { useRef } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, formatApiError } from "@/lib/api";
import { PageWrap } from "@/components/Primitives";
import { Button } from "@/components/ui/button";
import { FileText, Upload, Download } from "lucide-react";
import { toast } from "sonner";

export default function Documents() {
  const qc = useQueryClient();
  const fileRef = useRef();
  const { data } = useQuery({ queryKey: ["documents"], queryFn: async () => (await api.get("/documents")).data });

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const fd = new FormData(); fd.append("file", file);
    try {
      await api.post("/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      toast.success(`Uploaded ${file.name}`);
      qc.invalidateQueries({ queryKey: ["documents"] });
    } catch (e) { toast.error(formatApiError(e.response?.data?.detail)); }
  };

  return (
    <PageWrap title="Documents" subtitle="Property documents stored in your secure AWS record."
      action={<>
        <input ref={fileRef} type="file" className="hidden" onChange={onUpload} data-testid="doc-file-input" />
        <Button data-testid="upload-doc-btn" onClick={() => fileRef.current?.click()} className="gap-1 font-semibold" style={{ background: "#14f1d9", color: "#050505" }}>
          <Upload size={16} /> Upload
        </Button>
      </>}>
      <div className="space-y-2 max-w-2xl">
        {data?.map((d) => (
          <div key={d.id} className="panel rounded-md p-3 flex items-center gap-3" data-testid={`doc-${d.id}`}>
            <div className="w-9 h-9 rounded grid place-items-center bg-[#1a1a1e]"><FileText size={16} className="text-teal" /></div>
            <div className="flex-1"><div className="text-sm text-white">{d.name}</div><div className="text-[11px] text-[#71717a]">{d.size}</div></div>
            <Download size={15} className="text-[#71717a]" />
          </div>
        ))}
      </div>
    </PageWrap>
  );
}
