/**
 * Hook to check upload limits based on user's plan.
 * Prevents unnecessary upload attempts by checking limits client-side first.
 */
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "../context/AuthContext";
import * as api from "../api";
import type { ScopeType } from "../types";

// Plan limits (must match backend PLAN_LIMITS in api_routes.py)
// Plan limits (must match backend PLAN_LIMITS in api_routes.py)
const PLAN_LIMITS = {
  free: { docs_per_scope: 3, token_limit: 10000, documents: 3 },
  pro: { docs_per_scope: 5, token_limit: 500000, documents: 30 },
  premium: { docs_per_scope: 10, token_limit: 2000000, documents: 999999 }, // 999999 = unlimited
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

  // Calculate limits (Scope & Global)
  const maxDocsScope =
    PLAN_LIMITS[plan as keyof typeof PLAN_LIMITS]?.docs_per_scope || 3;
  const currentDocsScope = usage?.current_count || 0;

  const maxDocsGlobal =
    usage?.max_total_docs ??
    PLAN_LIMITS[plan as keyof typeof PLAN_LIMITS]?.documents ??
    3;
  const currentDocsGlobal = usage?.user_doc_count ?? 0;

  // Use a pessimistic approach during loading: assume limit reached to prevent race conditions
  const isLoading = !usage && !!scopeId;
  const canUpload =
    !isLoading &&
    currentDocsScope < maxDocsScope &&
    currentDocsGlobal < maxDocsGlobal;

  /**
   * Helper to check how many files can be uploaded from a batch
   */
  function checkUploadability(fileCount: number) {
    if (isLoading) {
      return {
        allowed: 0,
        blocked: fileCount,
        isLimitReached: false,
        isLoading: true,
      };
    }

    // Calculate effective remaining (bounded by both scope and global limits)
    const remainingScope = Math.max(0, maxDocsScope - currentDocsScope);
    const remainingGlobal = Math.max(0, maxDocsGlobal - currentDocsGlobal);
    const remaining = Math.min(remainingScope, remainingGlobal);

    if (remaining === 0) {
      return {
        allowed: 0,
        blocked: fileCount,
        isLimitReached: true,
        isLoading: false,
      };
    }

    if (fileCount <= remaining) {
      return {
        allowed: fileCount,
        blocked: 0,
        isLimitReached: false,
        isLoading: false,
      };
    }

    // Partial allowance
    return {
      allowed: remaining,
      blocked: fileCount - remaining,
      isLimitReached: true, // Will reach limit after upload
      isLoading: false,
    };
  }

  return {
    canUpload,
    currentCount: currentDocsScope,
    maxDocs: maxDocsScope,
    remaining: Math.max(
      0,
      Math.min(
        maxDocsScope - currentDocsScope,
        maxDocsGlobal - currentDocsGlobal
      )
    ),
    isLoading,
    checkUploadability,
    // Debug info
    globalUsage: { current: currentDocsGlobal, max: maxDocsGlobal },
  };
}

export function useTokenLimit() {
  const { user } = useAuth();
  const plan = user?.plan || "free";

  const tokenLimit =
    PLAN_LIMITS[plan as keyof typeof PLAN_LIMITS]?.token_limit || 10000;
  const tokensUsed = user?.tokens_used || 0;

  return {
    canQuery: tokensUsed < tokenLimit,
    tokensUsed,
    tokenLimit,
    remaining: tokenLimit - tokensUsed,
    percentUsed: (tokensUsed / tokenLimit) * 100,
  };
}

export function useProjectLimit() {
  const { user } = useAuth();
  const plan = user?.plan || "free";

  // Fetch current project count
  const { data: projects } = useQuery({
    queryKey: ["projects-count"],
    queryFn: () => api.listProjects().then((p) => p.length),
    staleTime: 5000, // Cache for 5 seconds
  });

  const maxProjects = plan === "free" ? 1 : plan === "pro" ? 10 : 999999; // unlimited for premium
  const currentCount = projects || 0;

  return {
    canCreate: currentCount < maxProjects,
    currentCount,
    maxProjects,
    remaining: maxProjects - currentCount,
    isLoading: projects === undefined,
  };
}

export function useChatLimit() {
  const { user } = useAuth();
  const plan = user?.plan || "free";

  // Fetch current chat count
  const { data: chats } = useQuery({
    queryKey: ["chats-count"],
    queryFn: () => api.listChats().then((c) => c.length),
    staleTime: 5000, // Cache for 5 seconds
  });

  const maxChats = plan === "free" ? 3 : 999999; // unlimited for pro/premium
  const currentCount = chats || 0;

  return {
    canCreate: currentCount < maxChats,
    currentCount,
    maxChats,
    remaining: maxChats - currentCount,
    isLoading: chats === undefined,
  };
}
