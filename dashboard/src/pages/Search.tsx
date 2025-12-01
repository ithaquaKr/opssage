import { Search as SearchIcon } from "lucide-react";
import { useState } from "react";
import { documentsApi } from "../api/client";
import Badge from "../components/Badge";
import Button from "../components/Button";
import { Card, CardHeader } from "../components/Card";
import type { SearchResult } from "../types";

export default function Search() {
    const [query, setQuery] = useState("");
    const [collection, setCollection] = useState<"documents" | "playbooks" | "incidents">("documents");
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setSearched(true);
        try {
            const response = await documentsApi.search(query, collection, 10);
            setResults(response.data.results);
        } catch (error) {
            console.error("Search failed:", error);
            setResults([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Knowledge Search</h1>
                <p className="mt-2 text-gray-600">Search the knowledge base using semantic similarity</p>
            </div>

            <div className="space-y-6">
                {/* Search Form */}
                <Card>
                    <form onSubmit={handleSearch} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Search Query</label>
                            <div className="mt-1 flex gap-2">
                                <input
                                    type="text"
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    placeholder="e.g., how to troubleshoot high CPU usage"
                                    className="block w-full rounded-lg border border-gray-300 px-4 py-3 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                                />
                                <Button type="submit" loading={loading}>
                                    <SearchIcon className="mr-2 h-4 w-4" />
                                    Search
                                </Button>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">Collection</label>
                            <div className="mt-2 flex gap-2">
                                {(["documents", "playbooks", "incidents"] as const).map((col) => (
                                    <button
                                        key={col}
                                        type="button"
                                        onClick={() => setCollection(col)}
                                        className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                                            collection === col
                                                ? "bg-primary-100 text-primary-700"
                                                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                                        }`}
                                    >
                                        {col.charAt(0).toUpperCase() + col.slice(1)}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </form>
                </Card>

                {/* Search Results */}
                {searched && (
                    <Card>
                        <CardHeader
                            title="Search Results"
                            description={
                                loading
                                    ? "Searching..."
                                    : `Found ${results.length} result${results.length !== 1 ? "s" : ""}`
                            }
                        />

                        {loading ? (
                            <div className="py-12 text-center text-gray-500">Searching knowledge base...</div>
                        ) : results.length === 0 ? (
                            <div className="py-12 text-center text-gray-500">
                                No results found. Try a different query or collection.
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {results.map((result, index) => (
                                    <div
                                        key={result.id}
                                        className="rounded-lg border border-gray-200 p-4 transition-colors hover:bg-gray-50"
                                    >
                                        <div className="mb-2 flex items-start justify-between">
                                            <div className="flex items-center gap-2">
                                                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary-100 text-xs font-medium text-primary-700">
                                                    {index + 1}
                                                </span>
                                                <h3 className="font-medium text-gray-900">
                                                    {result.metadata.filename || "Document"}
                                                </h3>
                                            </div>
                                            <div className="flex gap-2">
                                                {result.metadata.category && (
                                                    <Badge variant="info">{result.metadata.category}</Badge>
                                                )}
                                                <Badge variant="success">
                                                    {(result.relevance * 100).toFixed(0)}% match
                                                </Badge>
                                            </div>
                                        </div>

                                        <p className="text-sm leading-relaxed text-gray-700">{result.text}</p>

                                        {result.metadata.doc_type && (
                                            <p className="mt-2 text-xs text-gray-500">
                                                Type: {result.metadata.doc_type}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </Card>
                )}

                {/* Search Tips */}
                {!searched && (
                    <Card>
                        <CardHeader title="Search Tips" />
                        <div className="space-y-3 text-sm text-gray-700">
                            <p>
                                <strong>Semantic Search:</strong> The search uses AI embeddings to find contextually
                                relevant documents, not just keyword matches.
                            </p>
                            <p>
                                <strong>Natural Language:</strong> You can use natural language queries like "How do
                                I fix database connection issues?"
                            </p>
                            <p>
                                <strong>Collections:</strong> Search different collections for specific types of
                                content:
                            </p>
                            <ul className="ml-6 list-disc space-y-1">
                                <li>
                                    <strong>Documents:</strong> General technical documentation and guides
                                </li>
                                <li>
                                    <strong>Playbooks:</strong> Incident response procedures and runbooks
                                </li>
                                <li>
                                    <strong>Incidents:</strong> Historical incident reports and post-mortems
                                </li>
                            </ul>
                        </div>
                    </Card>
                )}
            </div>
        </div>
    );
}
