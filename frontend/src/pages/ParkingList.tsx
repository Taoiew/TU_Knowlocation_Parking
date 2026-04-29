import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";

// ============================================================
// Types
// ============================================================
type UserType = "all" | "staff" | "general" | "disabled";

type ParkingArea = {
    id: number;
    name: string;
    latitude: number | null;
    longitude: number | null;
    total_slots: number;
    available_slots: number;
    unavailable_slots: number;
    // From backend (optional – may not exist yet)
    allowed_types?: UserType[];
};

// ============================================================
// Fallback mapping (used when backend doesn't provide allowed_types yet)
// Key = parking area name, value = allowed user types
// ============================================================
const FALLBACK_ALLOWED_TYPES: Record<string, UserType[]> = {
    "GYM 7": ["staff", "general"],
    "Parking 1": ["staff", "general", "disabled"],
    "Parking 2": ["staff"],                          // บุคลากรเท่านั้น
    "Parking 3": ["staff", "general"],
    "Parking 4": ["staff", "disabled"],
};

function getAllowedTypes(area: ParkingArea): UserType[] {
    if (area.allowed_types && area.allowed_types.length > 0) {
        return area.allowed_types;
    }
    return FALLBACK_ALLOWED_TYPES[area.name] ?? ["staff", "general"];
}

// ============================================================
// Filter config
// ============================================================
type FilterOption = {
    value: UserType;
    label: string;
    emoji: string;
    color: string;        // active bg
    textColor: string;    // active text
    border: string;       // active border
    badgeBg: string;      // badge on card
    badgeText: string;
};

const FILTER_OPTIONS: FilterOption[] = [
    {
        value: "all",
        label: "ทั้งหมด",
        emoji: "🅿️",
        color: "bg-gray-800",
        textColor: "text-white",
        border: "border-gray-800",
        badgeBg: "bg-gray-100",
        badgeText: "text-gray-700",
    },
    {
        value: "staff",
        label: "บุคลากร",
        emoji: "🏛️",
        color: "bg-blue-600",
        textColor: "text-white",
        border: "border-blue-600",
        badgeBg: "bg-blue-100",
        badgeText: "text-blue-700",
    },
    {
        value: "general",
        label: "คนทั่วไป",
        emoji: "👤",
        color: "bg-emerald-600",
        textColor: "text-white",
        border: "border-emerald-600",
        badgeBg: "bg-emerald-100",
        badgeText: "text-emerald-700",
    },
    {
        value: "disabled",
        label: "ผู้พิการ",
        emoji: "♿",
        color: "bg-purple-600",
        textColor: "text-white",
        border: "border-purple-600",
        badgeBg: "bg-purple-100",
        badgeText: "text-purple-700",
    },
];

