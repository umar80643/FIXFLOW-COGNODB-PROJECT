import axios from 'axios';
import type { DeviceDetail, DeviceSummary, GraphResponse, Insight } from './types';
import { demoDevices, demoDetail, demoInsights } from './data';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL,
  timeout: 6000,
});

async function safeGet<T>(path: string, fallback: T): Promise<T> {
  try {
    const { data } = await client.get<T>(path);
    return data;
  } catch {
    return fallback;
  }
}

export async function loadHealth(): Promise<{ status: string; database_connected: boolean; message: string }> {
  return safeGet('/api/health', { status: 'degraded', database_connected: false, message: 'Demo mode active' });
}

export async function searchDevices(query: string, category?: string): Promise<DeviceSummary[]> {
  const params = new URLSearchParams();
  if (query) params.set('search', query);
  if (category) params.set('category', category);
  const suffix = params.toString() ? `?${params.toString()}` : '';
  const data = await safeGet<{ query: string; devices: DeviceSummary[] }>(`/api/devices${suffix}`, { query, devices: demoDevices });
  return data.devices;
}

export async function loadDevice(slug: string): Promise<DeviceDetail> {
  return safeGet(`/api/devices/${slug}`, demoDetail);
}

export async function loadInsights(): Promise<Insight[]> {
  const data = await safeGet<{ insights: Insight[] }>('/api/insights', { insights: demoInsights });
  return data.insights;
}

export async function loadGraph(slug: string): Promise<GraphResponse> {
  const fallback: GraphResponse = {
    nodes: [
      { id: demoDetail.device.id, label: demoDetail.device.name, kind: 'Device', x: 120, y: 220, group: 'device', meta: {} },
      { id: demoDetail.symptoms[0].id, label: demoDetail.symptoms[0].name, kind: 'Symptom', x: 320, y: 110, group: 'symptom', meta: {} },
      { id: demoDetail.guides[0].id, label: demoDetail.guides[0].title, kind: 'RepairGuide', x: 520, y: 180, group: 'guide', meta: {} },
      { id: demoDetail.parts[0].id, label: demoDetail.parts[0].name, kind: 'Part', x: 620, y: 390, group: 'part', meta: {} },
      { id: demoDetail.tools[0].id, label: demoDetail.tools[0].name, kind: 'Tool', x: 620, y: 40, group: 'tool', meta: {} },
      { id: demoDetail.venues[0].id, label: demoDetail.venues[0].name, kind: 'Venue', x: 880, y: 240, group: 'venue', meta: {} },
    ],
    edges: [
      { id: 'edge-1', source: demoDetail.device.id, target: demoDetail.symptoms[0].id, kind: 'HAS_SYMPTOM' },
      { id: 'edge-2', source: demoDetail.symptoms[0].id, target: demoDetail.guides[0].id, kind: 'RESOLVED_BY' },
    ],
  };
  return safeGet(`/api/graph/${slug}`, fallback);
}

export async function loadRelatedDevices(slug: string): Promise<DeviceSummary[]> {
  const data = await safeGet<{ query: string; devices: DeviceSummary[] }>(`/api/related/${slug}`, { query: slug, devices: demoDevices.slice(1, 4) });
  return data.devices;
}

export async function loadRecommendation(deviceSlug: string, symptomSlug: string): Promise<{
  device: DeviceSummary;
  symptom: DeviceDetail['symptoms'][number];
  guides: DeviceDetail['guides'];
  parts: DeviceDetail['parts'];
  tools: DeviceDetail['tools'];
  venues: DeviceDetail['venues'];
  graph: GraphResponse;
}> {
  const fallbackGraph = await loadGraph(deviceSlug);
  return safeGet(`/api/recommendations/${deviceSlug}/${symptomSlug}`, {
    device: demoDetail.device,
    symptom: demoDetail.symptoms[0],
    guides: demoDetail.guides,
    parts: demoDetail.parts,
    tools: demoDetail.tools,
    venues: demoDetail.venues,
    graph: fallbackGraph,
  });
}
