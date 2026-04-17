import type { AppData } from '../app/types';
import { demoData } from './demoData';

const STORAGE_KEY = 'focus-flow-v1';

export const localStore = {
  load(): AppData {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(demoData));
      return demoData;
    }

    try {
      return JSON.parse(raw) as AppData;
    } catch {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(demoData));
      return demoData;
    }
  },
  save(data: AppData) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  },
};