// ============================================================
// Custom marker icon
// ============================================================
const createCustomIcon = (available: number, dimmed: boolean) => {
    const isFull = available === 0;
    const colorClass = dimmed
        ? "bg-gray-300"
        : isFull
            ? "bg-red-500"
            : "bg-emerald-500";
    const pulse = dimmed ? "" : `<div class="absolute inset-0 rounded-full ${colorClass} opacity-20 animate-ping"></div>`;
    return L.divIcon({
        className: "custom-leaflet-icon",
        html: `<div class="relative w-10 h-10 transform transition-all ${dimmed ? "opacity-30 scale-75" : "hover:scale-110"}">
             ${pulse}
             <div class="absolute inset-1 rounded-full ${colorClass} border-2 border-white shadow-md flex items-center justify-center text-white font-bold text-xs">
               ${available}
             </div>
           </div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
    });
};

// ============================================================
// Component
// ============================================================
export default function ParkingList() {
    const [areas, setAreas] = useState<ParkingArea[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeFilter, setActiveFilter] = useState<UserType>("all");

    useEffect(() => {
        fetch("/api/parking")
            .then((res) => res.json())
            .then((data) => {
                setAreas(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Failed to fetch parking areas", err);
                setLoading(false);
            });
    }, []);

    // Center on TU Rangsit
    const centerLat = 14.0722;
    const centerLng = 100.605;

    // Filtered areas for the card list
    const filteredAreas =
        activeFilter === "all"
            ? areas
            : areas.filter((a) => getAllowedTypes(a).includes(activeFilter));

    const activeOption =
        FILTER_OPTIONS.find((f) => f.value === activeFilter) ?? FILTER_OPTIONS[0];

    return (
        <div className="flex flex-col h-full bg-[#f8fafc]">
            {/* ── Map ── */}
            <div className="w-full h-[40vh] md:h-[50vh] relative z-0 shrink-0">
                <MapContainer
                    center={[centerLat, centerLng]}
                    zoom={15}
                    scrollWheelZoom={true}
                    className="w-full h-full"
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                    />
                    {areas.map((area) => {
                        if (!area.latitude || !area.longitude) return null;
                        const allowed = getAllowedTypes(area);
                        const dimmed =
                            activeFilter !== "all" && !allowed.includes(activeFilter);
                        return (
                            <Marker
                                key={`marker-${area.id}`}
                                position={[area.latitude, area.longitude]}
                                icon={createCustomIcon(area.available_slots, dimmed)}
                            >
                                <Popup className="rounded-xl overflow-hidden shadow-sm">
                                    <div className="font-semibold text-gray-900">
                                        {area.name}
                                    </div>
                                    <div className="text-sm text-gray-600 mb-1">
                                        {area.available_slots} / {area.total_slots} available
                                    </div>
                                    {/* Allowed type badges inside popup */}
                                    <div className="flex flex-wrap gap-1 mb-2">
                                        {FILTER_OPTIONS.filter(
                                            (f) =>
                                                f.value !== "all" &&
                                                getAllowedTypes(area).includes(f.value)
                                        ).map((f) => (
                                            <span
                                                key={f.value}
                                                className={`px-2 py-0.5 rounded-full text-xs font-medium ${f.badgeBg} ${f.badgeText}`}
                                            >
                                                {f.label}
                                            </span>
                                        ))}
                                    </div>
                                    <Link
                                        to={`/parking/${area.id}`}
                                        className="mt-1 block w-full text-center bg-emerald-100 text-emerald-800 rounded-md py-1 text-xs font-medium"
                                    >
                                        View Info
                                    </Link>
                                </Popup>
                            </Marker>
                        );
                    })}
                </MapContainer>

                {/* Gradient fade at bottom of map */}
                <div className="absolute bottom-0 w-full h-8 bg-gradient-to-t from-[#f8fafc] to-transparent z-[400] pointer-events-none" />
            </div>

            {/* ── Content Section ── */}
            <div className="px-4 py-6 md:px-8 max-w-7xl mx-auto w-full pb-20">
                {/* Header */}
                <div className="mb-5">
                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">
                        Campus Parking
                    </h2>
                    <p className="text-sm text-gray-500 font-medium mt-0.5">
                        Real-time availability
                    </p>
                </div>

                {/* ── Filter Chips ── */}
                <div className="mb-6">
                    <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">
                        ฉันเป็น...
                    </p>
                    <div className="flex flex-wrap gap-2">
                        {FILTER_OPTIONS.map((opt) => {
                            const isActive = activeFilter === opt.value;
                            return (
                                <button
                                    key={opt.value}
                                    id={`filter-${opt.value}`}
                                    onClick={() => setActiveFilter(opt.value)}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold border-2 transition-all duration-200 cursor-pointer select-none
                                        ${isActive
                                            ? `${opt.color} ${opt.textColor} ${opt.border} shadow-md scale-105`
                                            : "bg-white text-gray-500 border-gray-200 hover:border-gray-300 hover:shadow-sm"
                                        }`}
                                >
                                    <span className="text-base leading-none">{opt.emoji}</span>
                                    {opt.label}
                                    {/* Count badge */}
                                    {opt.value !== "all" && (
                                        <span
                                            className={`ml-0.5 px-1.5 py-0.5 rounded-full text-xs font-bold leading-none ${isActive
                                                    ? "bg-white/25 text-white"
                                                    : "bg-gray-100 text-gray-500"
                                                }`}
                                        >
                                            {areas.filter((a) =>
                                                getAllowedTypes(a).includes(opt.value)
                                            ).length}
                                        </span>
                                    )}
                                </button>
                            );
                        })}
                    </div>

                    {/* Active filter hint */}
                    {activeFilter !== "all" && (
                        <p className="mt-3 text-sm text-gray-500">
                            <span className="font-semibold">{activeOption.emoji} {activeOption.label}</span>
                            {" "}สามารถใช้ที่จอดรถได้{" "}
                            <span className="font-bold text-gray-800">{filteredAreas.length}</span>
                            {" "}แห่ง จากทั้งหมด{" "}
                            <span className="font-bold text-gray-800">{areas.length}</span>{" "}แห่ง
                        </p>
                    )}
                </div>

                {/* ── Parking Cards ── */}
                {loading ? (
                    <div className="flex justify-center items-center py-12">
                        <div className="w-10 h-10 rounded-full border-4 border-gray-200 border-t-emerald-500 animate-spin" />
                    </div>
                ) : filteredAreas.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-16 text-center">
                        <span className="text-5xl mb-3">🔍</span>
                        <p className="text-gray-500 font-medium">
                            ไม่มีที่จอดรถสำหรับกลุ่มนี้
                        </p>
                        <button
                            onClick={() => setActiveFilter("all")}
                            className="mt-4 text-sm text-blue-600 underline"
                        >
                            ดูทั้งหมด
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {filteredAreas.map((area) => {
                            const allowed = getAllowedTypes(area);
                            return (
                                <Link
                                    key={area.id}
                                    to={`/parking/${area.id}`}
                                    className="bg-white rounded-[24px] border border-gray-100/80 shadow-sm hover:shadow-xl hover:border-emerald-100 transition-all duration-300 transform hover:-translate-y-1 block relative overflow-hidden group"
                                >
                                    {/* Accent line */}
                                    <div
                                        className={`absolute left-0 top-0 bottom-0 w-1 ${area.available_slots > 0 ? "bg-emerald-500" : "bg-red-400"}`}
                                    />

                                    <div className="p-5 pl-6">
                                        {/* Top row */}
                                        <div className="flex justify-between items-start mb-3">
                                            <h3 className="text-lg font-bold text-gray-900">
                                                {area.name}
                                            </h3>
                                            <span
                                                className={`px-3 py-1 text-xs font-bold rounded-full ${area.available_slots > 0
                                                        ? "bg-emerald-100 text-emerald-700"
                                                        : "bg-red-100 text-red-600"
                                                    }`}
                                            >
                                                {area.available_slots > 0 ? "OPEN" : "FULL"}
                                            </span>
                                        </div>

                                        {/* Allowed type badges */}
                                        <div className="flex flex-wrap gap-1 mb-3">
                                            {FILTER_OPTIONS.filter(
                                                (f) => f.value !== "all" && allowed.includes(f.value)
                                            ).map((f) => (
                                                <span
                                                    key={f.value}
                                                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${f.badgeBg} ${f.badgeText}`}
                                                >
                                                    {f.label}
                                                </span>
                                            ))}
                                        </div>

                                        {/* Slot count */}
                                        <div className="flex items-end gap-1 mb-2">
                                            <span
                                                className={`text-4xl font-extrabold ${area.available_slots > 0
                                                        ? "text-emerald-500"
                                                        : "text-red-500"
                                                    }`}
                                            >
                                                {area.available_slots}
                                            </span>
                                            <span className="text-base text-gray-400 mb-1 font-medium">
                                                / {area.total_slots} slots
                                            </span>
                                        </div>

                                        {/* Progress bar */}
                                        <div className="h-1.5 w-full bg-gray-100 rounded-full mt-4 overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all duration-700 ease-out ${area.available_slots > 0
                                                        ? "bg-gradient-to-r from-emerald-400 to-emerald-500"
                                                        : "bg-red-400"
                                                    }`}
                                                style={{
                                                    width: `${(area.available_slots / area.total_slots) * 100}%`,
                                                }}
                                            />
                                        </div>
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}