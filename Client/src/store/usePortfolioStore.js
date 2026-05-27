import { create } from 'zustand'

const usePortfolioStore = create((set) => ({
  sites: [],
  kpis: null,
  mapData: null,
  summary: null,
  loading: false,
  error: null,

  setSites: (sites) => set({ sites }),
  setKPIs: (kpis) => set({ kpis }),
  setMapData: (mapData) => set({ mapData }),
  setSummary: (summary) => set({ summary }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))

export default usePortfolioStore
