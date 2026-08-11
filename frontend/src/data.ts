import type { DeviceDetail, DeviceSummary, Insight } from './types';

export const demoDevices: DeviceSummary[] = [
  {
    id: 'device-iphone-15',
    slug: 'iphone-15',
    name: 'iPhone 15',
    brand: 'Apple',
    category: 'Phone',
    popularity: 98,
    difficulty: 'medium',
    confidence: 0.92,
  },
  {
    id: 'device-macbook-air-m2',
    slug: 'macbook-air-m2',
    name: 'MacBook Air M2',
    brand: 'Apple',
    category: 'Laptop',
    popularity: 95,
    difficulty: 'hard',
    confidence: 0.89,
  },
  {
    id: 'device-surface-laptop-5',
    slug: 'surface-laptop-5',
    name: 'Surface Laptop 5',
    brand: 'Microsoft',
    category: 'Laptop',
    popularity: 87,
    difficulty: 'medium',
    confidence: 0.86,
  },
  {
    id: 'device-nintendo-switch-oled',
    slug: 'nintendo-switch-oled',
    name: 'Nintendo Switch OLED',
    brand: 'Nintendo',
    category: 'Console',
    popularity: 84,
    difficulty: 'easy',
    confidence: 0.88,
  },
];

export const demoInsights: Insight[] = [
  { label: 'Devices', value: '4', description: 'Ready in demo mode' },
  { label: 'Symptoms', value: '8', description: 'Common repair issues' },
  { label: 'Guides', value: '6', description: 'Curated repair paths' },
];

export const demoDetail: DeviceDetail = {
  device: demoDevices[0],
  symptoms: [
    { id: 'symptom-battery-drops-fast', slug: 'battery-drops-fast', name: 'Battery drains quickly', severity: 'high', frequency: 82, likely_fix_time: '20-40 min' },
    { id: 'symptom-usb-c-loose', slug: 'usb-c-loose', name: 'USB-C port feels loose', severity: 'medium', frequency: 61, likely_fix_time: '30-50 min' },
  ],
  guides: [
    { id: 'guide-battery-replacement-iphone-15', slug: 'battery-replacement-iphone-15', title: 'Replace the iPhone 15 battery', summary: 'Inspect battery health, open safely, and replace the pack.', difficulty: 'medium', estimated_minutes: 35, score: 0.94 },
    { id: 'guide-usb-c-dock-cleaning', slug: 'usb-c-dock-cleaning', title: 'Clean and inspect the charging dock', summary: 'Check debris, retention, and flex cable wear before replacing parts.', difficulty: 'easy', estimated_minutes: 20, score: 0.81 },
  ],
  parts: [
    { id: 'part-iphone-15-battery', name: 'iPhone 15 battery pack', vendor: 'OEM compatible', price: 59, compatibility: 94 },
    { id: 'part-lightning-flex', name: 'USB-C flex assembly', vendor: 'Aftermarket', price: 24.5, compatibility: 89 },
  ],
  tools: [
    { id: 'tool-pentalobe-driver', name: 'Pentalobe driver', purpose: 'Open the outer case' },
    { id: 'tool-spudger', name: 'Nylon spudger', purpose: 'Disconnect delicate cables' },
  ],
  venues: [
    { id: 'venue-apple-service-center-1', name: 'Apple Service Center - Downtown', city: 'Austin', rating: 4.8, support_level: 'OEM' },
    { id: 'venue-repair-hub-austin', name: 'Repair Hub Austin', city: 'Austin', rating: 4.6, support_level: 'Independent' },
  ],
};
