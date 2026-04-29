import { useEffect, useMemo, useState } from "react";
import type { ChangeEvent } from "react";

type ParkingArea = {
    id: number;
    name: string;
    address: string;
    latitude: number;
    longitude: number;
    total_slots: number;
    available_slots: number;
    unavailable_slots: number;
};

type SlotStatus = "available" | "occupied" | "maintenance";

type Slot = {
    id: number;
    area_id: number;
    name: string;
    status: SlotStatus;
};

type AreaResponse = {
    area: ParkingArea;
    slots: Slot[];
};

type MLPrediction = {
    area_id: number;
    area_name: string;
    prediction: string;
    confidence: number;
    occupancy_rate: string;
    available_slots: number;
    total_slots: number;
    model: string;
};

type MLSlotResult = {
    slot_index: number;
    status: "available" | "occupied";
    polygon: number[][];
};

type MLImageResult = {
    model_name: string;
    total_slots_analyzed: number;
    available_slots: number;
    occupied_slots: number;
    cars_detected: number;
    slot_results: MLSlotResult[];
    annotated_image: string;
};

type MLImageDetectResponse = {
    area: ParkingArea;
    db_slots: Slot[];
    ml_result: MLImageResult;
    sync: {
        applied: boolean;
        synced_slots: number;
        remaining_slots_marked_maintenance?: number;
    };
};

const API_URL = "/api";
const statusCycle: SlotStatus[] = ["available", "occupied", "maintenance"];

