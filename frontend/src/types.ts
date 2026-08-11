export type DeviceSummary = {
  id: string;
  slug: string;
  name: string;
  brand?: string | null;
  category?: string | null;
  popularity: number;
  difficulty: string;
  confidence: number;
};

export type Symptom = {
  id: string;
  slug: string;
  name: string;
  severity: string;
  frequency: number;
  likely_fix_time: string;
};

export type Guide = {
  id: string;
  slug: string;
  title: string;
  summary: string;
  difficulty: string;
  estimated_minutes: number;
  score: number;
};

export type Part = {
  id: string;
  name: string;
  vendor: string;
  price: number;
  compatibility: number;
};

export type Tool = {
  id: string;
  name: string;
  purpose: string;
};

export type Venue = {
  id: string;
  name: string;
  city: string;
  rating: number;
  support_level: string;
};

export type DeviceDetail = {
  device: DeviceSummary;
  symptoms: Symptom[];
  guides: Guide[];
  parts: Part[];
  tools: Tool[];
  venues: Venue[];
};

export type Insight = {
  label: string;
  value: string;
  description: string;
};

export type GraphNode = {
  id: string;
  label: string;
  kind: string;
  x: number;
  y: number;
  group: string;
  meta: Record<string, unknown>;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  kind: string;
};

export type GraphResponse = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};
