import { useEffect, useState } from "react";
import { fetchProtectedBlob } from "@/services/api";

export function useBlobUrl(apiPath: string | null): {
  blobUrl: string | null;
  loading: boolean;
  error: string | null;
} {
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!apiPath) {
      setBlobUrl(null);
      return;
    }

    let active = true;
    let objectUrl: string | null = null;
    setLoading(true);
    setError(null);

    fetchProtectedBlob(apiPath)
      .then((blob) => {
        if (!active) return;
        objectUrl = URL.createObjectURL(blob);
        setBlobUrl(objectUrl);
      })
      .catch((err) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load preview.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [apiPath]);

  return { blobUrl, loading, error };
}