export default function TestingPage() {
    const [areas, setAreas] = useState<ParkingArea[]>([]);
    const [areaId, setAreaId] = useState(1);
    const [area, setArea] = useState<ParkingArea | null>(null);
    const [slots, setSlots] = useState<Slot[]>([]);
    const [availableSlots, setAvailableSlots] = useState(2);
    const [prediction, setPrediction] = useState<MLPrediction | null>(null);
    const [mlImageResult, setMLImageResult] = useState<MLImageResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState("");
    const [applyMLToBackend, setApplyMLToBackend] = useState(true);

    useEffect(() => {
        void fetchAreas();
    }, []);

    useEffect(() => {
        if (areas.length > 0) {
            void fetchAreaDetails(areaId);
        }
    }, [areaId, areas.length]);

    const availableMLSlots = useMemo(
        () => mlImageResult?.slot_results.filter((slot) => slot.status === "available").length ?? 0,
        [mlImageResult],
    );

    async function fetchAreas() {
        try {
            const response = await fetch(`${API_URL}/parking/areas`);
            const data: ParkingArea[] = await response.json();
            setAreas(data);

            const gym7 = data.find((item) => item.name === "GYM 7" || item.name === "GYM-7");
            if (gym7) {
                setAreaId(gym7.id);
            } else if (data[0]) {
                setAreaId(data[0].id);
            }
        } catch (error) {
            setMessage(`Failed to load parking areas: ${String(error)}`);
        }
    }

    async function fetchAreaDetails(selectedAreaId: number) {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/parking/areas/${selectedAreaId}`);
            const data: AreaResponse | { error: string } = await response.json();

            if (!response.ok || "error" in data) {
                throw new Error("error" in data ? data.error : "Failed to load area");
            }

            setArea(data.area);
            setSlots(data.slots);
            setAvailableSlots(data.area.available_slots);
            setPrediction(null);
            setMessage("");
        } catch (error) {
            setMessage(`Failed to load area details: ${String(error)}`);
        } finally {
            setLoading(false);
        }
    }

    async function handleUpdateSlots() {
        if (!area) return;

        try {
            setLoading(true);
            setMessage("");

            const response = await fetch(`${API_URL}/parking/areas/${areaId}/update`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ available_slots: availableSlots }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error ?? "Failed to update available slots");
            }

            setMessage(data.message);
            await fetchAreaDetails(areaId);
        } catch (error) {
            setMessage(`Update failed: ${String(error)}`);
        } finally {
            setLoading(false);
        }
    }

    function getNextStatus(currentStatus: SlotStatus): SlotStatus {
        const currentIndex = statusCycle.indexOf(currentStatus);
        return statusCycle[(currentIndex + 1) % statusCycle.length];
    }

    async function handleUpdateSlotStatus(slot: Slot) {
        try {
            setLoading(true);
            const nextStatus = getNextStatus(slot.status);

            const response = await fetch(
                `${API_URL}/parking/areas/${areaId}/slots/${slot.id}`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ status: nextStatus }),
                },
            );

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error ?? "Failed to update slot");
            }

            setMessage(data.message);
            await fetchAreaDetails(areaId);
        } catch (error) {
            setMessage(`Slot update failed: ${String(error)}`);
        } finally {
            setLoading(false);
        }
    }

    async function handleMLPredict() {
        try {
            setLoading(true);
            setMessage("");

            const response = await fetch(`${API_URL}/parking/areas/${areaId}/ml-predict`, {
                method: "POST",
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error ?? "Failed to run ML prediction");
            }

            setPrediction(data);
            setMessage("ML prediction completed");
        } catch (error) {
            setMessage(`ML failed: ${String(error)}`);
        } finally {
            setLoading(false);
        }
    }

    function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0] ?? null;
        setSelectedFile(file);
        setMLImageResult(null);

        if (!file) {
            setPreviewUrl("");
            return;
        }

        const objectUrl = URL.createObjectURL(file);
        setPreviewUrl(objectUrl);
    }

    async function handleUploadMLImage() {
        if (!selectedFile) {
            setMessage("Please choose an image file first");
            return;
        }

        try {
            setLoading(true);
            setMessage("");

            const formData = new FormData();
            formData.append("image", selectedFile);
            formData.append("apply_to_area", String(applyMLToBackend));

            const response = await fetch(`${API_URL}/parking/areas/${areaId}/ml-image-detect`, {
                method: "POST",
                body: formData,
            });

            const data = (await response.json()) as MLImageDetectResponse | { error: string };
            if (!response.ok || "error" in data) {
                throw new Error("error" in data ? data.error : "ML image detection failed");
            }

            setMLImageResult(data.ml_result);
            setArea(data.area);
            setSlots(data.db_slots);
            setAvailableSlots(data.area.available_slots);
            setPrediction(null);

            if (data.sync.applied) {
                setMessage(
                    `ML analyzed ${data.ml_result.total_slots_analyzed} slots and synced ${data.sync.synced_slots} slots to backend`,
                );
            } else {
                setMessage(
                    `ML analyzed ${data.ml_result.total_slots_analyzed} slots using ${data.ml_result.model_name}`,
                );
            }
        } catch (error) {
            setMessage(`ML image detection failed: ${String(error)}`);
        } finally {
            setLoading(false);
        }
    }

    function getPredictionTone(predictionValue: string) {
        switch (predictionValue) {
            case "very_available":
            case "available":
                return "bg-emerald-50 text-emerald-800 border-emerald-200";
            case "moderate":
                return "bg-amber-50 text-amber-800 border-amber-200";
            case "likely_full":
            case "very_full":
                return "bg-red-50 text-red-800 border-red-200";
            default:
                return "bg-slate-50 text-slate-800 border-slate-200";
        }
    }

    function getSlotTone(status: SlotStatus) {
        if (status === "available") {
            return "bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100";
        }
        if (status === "occupied") {
            return "bg-red-50 text-red-800 border-red-200 hover:bg-red-100";
        }
        return "bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100";
    }

    return (
        <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_#e0f2fe,_transparent_32%),linear-gradient(180deg,#f8fafc_0%,#eef2ff_100%)] px-4 py-8 md:px-8">
            <div className="mx-auto flex max-w-7xl flex-col gap-6">
                <section className="rounded-[32px] border border-white/70 bg-white/85 p-6 shadow-xl shadow-slate-200/60 backdrop-blur md:p-8">
                    <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                        <div>
                            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">
                                System Testing
                            </p>
                            <h1 className="mt-2 text-3xl font-black tracking-tight text-slate-900 md:text-4xl">
                                Parking Control Sandbox
                            </h1>
                            <p className="mt-3 max-w-2xl text-sm text-slate-600 md:text-base">
                                อัปโหลดรูปเข้า ML ในโฟลเดอร์ <code>ML</code> เพื่อให้ระบบวิเคราะห์สถานะช่องจอดและ sync เข้า backend ได้จากหน้าเดียว
                            </p>
                        </div>

                        <div className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-lg">
                            <div className="text-xs uppercase tracking-[0.2em] text-slate-300">
                                Testing Route
                            </div>
                            <div className="mt-1 font-mono text-sm">/test</div>
                        </div>
                    </div>
                </section>

                {message && (
                    <div className="rounded-2xl border border-slate-200 bg-white px-5 py-4 text-sm font-medium text-slate-700 shadow-sm">
                        {message}
                    </div>
                )}

                <section className="grid gap-6">
                    <div className="rounded-[28px] border border-white/70 bg-white/90 p-6 shadow-lg shadow-slate-200/50">
                        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                            <div>
                                <h2 className="text-xl font-bold text-slate-900">Select Parking Area</h2>
                                <p className="text-sm text-slate-500">
                                    เลือกพื้นที่จอดเพื่ออัปเดตสถานะหรือเรียก ML
                                </p>
                            </div>

                            <select
                                value={areaId}
                                onChange={(event) => setAreaId(Number(event.target.value))}
                                className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-800 outline-none ring-0 transition focus:border-sky-400"
                            >
                                {areas.map((parkingArea) => (
                                    <option key={parkingArea.id} value={parkingArea.id}>
                                        {parkingArea.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {loading && !area ? (
                            <div className="py-12 text-center text-sm text-slate-500">Loading area...</div>
                        ) : null}

                        {area ? (
                            <div className="mt-6 grid gap-4 md:grid-cols-3">
                                <div className="rounded-3xl bg-slate-950 p-5 text-white">
                                    <div className="text-xs uppercase tracking-[0.2em] text-slate-300">
                                        Area
                                    </div>
                                    <div className="mt-2 text-2xl font-black">{area.name}</div>
                                    <div className="mt-2 text-sm text-slate-300">{area.address}</div>
                                </div>

                                <div className="rounded-3xl border border-emerald-100 bg-emerald-50 p-5">
                                    <div className="text-xs uppercase tracking-[0.2em] text-emerald-700">
                                        Available
                                    </div>
                                    <div className="mt-2 text-4xl font-black text-emerald-700">
                                        {area.available_slots}
                                    </div>
                                </div>

                                <div className="rounded-3xl border border-red-100 bg-red-50 p-5">
                                    <div className="text-xs uppercase tracking-[0.2em] text-red-700">
                                        Occupied
                                    </div>
                                    <div className="mt-2 text-4xl font-black text-red-700">
                                        {area.unavailable_slots}
                                    </div>
                                </div>
                            </div>
                        ) : null}

                        {area ? (
                            <div className="mt-6 grid gap-4 md:grid-cols-[1fr_auto_auto]">
                                <input
                                    type="number"
                                    min={0}
                                    max={area.total_slots}
                                    value={availableSlots}
                                    onChange={(event) => setAvailableSlots(Number(event.target.value))}
                                    className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-medium text-slate-800 outline-none transition focus:border-sky-400"
                                />
                                <button
                                    onClick={handleUpdateSlots}
                                    disabled={loading}
                                    className="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    Set Available Slots
                                </button>
                                <button
                                    onClick={handleMLPredict}
                                    disabled={loading}
                                    className="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    Run ML Summary
                                </button>
                            </div>
                        ) : null}
                    </div>
                </section>

                <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
                    <div className="rounded-[28px] border border-white/70 bg-white/90 p-6 shadow-lg shadow-slate-200/50">
                        <div className="flex flex-col gap-2">
                            <h2 className="text-xl font-bold text-slate-900">Upload Image to ML</h2>
                            <p className="text-sm text-slate-500">
                                อัปโหลดภาพลานจอดให้โมเดลในโฟลเดอร์ <code>ML</code> วิเคราะห์สถานะรายช่อง
                            </p>
                        </div>

                        <div className="mt-5 grid gap-4 md:grid-cols-[1fr_auto]">
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 file:mr-4 file:rounded-xl file:border-0 file:bg-sky-100 file:px-3 file:py-2 file:font-semibold file:text-sky-700"
                            />
                            <button
                                onClick={handleUploadMLImage}
                                disabled={loading || !selectedFile}
                                className="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                Analyze Image
                            </button>
                        </div>


                        <div className="mt-6 grid gap-4 lg:grid-cols-2">
                            <div className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-50">
                                <div className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
                                    Uploaded Image
                                </div>
                                {previewUrl ? (
                                    <img src={previewUrl} alt="Uploaded preview" className="h-full w-full object-cover" />
                                ) : (
                                    <div className="flex min-h-[240px] items-center justify-center px-6 text-center text-sm text-slate-400">
                                        เลือกรูปก่อน แล้ว preview จะขึ้นตรงนี้
                                    </div>
                                )}
                            </div>

                            <div className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-50">
                                <div className="border-b border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700">
                                    ML Annotated Result
                                </div>
                                {mlImageResult ? (
                                    <img src={mlImageResult.annotated_image} alt="ML annotated result" className="h-full w-full object-cover" />
                                ) : (
                                    <div className="flex min-h-[240px] items-center justify-center px-6 text-center text-sm text-slate-400">
                                        หลังวิเคราะห์แล้วภาพที่ ML ตีกรอบและระบุ FULL/EMPTY จะขึ้นตรงนี้
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="rounded-[28px] border border-white/70 bg-white/90 p-6 shadow-lg shadow-slate-200/50">
                        <h2 className="text-xl font-bold text-slate-900">Image Detection Result</h2>
                        <p className="mt-1 text-sm text-slate-500">
                            สรุปผลจากการวิเคราะห์รูปภาพล่าสุด
                        </p>

                        {mlImageResult ? (
                            <>
                                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                                    <div className="rounded-3xl bg-emerald-50 p-5">
                                        <div className="text-xs uppercase tracking-[0.2em] text-emerald-700">
                                            Empty Detected
                                        </div>
                                        <div className="mt-2 text-4xl font-black text-emerald-700">
                                            {mlImageResult.available_slots}
                                        </div>
                                    </div>
                                    <div className="rounded-3xl bg-red-50 p-5">
                                        <div className="text-xs uppercase tracking-[0.2em] text-red-700">
                                            Full Detected
                                        </div>
                                        <div className="mt-2 text-4xl font-black text-red-700">
                                            {mlImageResult.occupied_slots}
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-4 rounded-3xl bg-slate-50 p-5 text-sm text-slate-700">
                                    <div>Model: <span className="font-semibold">{mlImageResult.model_name}</span></div>
                                    <div className="mt-1">Cars detected: {mlImageResult.cars_detected}</div>
                                    <div className="mt-1">Slots analyzed: {mlImageResult.total_slots_analyzed}</div>
                                    <div className="mt-1">Available by ML: {availableMLSlots}</div>
                                </div>

                                <div className="mt-5 max-h-[360px] overflow-auto rounded-3xl border border-slate-200">
                                    <div className="grid grid-cols-2 border-b border-slate-200 bg-slate-50 px-4 py-3 text-xs font-bold uppercase tracking-[0.16em] text-slate-500">
                                        <span>ML Slot</span>
                                        <span>Status</span>
                                    </div>
                                    {mlImageResult.slot_results.map((slot) => (
                                        <div
                                            key={slot.slot_index}
                                            className="grid grid-cols-2 border-b border-slate-100 px-4 py-3 text-sm text-slate-700 last:border-b-0"
                                        >
                                            <span>Slot {slot.slot_index}</span>
                                            <span className={slot.status === "available" ? "font-semibold text-emerald-700" : "font-semibold text-red-700"}>
                                                {slot.status}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </>
                        ) : (
                            <div className="mt-5 rounded-3xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
                                ยังไม่มีผล image detection
                            </div>
                        )}
                    </div>
                </section>

                <section className="rounded-[28px] border border-white/70 bg-white/90 p-6 shadow-lg shadow-slate-200/50">
                    <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
                        <div>
                            <h2 className="text-xl font-bold text-slate-900">Backend Slot Status Grid</h2>
                            <p className="text-sm text-slate-500">
                                คลิกแต่ละช่องเพื่อทดสอบ API อัปเดตสถานะราย slot
                            </p>
                        </div>

                        <div className="flex flex-wrap gap-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                            <span className="flex items-center gap-2">
                                <span className="h-3 w-3 rounded-full bg-emerald-400" />
                                Available
                            </span>
                            <span className="flex items-center gap-2">
                                <span className="h-3 w-3 rounded-full bg-red-400" />
                                Occupied
                            </span>
                            <span className="flex items-center gap-2">
                                <span className="h-3 w-3 rounded-full bg-amber-400" />
                                Maintenance
                            </span>
                        </div>
                    </div>

                    <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8">
                        {slots.map((slot) => (
                            <button
                                key={slot.id}
                                onClick={() => handleUpdateSlotStatus(slot)}
                                disabled={loading}
                                className={`rounded-3xl border px-4 py-5 text-left transition ${getSlotTone(slot.status)} disabled:cursor-not-allowed disabled:opacity-60`}
                            >
                                <div className="text-xs font-semibold uppercase tracking-[0.16em]">
                                    {slot.name}
                                </div>
                                <div className="mt-3 text-lg font-black capitalize">{slot.status}</div>
                            </button>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
}