import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
console.log("TNFD API Base URL in Client:", API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for large KML files
});

export const fetchActivities = async () => {
  const resp = await api.get('/activities');
  return resp.data;
};

export const uploadKml = async (formData) => {
  const resp = await api.post('/upload-kml', formData);
  return resp.data;
};

export const fetchSites = async () => {
  const resp = await api.get('/sites');
  return resp.data;
};

export const clearSites = async () => {
  const resp = await api.post('/sites/clear');
  return resp.data;
};

export const deleteSite = async (siteId) => {
  const resp = await api.delete(`/sites/${siteId}`);
  return resp.data;
};


export const fetchSiteDetail = async (siteId) => {
  const resp = await api.get(`/sites/${siteId}`);
  return resp.data;
};

export const fetchDashboardKPIs = async () => {
  const resp = await api.get('/dashboard/kpis');
  return resp.data;
};

export const fetchDashboardMap = async () => {
  const resp = await api.get('/dashboard/map');
  return resp.data;
};

export const fetchTopPrioritySites = async () => {
  const resp = await api.get('/dashboard/top-priority-sites');
  return resp.data;
};

export const fetchPortfolioOverview = async () => {
  const resp = await api.get('/portfolio/impact-dependency-overview');
  return resp.data;
};
