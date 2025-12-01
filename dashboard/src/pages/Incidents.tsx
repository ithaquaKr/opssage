import { AlertCircle, CheckCircle, ChevronRight, Clock, XCircle } from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Link } from "react-router-dom";

interface Incident {
    incident_id: string;
    status: string;
    created_at: string;
    updated_at: string;
    alert_input: {
        alert_name: string;
        severity: string;
        message: string;
        labels: Record<string, string>;
    };
    diagnostic_report?: {
        root_cause: string;
        confidence_score: number;
    };
}

export default function Incidents() {
    const [incidents, setIncidents] = useState<Incident[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>("all");

    useEffect(() => {
        fetchIncidents();
        // Poll for updates every 10 seconds
        const interval = setInterval(fetchIncidents, 10000);
        return () => clearInterval(interval);
    }, [filter]);

    const fetchIncidents = async () => {
        try {
            const baseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
            const url =
                filter === "all" ? `${baseUrl}/api/v1/incidents` : `${baseUrl}/api/v1/incidents?status=${filter}`;

            const response = await fetch(url);
            if (!response.ok) throw new Error("Failed to fetch incidents");

            const data = await response.json();
            setIncidents(data);
        } catch (error) {
            console.error("Error fetching incidents:", error);
            toast.error("Failed to load incidents");
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "completed":
                return <CheckCircle className="h-5 w-5 text-green-500" />;
            case "failed":
                return <XCircle className="h-5 w-5 text-red-500" />;
            case "pending":
            case "running_aica":
            case "running_krea":
            case "running_rcara":
                return <Clock className="h-5 w-5 text-yellow-500 animate-spin" />;
            default:
                return <AlertCircle className="h-5 w-5 text-gray-500" />;
        }
    };

    const getStatusBadge = (status: string) => {
        const baseClass = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
        switch (status) {
            case "completed":
                return <span className={`${baseClass} bg-green-100 text-green-800`}>Completed</span>;
            case "failed":
                return <span className={`${baseClass} bg-red-100 text-red-800`}>Failed</span>;
            case "running_aica":
                return <span className={`${baseClass} bg-blue-100 text-blue-800`}>AICA Running</span>;
            case "running_krea":
                return <span className={`${baseClass} bg-purple-100 text-purple-800`}>KREA Running</span>;
            case "running_rcara":
                return <span className={`${baseClass} bg-indigo-100 text-indigo-800`}>RCARA Running</span>;
            case "pending":
                return <span className={`${baseClass} bg-yellow-100 text-yellow-800`}>Pending</span>;
            default:
                return <span className={`${baseClass} bg-gray-100 text-gray-800`}>{status}</span>;
        }
    };

    const getSeverityBadge = (severity: string) => {
        const baseClass = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
        switch (severity.toLowerCase()) {
            case "critical":
                return <span className={`${baseClass} bg-red-100 text-red-800`}>Critical</span>;
            case "warning":
                return <span className={`${baseClass} bg-yellow-100 text-yellow-800`}>Warning</span>;
            case "info":
                return <span className={`${baseClass} bg-blue-100 text-blue-800`}>Info</span>;
            default:
                return <span className={`${baseClass} bg-gray-100 text-gray-800`}>{severity}</span>;
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString();
    };

    const filteredIncidents = incidents;

    return (
        <div className="p-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Incidents</h1>
                <p className="mt-2 text-sm text-gray-600">View and manage all incident analysis reports</p>
            </div>

            {/* Filters */}
            <div className="mb-6 flex gap-2">
                <button
                    onClick={() => setFilter("all")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        filter === "all"
                            ? "bg-primary-600 text-white"
                            : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
                    }`}
                >
                    All
                </button>
                <button
                    onClick={() => setFilter("completed")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        filter === "completed"
                            ? "bg-primary-600 text-white"
                            : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
                    }`}
                >
                    Completed
                </button>
                <button
                    onClick={() => setFilter("failed")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        filter === "failed"
                            ? "bg-primary-600 text-white"
                            : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
                    }`}
                >
                    Failed
                </button>
            </div>

            {/* Incidents List */}
            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                </div>
            ) : filteredIncidents.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-12 text-center">
                    <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-lg font-medium text-gray-900">No incidents found</h3>
                    <p className="mt-1 text-sm text-gray-500">
                        {filter === "all" ? "No incidents have been created yet." : `No ${filter} incidents found.`}
                    </p>
                </div>
            ) : (
                <div className="bg-white shadow-md rounded-lg overflow-hidden">
                    <ul className="divide-y divide-gray-200">
                        {filteredIncidents.map((incident) => (
                            <li key={incident.incident_id}>
                                <Link
                                    to={`/incidents/${incident.incident_id}`}
                                    className="block hover:bg-gray-50 transition-colors"
                                >
                                    <div className="px-6 py-4">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-4 flex-1">
                                                {getStatusIcon(incident.status)}
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center gap-3 mb-1">
                                                        <p className="text-sm font-medium text-gray-900 truncate">
                                                            {incident.alert_input.alert_name}
                                                        </p>
                                                        {getSeverityBadge(incident.alert_input.severity)}
                                                        {getStatusBadge(incident.status)}
                                                    </div>
                                                    <p className="text-sm text-gray-600 truncate">
                                                        {incident.alert_input.message}
                                                    </p>
                                                    <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
                                                        <span>ID: {incident.incident_id.slice(0, 8)}...</span>
                                                        {incident.alert_input.labels.namespace && (
                                                            <span>
                                                                Namespace: {incident.alert_input.labels.namespace}
                                                            </span>
                                                        )}
                                                        {incident.alert_input.labels.service && (
                                                            <span>
                                                                Service: {incident.alert_input.labels.service}
                                                            </span>
                                                        )}
                                                        <span>{formatDate(incident.created_at)}</span>
                                                    </div>
                                                    {incident.diagnostic_report && (
                                                        <div className="mt-2">
                                                            <p className="text-xs text-gray-700 line-clamp-1">
                                                                <span className="font-medium">Root Cause:</span>{" "}
                                                                {incident.diagnostic_report.root_cause}
                                                            </p>
                                                            <p className="text-xs text-gray-500 mt-1">
                                                                Confidence:{" "}
                                                                {Math.round(
                                                                    incident.diagnostic_report.confidence_score *
                                                                        100,
                                                                )}
                                                                %
                                                            </p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                            <ChevronRight className="h-5 w-5 text-gray-400" />
                                        </div>
                                    </div>
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
