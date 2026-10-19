import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { getAccessToken, getOrgId } from "../api/client";

export function useRealtime() {
  const qc = useQueryClient();
  useEffect(() => {
    const token = getAccessToken();
    const org = getOrgId();
    if (!token || !org) return;
    const protocol = window.location.protocol === "https:" ? "ws" : "wss";
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws/org/?token=${token}&organization_id=${org}`);
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === "warning") qc.invalidateQueries({ queryKey: ["/alerts/"] });
      if (payload.type === "tracking") qc.invalidateQueries({ queryKey: ["/carriers/"] });
      if (payload.type === "purchase_order") qc.invalidateQueries({ queryKey: ["/purchase-orders/"] });
      if (payload.type === "notification") qc.invalidateQueries({ queryKey: ["/notifications/"] });
      qc.invalidateQueries({ queryKey: ["/dashboard/"] });
      qc.invalidateQueries({ queryKey: ["/activity/"] });
    };
    return () => socket.close();
  }, [qc]);
}
