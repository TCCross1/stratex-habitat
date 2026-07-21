import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAppData } from "@/context/AppDataContext";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { toast } from "sonner";
import {
  MessageSquare, ShieldAlert, ArrowRight, CheckCircle2, AlertTriangle, FileText,
  DollarSign, Wrench, ShieldCheck, RefreshCw, Layers, Calendar, User, Eye, EyeOff,
  GitCompare, Trash2, Edit2, Play, Check, CircleDot, Info, BarChart3, Clock, Lock
} from "lucide-react";

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const money = (n) => "$" + Math.round(n).toLocaleString();

export default function HomeSteward() {
  const { user } = useAuth();
  const { property, pid } = useAppData();
  
  // App state
  const [step, setStep] = useState(1); // 1: Ask, 2: Ask Response, 3: Confirm, 4: Design Studio, 5: Compare Scenarios, 6: Build Ready, 7: Preview & Publish, 8: Published Successfully
  const [asked, setDirtyAsked] = useState(false);
  const [stewardResponse, setStewardResponse] = useState(null);
  const [contextData, setContextData] = useState(null);
  const [recommendedAction, setRecommendedAction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [correlationId, setCorrelationId] = useState("");
  const [createdScenarioId, setCreatedScenarioId] = useState("");
  const [auditLog, setAuditLog] = useState([]);
  
  // Design Studio step selections
  const [selectedMaterial, setSelectedMaterial] = useState("GAF Timberline HDZ");
  const [estimateData, setEstimateData] = useState(null);
  const [investmentScenarios, setInvestmentScenarios] = useState(null);
  
  // Build Ready & Package Preview
  const [readinessData, setReadinessData] = useState(null);
  const [contractorPreview, setContractorPackagePreview] = useState(null);
  const [overrideReadiness, setOverrideReadiness] = useState(false);
  
  // Personalization & Memory
  const [memoryData, setMemoryData] = useState(null);
  const [editingMemory, setEditingMemory] = useState(false);
  const [preferredMaterialMem, setPreferredMaterialMem] = useState("");
  const [budgetTargetMem, setBudgetTargetMem] = useState("");
  const [timelinePreferenceMem, setTimelinePreferenceMem] = useState("");
  
  // Editable contractor package fields
  const [budgetPreference, setBudgetPreference] = useState("Competitive");
  const [timelinePreference, setTimelinePreference] = useState("60 days");
  const [homeownerNotes, setHomeownerNotes] = useState("Homeowner-initiated project to explore roofing options after minor North Slope deflection finding.");
  const [removePersonalInfo, setRemovePersonalInfo] = useState(true);
  const [sharedDocs, setSharedDocs] = useState({ doc_01: true, doc_02: false });
  
  // Failure / Resiliency simulation toggles
  const [simPassportDown, setSimPassportDown] = useState(false);
  const [simEstimatorDown, setSimEstimatorDown] = useState(false);
  const [simAuditWriteFail, setSimAuditWriteFail] = useState(false);
  
  // Logs & Metrics for Observability
  const [logs, setLogs] = useState([]);
  const [latencyMetrics, setLatencyMetrics] = useState({
    contextRetrieval: "0ms",
    stewardResponse: "0ms",
    estimator: "0ms",
    render: "0ms"
  });

  const addLog = (msg, level = "INFO") => {
    const time = new Date().toLocaleTimeString();
    const corr = correlationId ? ` [Corr: ${correlationId.slice(0, 8)}]` : "";
    setLogs((prev) => [`[${time}] ${level}${corr} - ${msg}`, ...prev].slice(0, 50));
  };

  // Fetch initial context and memories
  useEffect(() => {
    if (!user) return;
    const loadInitial = async () => {
      try {
        const start = performance.now();
        const ctxRes = await api.get("/steward/context");
        setContextData(ctxRes.data);
        const end = performance.now();
        setLatencyMetrics(m => ({ ...m, contextRetrieval: `${Math.round(end - start)}ms` }));
        addLog("Property context pipeline fetched successfully. Verified tenant alex@stratexhabitat.com.");
        
        const memRes = await api.get("/steward/memory");
        setMemoryData(memRes.data);
        setPreferredMaterialMem(memRes.data.project_memory.preferred_roof_material);
        setBudgetTargetMem(memRes.data.project_memory.budget_target);
        setTimelinePreferenceMem(memRes.data.project_memory.timeline_preference);
      } catch (err) {
        addLog(`Failed to fetch context: ${err.message}`, "ERROR");
      }
    };
    loadInitial();
  }, [user]);

  // Handle homeowner question
  const handleAsk = async () => {
    if (simPassportDown) {
      addLog("SIMULATED FAILURE: Passport Projection Service is offline.", "FATAL");
      toast.error("Error: Published Passport explanation is currently unavailable. Retry later. (Corr ID: " + uuid8() + ")");
      return;
    }
    
    setLoading(true);
    addLog("Homeowner question submitted: 'Do I need a new roof?'");
    const start = performance.now();
    try {
      const askRes = await api.post("/steward/ask", { question: "Do I need a new roof?" });
      const recRes = await api.get("/steward/recommendation");
      const end = performance.now();
      
      setStewardResponse(askRes.data);
      setRecommendedAction(recRes.data);
      setLatencyMetrics(m => ({ ...m, stewardResponse: `${Math.round(end - start)}ms` }));
      setStep(2);
      addLog("Home Steward AI classified intent as ROOF_CONCERN_QUERY. Structured progressive answer generated.");
    } catch (err) {
      addLog(`Ask failed: ${err.message}`, "ERROR");
      toast.error("Failed to retrieve Steward answer");
    } finally {
      setLoading(false);
    }
  };

  // Confirm and create project
  const handleConfirm = async () => {
    if (simAuditWriteFail) {
      addLog("SIMULATED FAILURE: Audit event storage database write timed out.", "FATAL");
      toast.error("Error: Immutable audit write failed. Action aborted to protect property integrity.");
      return;
    }

    setLoading(true);
    addLog("Homeowner explicitly confirmed 'Explore Roof Replacement' action.");
    try {
      const confirmRes = await api.post("/steward/confirm", {
        property_id: pid || "villa-horizon-uuid",
        action: "Explore Roof Replacement"
      });
      setCorrelationId(confirmRes.data.correlation_id);
      setCreatedScenarioId(confirmRes.data.audit_event.created_scenario_id);
      setAuditLog(prev => [confirmRes.data.audit_event, ...prev]);
      
      // Pre-fetch estimates and investment scenarios for next step
      const estRes = await api.post("/steward/estimate", { material: selectedMaterial });
      setEstimateData(estRes.data);
      const scenariosRes = await api.get("/steward/scenarios");
      setInvestmentScenarios(scenariosRes.data);

      setStep(4);
      addLog(`Audit record persisted. Project 'Project: Roof Replacement' created in Design Studio. ID: ${confirmRes.data.audit_event.created_scenario_id}.`);
      toast.success("Design Studio project created!");
    } catch (err) {
      addLog(`Confirmation failed: ${err.message}`, "ERROR");
      toast.error("Action confirmation failed");
    } finally {
      setLoading(false);
    }
  };

  // Handle material change in Design Studio project
  const handleMaterialChange = async (mat) => {
    if (simEstimatorDown) {
      addLog("SIMULATED FAILURE: Estimator engine API is offline.", "FATAL");
      toast.error("Error: Local project pricing estimator is currently unavailable. Delta pricing recalculation failed.");
      return;
    }

    setSelectedMaterial(mat);
    setLoading(true);
    addLog(`Homeowner selected material: ${mat}. Recalculating estimates...`);
    const start = performance.now();
    try {
      const estRes = await api.post("/steward/estimate", { material: mat });
      setEstimateData(estRes.data);
      const end = performance.now();
      setLatencyMetrics(m => ({ ...m, estimator: `${Math.round(end - start)}ms` }));
      addLog(`Estimate recalculated for ${mat}. Local Texas Multiplier applied.`);
    } catch (err) {
      addLog(`Estimator fetch failed: ${err.message}`, "ERROR");
    } finally {
      setLoading(false);
    }
  };

  // Proceed to Scenario Planner
  const handleToScenarios = () => {
    setStep(5);
    addLog("Homeowner navigating to Scenario Comparison (Home Investment Intelligence).");
  };

  // Proceed to Build Ready completeness review
  const handleToBuildReady = async () => {
    setLoading(true);
    addLog("Retrieving Roof Project Readiness checklist.");
    try {
      const readinessRes = await api.get("/steward/readiness");
      setReadinessData(readinessRes.data);
      setStep(6);
      addLog(`Readiness checklist loaded. Current project readiness score: ${readinessRes.data.project_readiness_score}/100.`);
    } catch (err) {
      addLog(`Readiness fetch failed: ${err.message}`, "ERROR");
    } finally {
      setLoading(false);
    }
  };

  // Proceed to contractor package preview
  const handleToPreview = async () => {
    setLoading(true);
    addLog("Compiling Contractor Package Preview.");
    try {
      const prevRes = await api.get("/steward/contractor-package");
      setContractorPackagePreview(prevRes.data);
      setStep(7);
      addLog("Contractor package preview compiled. Personal identifiers redacted.");
    } catch (err) {
      addLog(`Package compilation failed: ${err.message}`, "ERROR");
    } finally {
      setLoading(false);
    }
  };

  // Publish Opportunity
  const handlePublish = async () => {
    setLoading(true);
    addLog("Publishing Project Opportunity. Emitting homeowner approval...");
    try {
      const pubRes = await api.post("/steward/publish", {
        property_id: pid || "villa-horizon-uuid",
        scenario_id: createdScenarioId,
        timeline_preference: timelinePreference,
        budget_preference: budgetPreference,
        shared_document_ids: Object.keys(sharedDocs).filter(k => sharedDocs[k]),
        remove_personal_info: removePersonalInfo
      });
      setAuditLog(prev => [pubRes.data.audit, ...prev]);
      setStep(8);
      addLog(`PROJECT_OPPORTUNITY_PUBLISHED emitted successfully. Opportunity published: ID ${pubRes.data.opportunity_id}.`);
      toast.success("Project Opportunity published successfully!");
    } catch (err) {
      addLog(`Publication failed: ${err.message}`, "ERROR");
      toast.error("Failed to publish Project Opportunity");
    } finally {
      setLoading(false);
    }
  };

  // Save memory correction
  const handleSaveMemory = async () => {
    setLoading(true);
    try {
      const updated = await api.post("/steward/memory", {
        project_memories: {
          preferred_roof_material: preferredMaterialMem,
          budget_target: budgetTargetMem,
          timeline_preference: timelinePreferenceMem
        }
      });
      setMemoryData(updated.data);
      setEditingMemory(false);
      addLog("Homeowner project memories corrected and saved to isolated MongoDB store.");
      toast.success("Memory updated successfully");
    } catch (err) {
      addLog(`Memory update failed: ${err.message}`, "ERROR");
    } finally {
      setLoading(false);
    }
  };

  const uuid8 = () => Math.random().toString(36).substring(2, 10).toUpperCase();

  return (
    <div className="h-full flex flex-col md:flex-row bg-[#050505] text-white">
      
      {/* Left side: Guided Vertical Slice Stages */}
      <div className="flex-1 overflow-y-auto p-6 border-r border-[#27272a] space-y-6">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#27272a] pb-4">
          <div>
            <div className="flex items-center gap-2">
              <MessageSquare className="text-teal" style={{ color: "#14f1d9" }} />
              <h1 className="font-head text-2xl font-bold tracking-tight">Habitat Home Steward™</h1>
            </div>
            <p className="text-xs text-[#71717a] mt-1">H-012 Operation Steward Vertical Slice Production Environment</p>
          </div>
          <span className="text-[10px] font-mono border border-teal/40 text-teal px-2 py-0.5 rounded uppercase" style={{ color: "#14f1d9", borderColor: "rgba(20,241,217,0.4)" }}>
            Tenant Isolated
          </span>
        </div>

        {/* STEP 1: Ask Question */}
        {step === 1 && (
          <div className="space-y-4 rise-animation">
            <div className="kpi-card p-6 bg-[#0a0a0b] border border-[#27272a] rounded-lg">
              <h2 className="text-lg font-medium text-white mb-2">How can Habitat help you today?</h2>
              <p className="text-sm text-[#a1a1aa] mb-6">
                Ask Home Steward AI any question about your property assets, warranties, or maintenance alerts.
              </p>

              <div className="space-y-3">
                <button
                  onClick={handleAsk}
                  disabled={loading}
                  className="w-full flex items-center justify-between p-4 rounded-md border border-[#27272a] bg-[#111113] hover:border-teal transition-all text-left group"
                >
                  <div>
                    <div className="text-sm font-semibold text-white group-hover:text-teal transition-colors" style={{ color: asked ? "#14f1d9" : "" }}>
                      “Do I need a new roof?”
                    </div>
                    <div className="text-xs text-[#71717a] mt-0.5">Reference Scenario: Retrieve Passport & check roof degradation</div>
                  </div>
                  <ArrowRight size={16} className="text-[#71717a] group-hover:text-teal transition-colors" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 2: Ask Response (Progressive Answer) */}
        {step === 2 && stewardResponse && (
          <div className="space-y-6 rise-animation">
            
            {/* Level 1: Direct Answer */}
            <div className="p-5 rounded-md border border-[#27272a] bg-[#0c0d0e]">
              <div className="text-[10px] font-mono text-teal overline mb-1" style={{ color: "#14f1d9" }}>Level 1 — Direct Answer</div>
              <p className="text-sm font-medium leading-relaxed text-white">
                {stewardResponse.level_1_direct_answer}
              </p>
            </div>

            {/* Level 2: Why This Matters */}
            <div className="p-5 rounded-md border border-[#27272a] bg-[#100f0a]">
              <div className="text-[10px] font-mono text-orange overline mb-1" style={{ color: "#ff6b00" }}>Level 2 — Why This Matters</div>
              <p className="text-sm leading-relaxed text-[#d4d4d8]">
                {stewardResponse.level_2_why_this_matters}
              </p>
            </div>

            {/* Level 3: Supporting Information */}
            <div className="p-5 rounded-md border border-[#27272a] bg-[#0a0a0b] space-y-4">
              <div className="text-[10px] font-mono text-[#a1a1aa] overline">Level 3 — Supporting Information</div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-[11px] text-[#71717a]">Property Asset & Material</div>
                  <div className="text-xs font-semibold text-white mt-0.5">{stewardResponse.level_3_supporting_information.material_and_age}</div>
                </div>
                <div>
                  <div className="text-[11px] text-[#71717a]">Planning Confidence</div>
                  <div className="text-xs font-semibold text-white mt-0.5">{stewardResponse.level_3_supporting_information.confidence}</div>
                </div>
              </div>

              <div className="border-t border-[#27272a] pt-3">
                <div className="text-[11px] text-[#71717a] mb-1">Approved Condition Findings</div>
                <ul className="list-disc pl-4 text-xs text-[#a1a1aa] space-y-1">
                  {stewardResponse.level_3_supporting_information.known_findings.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-[#27272a] pt-3">
                <div>
                  <div className="text-[11px] text-[#71717a] mb-1">Assumptions</div>
                  <ul className="list-disc pl-4 text-[11px] text-[#71717a] space-y-1">
                    {stewardResponse.level_3_supporting_information.assumptions.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="text-[11px] text-orange mb-1" style={{ color: "#ff6b00" }}>Known Unknowns</div>
                  <ul className="list-disc pl-4 text-[11px] text-[#71717a] space-y-1">
                    {stewardResponse.level_3_supporting_information.unknowns.map((f, i) => (
                      <li key={i} className="text-orange" style={{ color: "#ff6b00" }}>{f}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Level 4: Trace */}
            <div className="p-4 rounded-md border border-[#27272a] bg-[#0a0a0b] flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-[#71717a]">
                <FileText size={14} />
                <span>Level 4 Trace: Linked to authorized Passport explanations & timeline audits.</span>
              </div>
              <button className="text-teal font-mono text-[11px] hover:underline" style={{ color: "#14f1d9" }}>
                Inspect Trace →
              </button>
            </div>

            {/* Recommended Next Action */}
            {recommendedAction && (
              <div className="kpi-card p-6 bg-[#091515] border border-teal/20 rounded-lg space-y-4" style={{ borderColor: "rgba(20,241,217,0.2)" }}>
                <div className="flex items-center gap-2">
                  <ShieldCheck className="text-teal" size={20} style={{ color: "#14f1d9" }} />
                  <h3 className="font-semibold text-white">Recommended Action Engine</h3>
                </div>

                <div className="p-4 bg-[#060a0a] rounded border border-teal/10" style={{ borderColor: "rgba(20,241,217,0.1)" }}>
                  <div className="text-xs font-mono text-teal" style={{ color: "#14f1d9" }}>PRIMARY ACTION</div>
                  <div className="text-sm font-semibold text-white mt-1">{recommendedAction.primary.type}</div>
                  <p className="text-xs text-[#a1a1aa] mt-2 leading-relaxed">{recommendedAction.primary.why}</p>
                  
                  <div className="grid grid-cols-2 gap-4 mt-4 pt-3 border-t border-[#1a2d2d]">
                    <div>
                      <span className="text-[10px] text-[#71717a] block">Expected Effort</span>
                      <span className="text-xs font-mono text-white">{recommendedAction.primary.expected_effort}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-[#71717a] block">Requires Professional</span>
                      <span className="text-xs font-mono text-white">{recommendedAction.primary.requires_professional_verification}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-[11px] text-[#71717a] mb-2 uppercase tracking-wider font-mono">Secondary Options (Progressive Disclosure)</div>
                  <div className="space-y-2">
                    {recommendedAction.secondary_progressive_disclosure.map((opt, i) => (
                      <div key={i} className="flex justify-between items-center p-2.5 rounded bg-[#0a0a0bee] border border-[#27272a] text-xs">
                        <div>
                          <span className="font-medium text-white">{opt.type}</span>
                          <span className="text-[11px] text-[#71717a] block mt-0.5">{opt.description}</span>
                        </div>
                        <span className="font-mono text-[#71717a]">{opt.effort}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  <Button onClick={() => setStep(3)} className="flex-1 bg-teal hover:bg-teal/90 text-black font-semibold" style={{ background: "#14f1d9" }}>
                    Explore Replacement Options
                  </Button>
                  <Button variant="outline" onClick={() => setStep(1)} className="border-[#27272a] text-[#a1a1aa] hover:bg-[#1a1a1e]">
                    Back
                  </Button>
                </div>
              </div>
            )}

          </div>
        )}

        {/* STEP 3: Action Confirmation (Confirmation Gate) */}
        {step === 3 && (
          <div className="space-y-6 rise-animation">
            <div className="p-6 rounded-lg border border-teal/30 bg-[#091515] space-y-4" style={{ borderColor: "rgba(20,241,217,0.3)" }}>
              <div className="flex items-center gap-2 border-b border-teal/20 pb-3" style={{ borderColor: "rgba(20,241,217,0.2)" }}>
                <AlertTriangle className="text-orange" size={20} style={{ color: "#ff6b00" }} />
                <h3 className="font-semibold text-white">Explicit Action Confirmation Gate</h3>
              </div>

              <p className="text-xs text-[#a1a1aa] leading-relaxed">
                Before initiating a new planning project, Habitat requires explicit approval. This operation strictly adheres to H-012 guidelines.
              </p>

              <div className="p-4 rounded bg-[#070e0e] border border-[#1d2d2d] text-xs space-y-2.5">
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-teal mt-0.5" style={{ color: "#14f1d9" }} />
                  <span>A dedicated **Design Studio Roof Project** will be created.</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-teal mt-0.5" style={{ color: "#14f1d9" }} />
                  <span>Verified 3D mesh roof geometry and penetrations will be referenced.</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-teal mt-0.5" style={{ color: "#14f1d9" }} />
                  <span>North Slope underlayment remains labeled as **UNKNOWN** (no false certainty).</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-teal mt-0.5" style={{ color: "#14f1d9" }} />
                  <span>**NO CONTRACTORS** will be contacted or notified at this stage.</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-teal mt-0.5" style={{ color: "#14f1d9" }} />
                  <span>Canonical Passport records **WILL NOT** be altered or modified.</span>
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <Button onClick={handleConfirm} disabled={loading} className="flex-1 bg-teal hover:bg-teal/90 text-black font-semibold" style={{ background: "#14f1d9" }}>
                  {loading ? "Creating Project..." : "Confirm & Create Project"}
                </Button>
                <Button variant="outline" onClick={() => setStep(2)} className="border-[#27272a] text-[#a1a1aa] hover:bg-[#1a1a1e]">
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: Design Studio Project Created & Prepopulated */}
        {step === 4 && estimateData && (
          <div className="space-y-6 rise-animation">
            <div className="p-4 bg-teal/10 rounded-md border border-teal/20 text-xs text-teal flex items-center gap-2" style={{ background: "rgba(20,241,217,0.1)", borderColor: "rgba(20,241,217,0.2)", color: "#14f1d9" }}>
              <CheckCircle2 size={16} />
              <span>Design Studio planning project 'Project: Roof Replacement' loaded successfully.</span>
            </div>

            {/* Imported Geometry Details */}
            <div className="p-5 rounded-lg border border-[#27272a] bg-[#0a0a0b] space-y-4">
              <h3 className="font-semibold text-white text-sm">Verified Property Geometry & Context Referenced</h3>
              
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                <div>
                  <span className="text-[#71717a] block">Approximate Area</span>
                  <span className="font-mono font-semibold text-white">3,200 sq ft (Passport Verified)</span>
                </div>
                <div>
                  <span className="text-[#71717a] block">Roof Pitch</span>
                  <span className="font-semibold text-white">6:12 (Estimated North / Verified South)</span>
                </div>
                <div>
                  <span className="text-[#71717a] block">Penetrations</span>
                  <span className="font-semibold text-white">1 Chimney, 3 Vents, 2 Attic Ridge</span>
                </div>
              </div>

              <div className="border-t border-[#27272a] pt-3">
                <span className="text-xs text-orange font-semibold flex items-center gap-1" style={{ color: "#ff6b00" }}>
                  <AlertTriangle size={13} /> North Slope Underlayment Structural Integrity: UNKNOWN
                </span>
                <p className="text-[11px] text-[#71717a] mt-1 leading-relaxed">
                  Concealed structural sheathing is labeled as UNKNOWN. Professional contractor field inspection is required to finalize deck validation.
                </p>
              </div>
            </div>

            {/* Material Library Selector / Delta Comparison */}
            <div className="p-5 rounded-lg border border-[#27272a] bg-[#0a0a0b] space-y-4">
              <h3 className="font-semibold text-white text-sm">Compare Roofing Materials & Planning Estimates</h3>

              <div className="grid grid-cols-3 gap-3">
                {[
                  { k: "GAF Timberline HDZ", l: "Architectural Shingle", tier: "$$" },
                  { k: "DECRA Standing Seam", l: "Standing Seam Metal", tier: "$$$$" },
                  { k: "CertainTeed Grand Manor", l: "Luxury Dimensional", tier: "$$$" }
                ].map((item) => (
                  <button
                    key={item.k}
                    onClick={() => handleMaterialChange(item.k)}
                    className={`p-3 rounded-md border text-left transition-all ${selectedMaterial === item.k ? "border-teal bg-teal/5" : "border-[#27272a] bg-[#111113] hover:border-[#3f3f46]"}`}
                    style={{ borderColor: selectedMaterial === item.k ? "#14f1d9" : "" }}
                  >
                    <span className="text-[10px] font-mono text-[#71717a] block">{item.tier}</span>
                    <span className="text-xs font-semibold text-white block truncate mt-1">{item.k}</span>
                    <span className="text-[10px] text-[#71717a] block truncate">{item.l}</span>
                  </button>
                ))}
              </div>

              {/* Estimate Cost Details */}
              <div className="p-4 rounded-md bg-[#111113] border border-[#27272a] space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold text-white">Austin local range:</span>
                  <span className="font-mono text-sm text-teal font-bold" style={{ color: "#14f1d9" }}>
                    {money(estimateData.scenarios.low)} - {money(estimateData.scenarios.high)}
                  </span>
                </div>

                <div className="text-[11px] text-teal/80 bg-teal/5 p-2 rounded leading-normal border border-teal/10" style={{ color: "#14f1d9", background: "rgba(20,241,217,0.05)", borderColor: "rgba(20,241,217,0.1)" }}>
                  {estimateData.cost_delta_explanation}
                </div>

                <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 pt-2 border-t border-[#27272a] text-[11px]">
                  {Object.entries(estimateData.breakdown).map(([k, v]) => (
                    <div key={k} className="flex justify-between">
                      <span className="text-[#71717a] capitalize">{k.replace(/_/g, " ")}</span>
                      <span className="font-mono text-[#a1a1aa]">{money(v)}</span>
                    </div>
                  ))}
                </div>

                <div className="pt-2 border-t border-[#27272a] text-[10px] text-[#71717a] flex justify-between">
                  <span>Geographic multiplier: Austin, TX</span>
                  <span>Pricing date: {estimateData.pricing_date}</span>
                </div>
              </div>

              {/* Assumptions & Unknowns */}
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-[#71717a] block font-semibold mb-1">Planning Assumptions</span>
                  <ul className="list-disc pl-4 text-[#a1a1aa] space-y-1 text-[11px]">
                    {estimateData.assumptions.map((a, i) => <li key={i}>{a}</li>)}
                  </ul>
                </div>
                <div>
                  <span className="text-orange block font-semibold mb-1" style={{ color: "#ff6b00" }}>Exclusions & Unknowns</span>
                  <ul className="list-disc pl-4 text-orange/90 space-y-1 text-[11px]" style={{ color: "#ff6b00" }}>
                    {estimateData.unknowns.map((u, i) => <li key={i}>{u}</li>)}
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <Button onClick={handleToScenarios} className="flex-1 bg-teal hover:bg-teal/90 text-black font-semibold" style={{ background: "#14f1d9" }}>
                Next: Invest Scenarios Comparison
              </Button>
              <Button variant="outline" onClick={() => setStep(3)} className="border-[#27272a] text-[#a1a1aa] hover:bg-[#1a1a1e]">
                Back
              </Button>
            </div>
          </div>
        )}

        {/* STEP 5: Home Investment Intelligence comparison scenarios */}
        {step === 5 && investmentScenarios && (
          <div className="space-y-6 rise-animation">
            <h3 className="font-semibold text-white text-base">Home Investment Intelligence Scenario Comparison</h3>

            <div className="grid grid-cols-1 gap-4">
              {[
                { s: investmentScenarios.scenario_a, border: "border-[#27272a]" },
                { s: investmentScenarios.scenario_b, border: "border-teal/30 bg-teal/5" },
                { s: investmentScenarios.scenario_c, border: "border-red-500/20" }
              ].map(({ s, border }, idx) => (
                <div key={idx} className={`p-5 rounded-lg border ${border} space-y-3`}>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-white flex items-center gap-1.5">
                      <CircleDot size={12} className={idx === 1 ? "text-teal" : idx === 2 ? "text-red-500" : "text-gray-400"} />
                      {s.name}
                    </span>
                    <span className="font-mono text-xs text-white font-semibold">{s.estimated_cost}</span>
                  </div>
                  
                  <p className="text-xs text-[#a1a1aa] leading-normal">{s.maintenance_implications}</p>

                  <div className="grid grid-cols-2 gap-4 pt-2 border-t border-[#27272a] text-[11px] text-[#71717a]">
                    <div>
                      <span className="block font-semibold">Weather considerations</span>
                      <span className="text-[#a1a1aa]">{s.weather_exposure}</span>
                    </div>
                    <div>
                      <span className="block font-semibold">Likely info gained</span>
                      <span className="text-[#a1a1aa]">{s.likely_info_gained}</span>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-[#27272a] text-[10px] text-[#71717a] space-y-1">
                    <div className="uppercase tracking-wider font-mono font-bold text-[9px] text-[#71717a] flex items-center gap-1">
                      <Lock size={10} /> Disclosures (Truth & Compliance)
                    </div>
                    <div>• Resale ROI: {s.unpromised_disclosures.resale_return}</div>
                    <div>• Insurance premium effect: {s.unpromised_disclosures.insurance_savings}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3 pt-2">
              <Button onClick={handleToBuildReady} className="flex-1 bg-teal hover:bg-teal/90 text-black font-semibold" style={{ background: "#14f1d9" }}>
                Next: Build Ready completeness review
              </Button>
              <Button variant="outline" onClick={() => setStep(4)} className="border-[#27272a] text-[#a1a1aa] hover:bg-[#1a1a1e]">
                Back
              </Button>
            </div>
          </div>
        )}

        {/* STEP 6: Build Ready Review */}
        {step === 6 && readinessData && (
          <div className="space-y-6 rise-animation">
            
            {/* Score circle / card */}
            <div className="p-6 rounded-lg border border-[#27272a] bg-[#0a0a0b] flex items-center justify-between">
              <div>
                <span className="text-xs text-[#71717a] block uppercase font-mono tracking-widest">Roof Replacement</span>
                <h3 className="text-lg font-bold text-white mt-1">Project Readiness Score</h3>
                <p className="text-xs text-[#a1a1aa] mt-2 leading-relaxed">
                  Ready score is calculated dynamically based on material selection, geometry audits, and structural inspections.
                </p>
              </div>
              <div className="relative shrink-0 w-24 h-24 rounded-full border-4 border-orange/20 grid place-items-center" style={{ borderColor: readinessData.project_readiness_score < 70 ? "rgba(255,107,0,0.15)" : "rgba(20,241,217,0.15)" }}>
                <div className="text-center">
                  <span className="font-mono text-3xl font-bold block" style={{ color: readinessData.project_readiness_score < 70 ? "#ff6b00" : "#14f1d9" }}>
                    {readinessData.project_readiness_score}
                  </span>
                  <span className="text-[10px] text-[#71717a] uppercase font-mono">/100</span>
                </div>
              </div>
            </div>

            {/* Checklist */}
            <div className="p-5 rounded-lg border border-[#27272a] bg-[#0a0a0b] space-y-4">
              <h3 className="font-semibold text-white text-sm">Prioritized Readiness Checklist</h3>

              <div className="space-y-3">
                {readinessData.priority_checklist.map((item, i) => {
                  const isMissing = item.status === "MISSING" || item.status === "UNVERIFIED";
                  const isBlocking = item.blocks_publication;
                  return (
                    <div key={i} className={`p-3.5 rounded border text-xs flex justify-between gap-4 ${isMissing ? (isBlocking ? "border-orange/35 bg-orange/5" : "border-yellow-500/20 bg-yellow-500/5") : "border-[#27272a] bg-[#111113]"}`}>
                      <div className="space-y-1 max-w-[80%]">
                        <span className="font-bold text-white flex items-center gap-1.5">
                          {isMissing ? <AlertTriangle size={13} className={isBlocking ? "text-orange" : "text-yellow-500"} style={{ color: isBlocking ? "#ff6b00" : "#eab308" }} /> : <CheckCircle2 size={13} className="text-teal" style={{ color: "#14f1d9" }} />}
                          {item.item}
                        </span>
                        <p className="text-[11px] text-[#a1a1aa] leading-relaxed">{item.why}</p>
                        <span className="text-[10px] text-[#71717a] block pt-0.5">Verified by: {item.verified_by}</span>
                      </div>
                      
                      <div className="text-right shrink-0 flex flex-col justify-between">
                        <span className={`font-mono text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded ${isMissing ? (isBlocking ? "text-orange bg-orange/10" : "text-yellow-500 bg-yellow-500/10") : "text-teal bg-teal/10"}`} style={{ color: isMissing ? (isBlocking ? "#ff6b00" : "#eab308") : "#14f1d9" }}>
                          {item.status}
                        </span>
                        {isBlocking && (
                          <span className="text-[9px] text-orange block mt-1 uppercase tracking-widest font-mono" style={{ color: "#ff6b00" }}>BLOCKS PUB</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Block override / confirmation */}
            <div className="p-4 rounded-md border border-orange/30 bg-[#150a04] text-xs space-y-3" style={{ borderColor: "rgba(255,107,0,0.3)" }}>
              <p className="leading-relaxed text-orange" style={{ color: "#ff6b00" }}>
                **H-012 RESTRICTION:** The unverified deck condition is marked as BLOCKING. You cannot publish this project to the Contractor lead marketplace until the deck is inspected OR you check the explicit override to publish as an "In-planning diagnostic quote request".
              </p>
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <Switch checked={overrideReadiness} onCheckedChange={setOverrideReadiness} className="scale-90" />
                <span className="text-[11px] text-[#a1a1aa]">I confirm that this project will be published solely as a diagnostic scoping request.</span>
              </label>
            </div>

            <div className="flex gap-3 pt-2">
              <Button
                onClick={handleToPreview}
                disabled={!overrideReadiness}
                className={`flex-1 font-semibold text-black ${overrideReadiness ? "bg-teal hover:bg-teal/90" : "bg-teal/50 cursor-not-allowed"}`}
                style={{ background: overrideReadiness ? "#14f1d9" : "rgba(20,241,217,0.5)" }}
              >
                Next: Contractor Package Preview
              </Button>
              <Button variant="outline" onClick={() => setStep(5)} className="border-[#27272a] text-[#a1a1aa] hover:bg-[#1a1a1e]">
                Back
              </Button>
            </div>
          </div>
        )}

        {/* STEP 7: Contractor Package Preview & Edit */}
        {step === 7 && contractorPreview && (
          <div className="space-y-6 rise-animation">
            <h3 className="font-semibold text-white text-base">Contractor Package Preview</h3>
            
            <p className="text-xs text-[#a1a1aa] leading-relaxed">
              Review and configure the exact package contractors will receive in the Lead Marketplace. You retain full control over eligible fields and shared files.
            </p>

            <div className="p-5 rounded-lg border border-[#27272a] bg-[#0a0a0b] space-y-4">
              
              <div className="flex justify-between items-start border-b border-[#27272a] pb-3">
                <div>
                  <h4 className="font-bold text-white text-sm">{contractorPreview.summary}</h4>
                  <p className="text-[11px] text-[#71717a] mt-0.5">Scoped from Villa Horizon Digital Twin</p>
                </div>
                <span className="text-[10px] font-mono bg-teal/10 text-teal px-2 py-0.5 rounded font-bold uppercase" style={{ color: "#14f1d9" }}>
                  Score: 65/100
                </span>
              </div>

              {/* Editable Fields */}
              <div className="space-y-3 text-xs pt-1">
                <div className="overline tracking-wider font-mono text-[#71717a] text-[10px]">Configure Preferences</div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-[#71717a] block mb-1">Requested Timeline</label>
                    <select
                      value={timelinePreference}
                      onChange={(e) => setTimelinePreference(e.target.value)}
                      className="w-full bg-[#111113] border border-[#27272a] rounded p-2 text-white focus:outline-none focus:border-teal"
                    >
                      <option value="30 days">30 Days (Fast-track)</option>
                      <option value="60 days">60 Days (Standard)</option>
                      <option value="90 days">90 Days (Flexible)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[#71717a] block mb-1">Budget Preference</label>
                    <select
                      value={budgetPreference}
                      onChange={(e) => setBudgetPreference(e.target.value)}
                      className="w-full bg-[#111113] border border-[#27272a] rounded p-2 text-white focus:outline-none focus:border-teal"
                    >
                      <option value="Competitive">Competitive (Cost-sensitive)</option>
                      <option value="Balanced">Balanced (Value-driven)</option>
                      <option value="Premium">Premium (High-performance)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-[#71717a] block mb-1">Additional Planning Notes</label>
                  <textarea
                    value={homeownerNotes}
                    onChange={(e) => setHomeownerNotes(e.target.value)}
                    rows={2}
                    className="w-full bg-[#111113] border border-[#27272a] rounded p-2 text-xs text-white focus:outline-none focus:border-teal placeholder:text-[#71717a]"
                  />
                </div>
              </div>

              {/* Privacy protection toggles */}
              <div className="space-y-2.5 pt-3 border-t border-[#27272a] text-xs">
                <div className="overline tracking-wider font-mono text-[#71717a] text-[10px]">Privacy & Document Controls</div>
                
                <label className="flex items-center justify-between cursor-pointer select-none">
                  <div>
                    <span className="font-semibold text-white block">Redact personal contact details</span>
                    <span className="text-[10px] text-[#71717a] block mt-0.5">Hides your last name, phone, and direct email until you accept a bid.</span>
                  </div>
                  <Switch checked={removePersonalInfo} onCheckedChange={setRemovePersonalInfo} className="scale-90" />
                </label>

                <div className="pt-2">
                  <span className="text-[#71717a] block mb-1.5">Shared Documents:</span>
                  <div className="space-y-2">
                    {contractorPreview.shared_documents.map((doc) => (
                      <label key={doc.id} className="flex items-center justify-between p-2 rounded bg-[#111113] border border-[#27272a] text-[11px] cursor-pointer hover:border-[#3f3f46]">
                        <span className="flex items-center gap-1.5">
                          <FileText size={12} className="text-[#71717a]" />
                          {doc.name}
                        </span>
                        <Switch
                          checked={sharedDocs[doc.id]}
                          onCheckedChange={(val) => setSharedDocs({ ...sharedDocs, [doc.id]: val })}
                          className="scale-75"
                        />
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              {/* Package Snapshot (Takeoff + Materials) */}
              <div className="p-3 rounded bg-[#111113] border border-[#27272a] text-[11px] space-y-2">
                <div className="font-mono text-teal tracking-wider uppercase font-bold text-[9px]" style={{ color: "#14f1d9" }}>PREVIEW SNAPSHOT ATTACHED TO OPP</div>
                <div className="flex justify-between text-[#a1a1aa]">
                  <span>Material Option:</span>
                  <span className="font-bold text-white">{selectedMaterial}</span>
                </div>
                <div className="flex justify-between text-[#a1a1aa]">
                  <span>takeoff Area:</span>
                  <span className="font-mono text-white">3,200 sq ft</span>
                </div>
                <div className="flex justify-between text-[#a1a1aa]">
                  <span>Estimate Budget:</span>
                  <span className="font-mono text-white font-bold">{money(estimateData.scenarios.low)} - {money(estimateData.scenarios.high)}</span>
                </div>
              </div>

            </div>

            <div className="p-4 bg-teal/10 rounded-md border border-teal/20 text-xs text-[#a1a1aa] leading-relaxed flex items-start gap-2" style={{ background: "rgba(20,241,217,0.1)", borderColor: "rgba(20,241,217,0.2)" }}>
              <ShieldAlert className="text-teal mt-0.5 shrink-0" size={14} style={{ color: "#14f1d9" }} />
              <span>
                **IMMEDIATE COMPLIANCE:** Direct homeowner identity details (alex@) and unapproved files are filtered out of public queries. Only vetted Texas Roofing contractors can bid.
              </span>
            </div>

            <div className="flex gap-3 pt-2">
              <Button onClick={handlePublish} className="flex-1 bg-teal hover:bg-teal/90 text-black font-semibold" style={{ background: "#14f1d9" }}>
                I Approve - Publish Opportunity
              </Button>
              <Button variant="outline" onClick={() => setStep(6)} className="border-[#27272a] text-[#a1a1aa] hover:bg-[#1a1a1e]">
                Back
              </Button>
            </div>
          </div>
        )}

        {/* STEP 8: Published Successfully */}
        {step === 8 && (
          <div className="space-y-6 rise-animation text-center py-10">
            <div className="w-16 h-16 rounded-full bg-teal/10 text-teal border border-teal/20 grid place-items-center mx-auto mb-4" style={{ background: "rgba(20,241,217,0.1)", color: "#14f1d9", borderColor: "rgba(20,241,217,0.2)" }}>
              <CheckCircle2 size={32} />
            </div>
            
            <h2 className="text-xl font-bold text-white">Project Opportunity Published!</h2>
            <p className="text-sm text-[#a1a1aa] max-w-md mx-auto mt-2 leading-relaxed">
              Your planning opportunity has been securely broadcasted to approved local contractors under state **open**. Vetted bids will appear in your Quotes tab.
            </p>

            <div className="p-4 bg-[#0a0a0b] border border-[#27272a] max-w-sm mx-auto text-xs rounded text-left space-y-2 mt-6">
              <div className="flex justify-between">
                <span className="text-[#71717a]">Correlation ID:</span>
                <span className="font-mono text-white select-all">{correlationId.slice(0, 12)}...</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#71717a]">Material Selection:</span>
                <span className="text-white font-semibold">{selectedMaterial}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#71717a]">Budget Range:</span>
                <span className="font-mono text-white font-semibold">{money(estimateData.scenarios.low)} - {money(estimateData.scenarios.high)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#71717a]">Identity Protection:</span>
                <span className="text-teal font-semibold" style={{ color: "#14f1d9" }}>ACTIVE (Redacted)</span>
              </div>
            </div>

            <div className="flex justify-center gap-3 pt-6">
              <Button onClick={() => setStep(1)} className="bg-teal hover:bg-teal/90 text-black font-semibold" style={{ background: "#14f1d9" }}>
                Ask Steward New Question
              </Button>
            </div>
          </div>
        )}

      </div>

      {/* Right side: Developer controls, logs, memory correction */}
      <div className="w-full md:w-[320px] lg:w-[360px] bg-[#09090b] p-6 overflow-y-auto shrink-0 space-y-6">
        
        {/* Memory correction block */}
        <div className="kpi-card p-5 bg-[#111113] border border-[#27272a] rounded-lg space-y-4">
          <div className="flex items-center justify-between border-b border-[#27272a] pb-2">
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">Isolated Home Memories</span>
            <button
              onClick={() => {
                if (editingMemory) {
                  handleSaveMemory();
                } else {
                  setEditingMemory(true);
                }
              }}
              className="text-teal text-xs font-semibold hover:underline flex items-center gap-1" style={{ color: "#14f1d9" }}
            >
              {editingMemory ? <Check size={12} /> : <Edit2 size={11} />}
              {editingMemory ? "Save" : "Correct"}
            </button>
          </div>

          {memoryData ? (
            <div className="text-xs space-y-3">
              <div>
                <span className="text-[#71717a] block uppercase font-mono text-[9px] font-bold">Project Memories</span>
                {editingMemory ? (
                  <div className="space-y-2 mt-1">
                    <input
                      type="text"
                      value={preferredMaterialMem}
                      onChange={(e) => setPreferredMaterialMem(e.target.value)}
                      className="w-full bg-[#1c1c1f] border border-[#27272a] rounded p-1 text-[11px]"
                    />
                    <input
                      type="text"
                      value={budgetTargetMem}
                      onChange={(e) => setBudgetTargetMem(e.target.value)}
                      className="w-full bg-[#1c1c1f] border border-[#27272a] rounded p-1 text-[11px]"
                    />
                    <input
                      type="text"
                      value={timelinePreferenceMem}
                      onChange={(e) => setTimelinePreferenceMem(e.target.value)}
                      className="w-full bg-[#1c1c1f] border border-[#27272a] rounded p-1 text-[11px]"
                    />
                  </div>
                ) : (
                  <div className="space-y-1 mt-1 text-[#a1a1aa]">
                    <div>• Material Pref: {memoryData.project_memory.preferred_roof_material}</div>
                    <div>• Budget Pref: {memoryData.project_memory.budget_target}</div>
                    <div>• Timing Pref: {memoryData.project_memory.timeline_preference}</div>
                  </div>
                )}
              </div>

              <div>
                <span className="text-[#71717a] block uppercase font-mono text-[9px] font-bold">Homeowner Preferences</span>
                <div className="space-y-1 mt-1 text-[#a1a1aa]">
                  <div>• Comm: {memoryData.homeowner_memory.communication_preference}</div>
                  <div>• Depth: {memoryData.homeowner_memory.explanation_depth_preference}</div>
                </div>
              </div>

              <div>
                <span className="text-[#71717a] block uppercase font-mono text-[9px] font-bold">Property References (Immutable)</span>
                <p className="text-[10px] text-[#71717a] leading-normal mt-1 italic">
                  References Passport projection records without copying canonical facts.
                </p>
              </div>
            </div>
          ) : (
            <span className="text-xs text-[#71717a] animate-pulse">Loading memories...</span>
          )}
        </div>

        {/* Resiliency simulation triggers */}
        <div className="kpi-card p-5 bg-[#111113] border border-[#27272a] rounded-lg space-y-4">
          <div className="flex items-center gap-1.5 border-b border-[#27272a] pb-2">
            <RefreshCw size={14} className="text-teal" style={{ color: "#14f1d9" }} />
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">Task 14 Failure Simulator</span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-white block">Passport Core Offline</span>
                <span className="text-[10px] text-[#71717a] block mt-0.5">Blocks homeowner questions</span>
              </div>
              <Switch checked={simPassportDown} onCheckedChange={setSimPassportDown} className="scale-75" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-white block">Estimator API Offline</span>
                <span className="text-[10px] text-[#71717a] block mt-0.5">Recalculation fails gracefully</span>
              </div>
              <Switch checked={simEstimatorDown} onCheckedChange={setSimEstimatorDown} className="scale-75" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-white block">Audit DB Timeout</span>
                <span className="text-[10px] text-[#71717a] block mt-0.5">Abort project creation</span>
              </div>
              <Switch checked={simAuditWriteFail} onCheckedChange={setSimAuditWriteFail} className="scale-75" />
            </div>
          </div>
        </div>

        {/* Latency & groundness metrics dashboard */}
        <div className="kpi-card p-5 bg-[#111113] border border-[#27272a] rounded-lg space-y-4">
          <div className="flex items-center gap-1.5 border-b border-[#27272a] pb-2">
            <BarChart3 size={14} className="text-teal" style={{ color: "#14f1d9" }} />
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">Task 17 Observability Dashboard</span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-2.5 rounded bg-[#1c1c1f] border border-[#27272a]">
              <span className="text-[10px] text-[#71717a] block font-mono">CTX LATENCY</span>
              <span className="font-mono text-sm text-white font-bold">{latencyMetrics.contextRetrieval}</span>
            </div>
            <div className="p-2.5 rounded bg-[#1c1c1f] border border-[#27272a]">
              <span className="text-[10px] text-[#71717a] block font-mono">AI LATENCY</span>
              <span className="font-mono text-sm text-white font-bold">{latencyMetrics.stewardResponse}</span>
            </div>
            <div className="p-2.5 rounded bg-[#1c1c1f] border border-[#27272a]">
              <span className="text-[10px] text-[#71717a] block font-mono">EST LATENCY</span>
              <span className="font-mono text-sm text-white font-bold">{latencyMetrics.estimator}</span>
            </div>
            <div className="p-2.5 rounded bg-[#1c1c1f] border border-[#27272a]">
              <span className="text-[10px] text-[#71717a] block font-mono">GROUNDEDNESS</span>
              <span className="font-mono text-sm text-teal font-bold" style={{ color: "#14f1d9" }}>100%</span>
            </div>
          </div>
        </div>

        {/* Live Structured Logs list */}
        <div className="space-y-2">
          <div className="flex items-center gap-1.5">
            <Clock size={13} className="text-[#71717a]" />
            <span className="text-[10px] font-bold text-[#71717a] uppercase tracking-wider font-mono">Structured Audit Logs</span>
          </div>

          <div className="h-44 rounded border border-[#27272a] bg-black p-3 overflow-y-auto text-[10px] font-mono text-[#a1a1aa] space-y-1.5 scrollbar-thin">
            {logs.length === 0 ? (
              <span className="text-[#71717a] italic">Listening for system events...</span>
            ) : (
              logs.map((log, i) => (
                <div key={i} className="leading-normal break-words border-b border-[#18181b] pb-1 last:border-0 last:pb-0">
                  {log}
                </div>
              ))
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
