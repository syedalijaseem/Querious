/**
 * Hook to check upload limits based on user's plan.
 * Prevents unnecessary upload attempts by checking limits client-side first.
 */
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import * as api from "../api";
import type { ScopeType } from "../types";

// Plan limits (must match backend PLAN_LIMITS in api_routes.py)
const PLAN_LIMITS = {
  free: { docs_per_scope: 1, token_limit: 5000 },
  pro: { docs_per_scope: 5, token_limit: 500000 },
  premium: { docs_per_scope: 10, token_limit: 2000000 },
} as const;

export function useUploadLimits(scopeType: ScopeType, scopeId: string | null) {
  const { user } = useAuth();
  const plan = user?.plan || "free";

  // Fetch current usage from backend
  const { data: usage } = useQuery({
    queryKey: ["upload-limits", scopeType, scopeId],
    queryFn: () =>
      scopeId ? api.getUploadLimits(scopeType, scopeId) : Promise.resolve(null),
    enabled: !!scopeId,
    staleTime: 10000, // Cache for 10 seconds
  });

  const maxDocs =
    PLAN_LIMITS[plan as keyof typeof PLAN_LIMITS]?.docs_per_scope || 1;
  const currentCount = usage?.current_count || 0;

  return {
    canUpload: currentCount < maxDocs,
    currentCount,
    maxDocs,
    remaining: maxDocs - currentCount,
    isLoading: !scopeId || !usage,
  };
}

export function useTokenLimit() {
  const { user } = useAuth();
  const plan = user?.plan || "free";

  const tokenLimit =
    PLAN_LIMITS[plan as keyof typeof PLAN_LIMITS]?.token_limit || 5000;
  const tokensUsed = user?.tokens_used || 0;

  return {
    canQuery: tokensUsed < tokenLimit,
    tokensUsed,
    tokenLimit,
    remaining: tokenLimit - tokensUsed,
    percentUsed: (tokensUsed / tokenLimit) * 100,
  };
}
