/**
 * FireRadar frontend API base URL resolution.
 * Priority: window.__FIRERADAR_API_BASE__ > ?api= URL query > localStorage > default
 *
 * Canlı frontend (Netlify vb.) otomatik olarak production API'ye bağlanır; yerelde localhost kullanılır.
 * Production API URL'ini değiştirmek için aşağıdaki sabiti güncelleyin veya build öncesi script ile
 * window.__FIRERADAR_API_BASE__ enjekte edin.
 */
(function () {
  const PRODUCTION_API_BASE = "https://fireradaraihackathon.onrender.com";

  function looksLikeLocalHost(hostname) {
    if (!hostname) return true;
    const h = String(hostname).toLowerCase();
    return (
      h === "localhost" ||
      h === "127.0.0.1" ||
      h === "::1" ||
      h === "0.0.0.0" ||
      h.endsWith(".local") ||
      h.startsWith("192.168.") ||
      h.startsWith("10.") ||
      /^172\.(1[6-9]|2\d|3[0-1])\./.test(h)
    );
  }

  function isLocalFrontend() {
    try {
      const h = window.location.hostname;
      return looksLikeLocalHost(h);
    } catch {
      return true;
    }
  }

  const DEFAULT_API = isLocalFrontend() ? "http://localhost:8000" : PRODUCTION_API_BASE;

  function normalizeBase(url) {
    if (!url || !String(url).trim()) {
      return DEFAULT_API;
    }
    return String(url).trim().replace(/\/$/, "");
  }

  function readFromQuery() {
    try {
      return new URLSearchParams(window.location.search).get("api");
    } catch {
      return null;
    }
  }

  function readFromStorage() {
    try {
      return localStorage.getItem("fireradar_api_base");
    } catch {
      return null;
    }
  }

  window.FIRERADAR_CONFIG = {
    defaultApiBase: DEFAULT_API,
    productionApiBase: PRODUCTION_API_BASE,
    isLocalFrontend,
    getApiBaseUrl() {
      if (typeof window.__FIRERADAR_API_BASE__ === "string" && window.__FIRERADAR_API_BASE__.trim()) {
        return normalizeBase(window.__FIRERADAR_API_BASE__);
      }
      const fromQuery = readFromQuery();
      if (fromQuery) {
        return normalizeBase(fromQuery);
      }
      const fromStorage = readFromStorage();
      if (fromStorage) {
        return normalizeBase(fromStorage);
      }
      return DEFAULT_API;
    },
    setApiBaseUrl(url) {
      try {
        const trimmed = url && String(url).trim();
        if (!trimmed) {
          localStorage.removeItem("fireradar_api_base");
        } else {
          localStorage.setItem("fireradar_api_base", normalizeBase(trimmed));
        }
      } catch {
        /* ignore */
      }
    },
  };
})();
